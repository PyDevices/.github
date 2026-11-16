# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Build every library's documentation as one site, with one Sphinx run.

Each library keeps its documentation in its own repository, as a ``docs/``
folder with its own ``conf.py`` that calls `omnipython_docs.configure`. The
site's ``gather.py`` clones each repository into ``<srcdir>/_repos`` and
copies its docs folder into the source tree as a section, ``<srcdir>/<slug>``.
The build reads each library's ``conf.py``, where it sits in the clone, to
learn what the section needs:

- the folders autodoc imports from, the packages that get API pages, the
  modules to mock and the autodoc defaults (what it passes to `configure`);
- ``master_doc``, ``exclude_patterns``, ``suppress_warnings`` and
  ``myst_heading_anchors``, when the file sets them;
- its ``setup(app)``, if it has one. That is called with a stand-in app whose
  ``srcdir`` is the section's folder, so a hook that writes pages beside its
  ``conf.py`` writes them into the section.

So a library's ``conf.py`` stays the one description of how its pages are
built: the library's own CI builds it alone, and the site builds it beside
every other library.

While Sphinx reads a page, the mocks and autodoc defaults are the ones that
page's library set, so two libraries that mock each other's modules both
build as they do alone.
"""

from __future__ import annotations

import logging
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from sphinx.util import logging as sphinx_logging
from sphinx.util.logging import is_suppressed_warning

from . import configure as _configure

__all__ = ["Library", "configure_site", "read_libraries"]

# Each section's setup(app), by slug. Kept out of the config, which Sphinx pickles.
_SETUPS = {}


@dataclass
class Library:
    """One section of the site: a library's ``docs`` folder."""

    slug: str  # the section's folder and address: /<slug>/
    title: str  # its name in the sidebar
    repo: str  # "PyDevices/<repo>"
    docs: str = "docs"  # the folder holding conf.py, relative to the repository root
    summary: str = ""
    # Read from the section's conf.py.
    master_doc: str = "index"
    exclude: list = field(default_factory=list)
    suppress: list = field(default_factory=list)
    mocks: list = field(default_factory=list)
    autodoc_options: dict = field(default_factory=dict)
    source_dirs: list = field(default_factory=list)
    api: dict = field(default_factory=dict)
    heading_anchors: int = 0
    root: str = "index"  # the section's first page on the site
    root_toc: str = ""  # toctrees moved onto that page from master_doc

    @property
    def owner(self) -> str:
        return self.repo.split("/", 1)[0]

    @property
    def repo_name(self) -> str:
        return self.repo.split("/", 1)[1]


def read_libraries(path) -> list:
    """The site's sections, in sidebar order, from ``libraries.toml``."""
    import tomllib

    with open(path, "rb") as f:
        data = tomllib.load(f)
    return [Library(**entry) for entry in data["library"]]


class _SectionApp:
    """The Sphinx app as a section's ``setup`` sees it: ``srcdir`` is the
    section's folder, and its event handlers get this stand-in back."""

    def __init__(self, app, srcdir: Path):
        self._app = app
        self.srcdir = srcdir

    def __getattr__(self, name):
        return getattr(self._app, name)

    def connect(self, event, callback, priority=500):
        def handler(_app, *args):
            return callback(self, *args)

        return self._app.connect(event, handler, priority)


def _read_section_conf(lib: Library, conf_path: Path) -> None:
    """Run a library's conf.py and keep what the site needs from it."""
    import omnipython_docs

    calls = []

    def recording_configure(name, conf_file, **kwargs):
        calls.append(kwargs)
        return _configure(name, conf_file, **kwargs)

    namespace = {"__file__": str(conf_path), "__name__": f"_omnipython_docs_conf_{lib.slug.replace('-', '_')}"}
    saved_offline = os.environ.get("OMNIPYTHON_DOCS_OFFLINE")
    omnipython_docs.configure = recording_configure
    # The section's own reference map is not used, so don't ask the network for it.
    os.environ["OMNIPYTHON_DOCS_OFFLINE"] = "1"
    try:
        code = compile(conf_path.read_text(encoding="utf-8"), str(conf_path), "exec")
        exec(code, namespace)  # noqa: S102 - the library's own conf.py, as Sphinx would run it
    finally:
        omnipython_docs.configure = _configure
        if saved_offline is None:
            os.environ.pop("OMNIPYTHON_DOCS_OFFLINE", None)
        else:
            os.environ["OMNIPYTHON_DOCS_OFFLINE"] = saved_offline
    if len(calls) != 1:
        raise RuntimeError(f"{conf_path} must call omnipython_docs.configure once; it called it {len(calls)} times")

    kwargs = calls[0]
    conf_dir = conf_path.resolve().parent
    lib.master_doc = namespace.get("master_doc", "index")
    lib.exclude = list(namespace.get("exclude_patterns", []))
    lib.suppress = list(namespace.get("suppress_warnings", []))
    lib.mocks = list(namespace.get("autodoc_mock_imports", []))
    lib.autodoc_options = dict(namespace.get("autodoc_default_options", {}))
    lib.heading_anchors = int(namespace.get("myst_heading_anchors", 0))
    lib.source_dirs = [str((conf_dir / d).resolve()) for d in kwargs.get("source_dirs", ())]
    if kwargs.get("api_packages"):
        lib.api = {
            "dir": f"{lib.slug}/reference",
            "packages": list(kwargs["api_packages"]),
            "source_dirs": lib.source_dirs,
            "skip": list(kwargs.get("api_skip", ())),
        }
    if lib.master_doc != "index":
        # A library whose master_doc is a navigation-only page ("contents")
        # starts at its index on the site; the navigation moves onto it.
        nav = (conf_dir / f"{lib.master_doc}.md").read_text(encoding="utf-8")
        tocs = re.findall(r"^(`{3,}\{toctree\}.*?^`{3,})[ \t]*$", nav, flags=re.MULTILINE | re.DOTALL)
        if not tocs:
            raise RuntimeError(f"{conf_dir / lib.master_doc}.md has no toctree")
        lib.root_toc = "\n\n".join(
            "\n".join(line for line in toc.splitlines() if line.strip() != "index") for toc in tocs
        )
        lib.exclude.append(f"{lib.master_doc}.md")
    if callable(namespace.get("setup")):
        _SETUPS[lib.slug] = namespace["setup"]


def _clone_conf(srcdir: Path, lib: Library) -> Path:
    # Paths in a conf.py ("../lib", the stubs beside docs/) are relative to the
    # repository, so it runs from the clone, not from the section's copy.
    return srcdir / "_repos" / lib.repo_name / lib.docs / "conf.py"


def configure_site(conf_file: str, libraries: list, *, title: str = "OmniPython") -> dict:
    """Return the Sphinx settings for the combined site.

    conf_file  the site's ``conf.py`` (pass ``__file__``)
    libraries  the sections, from `read_libraries`; each must already be in
               place at ``<srcdir>/<slug>`` (``gather.py`` puts them there)
    """
    srcdir = Path(conf_file).resolve().parent
    missing = [lib.slug for lib in libraries
               if not (srcdir / lib.slug / "conf.py").is_file() or not _clone_conf(srcdir, lib).is_file()]
    if missing:
        raise RuntimeError(
            f"no docs for {', '.join(missing)} under {srcdir}: run "
            f"`python {srcdir.name}/gather.py` first"
        )

    settings = _configure(
        title, conf_file, repo="PyDevices/.github", edit_path=srcdir.name,
        version_file=None, main=True,
    )
    for lib in libraries:
        _read_section_conf(lib, _clone_conf(srcdir, lib))
    for lib in libraries:
        for d in lib.source_dirs:
            if d not in sys.path:
                sys.path.insert(0, d)

    exclude = list(settings["exclude_patterns"]) + ["_repos", "_build", "requirements.txt"]
    for lib in libraries:
        exclude += [f"{lib.slug}/{p}" for p in lib.exclude]
        exclude.append(f"{lib.slug}/_build")
    settings["exclude_patterns"] = sorted(set(exclude))
    settings["myst_heading_anchors"] = max(
        [settings["myst_heading_anchors"]] + [lib.heading_anchors for lib in libraries]
    )
    # Every library is in this build, so only the Python manuals stay in the reference map.
    settings["intersphinx_mapping"] = {
        k: v for k, v in settings["intersphinx_mapping"].items() if k in ("python", "micropython")
    }
    settings["html_context"]["pd_site"] = True
    settings["html_theme_options"]["collapse_navigation"] = True
    settings["html_theme_options"]["navigation_depth"] = 4
    # Page titles only: a section's first page has headings of its own, and its
    # pages would otherwise hang under the last of them.
    settings["html_theme_options"]["titles_only"] = True
    settings["html_title"] = f"{title} documentation"
    settings["extensions"] += ["omnipython_docs.apigen", "omnipython_docs.site"]
    settings["api_sections"] = [lib.api for lib in libraries if lib.api]
    settings["pd_libraries"] = libraries
    return settings


def _library_for(app, docname: str):
    head = docname.split("/", 1)[0]
    for lib in app.config.pd_libraries:
        if lib.slug == head:
            return lib
    return None


def _library_cards(libraries) -> str:
    cards = ["::::{grid} 1 1 2 3", ":gutter: 3", ""]
    for lib in libraries:
        cards += [f":::{{grid-item-card}} {lib.title}", f":link: {lib.slug}/{lib.root}",
                  ":link-type: doc", lib.summary, ":::", ""]
    cards.append("::::")
    return "\n".join(cards)


def _library_toctree(libraries) -> str:
    lines = ["```{toctree}", ":hidden:", ":caption: Libraries", ""]
    lines += [f"{lib.title} <{lib.slug}/{lib.root}>" for lib in libraries]
    lines.append("```")
    return "\n".join(lines)


_LINK = re.compile(r"(\]\(|^\[[^\]\n]+\]:[ \t]*)(<?)([^)\s<>#]+)(#[^)\s>]*)?(>?)", re.MULTILINE)


_INCLUDE = re.compile(r"^([ \t]*(?:(?:`{3,}|:{3,})\{(?:include|literalinclude)\}|\.\. (?:include|literalinclude)::)[ \t]+)(\S+)", re.MULTILINE)


def _repo_links(app, lib: Library, docname: str, text: str) -> str:
    """Point paths that leave the docs folder back at the repository.

    A page may link a source file or a test beside its docs ("../src/x.c"),
    or include the changelog from the repository's root. Alone, Sphinx finds
    those files on disk; here the docs folder is a copy, so a link goes to
    the file on GitHub and an include reads it from the clone.
    """
    clone_docs = (Path(app.srcdir) / "_repos" / lib.repo_name / lib.docs).resolve()
    clone_root = (Path(app.srcdir) / "_repos" / lib.repo_name).resolve()
    page_dir = (clone_docs / docname.split("/", 1)[1]).parent

    def swap(m):
        target = m.group(3)
        if "://" in target or target.startswith(("mailto:", "/", "{")) or ":" in target.split("/", 1)[0]:
            return m.group(0)
        full = Path(os.path.normpath(page_dir / target))
        if not full.is_relative_to(clone_root) or not full.exists():
            return m.group(0)
        if full.is_relative_to(clone_docs):
            if not target.startswith(".."):
                return m.group(0)
            # "../../docs/x.md" from a file outside docs: the same page, from this one.
            target = os.path.relpath(full, page_dir)
            return f"{m.group(1)}{m.group(2)}{target}{m.group(4) or ''}{m.group(5)}"
        kind = "tree" if full.is_dir() else "blob"
        url = f"https://github.com/{lib.repo}/{kind}/main/{full.relative_to(clone_root).as_posix()}"
        return f"{m.group(1)}{m.group(2)}{url}{m.group(4) or ''}{m.group(5)}"

    def include(m):
        target = m.group(2)
        if target.startswith(("/", "<")):
            return m.group(0)
        full = Path(os.path.normpath(page_dir / target))
        if full.is_relative_to(clone_docs) or not full.is_relative_to(clone_root):
            return m.group(0)
        # A path starting with "/" is read from the top of the site's source folder.
        return f"{m.group(1)}/_repos/{lib.repo_name}/{full.relative_to(clone_root).as_posix()}"

    return _LINK.sub(swap, _INCLUDE.sub(include, text))


def _use_section_settings(app, docname, source):
    """Before a page is read, put its library's mocks and autodoc defaults in place.

    On the site's front page, write the library cards and the sidebar's
    library list where the page asks for them."""
    if docname == app.config.master_doc:
        source[0] = (source[0]
                     .replace("% pd-libraries: cards", _library_cards(app.config.pd_libraries))
                     .replace("% pd-libraries: toctree", _library_toctree(app.config.pd_libraries)))
    lib = _library_for(app, docname)
    if lib is not None and "/" in docname:
        source[0] = _repo_links(app, lib, docname, source[0])
        if lib.root_toc and docname == f"{lib.slug}/{lib.root}":
            source[0] += "\n\n" + lib.root_toc + "\n"
    mocks = lib.mocks if lib else []
    if app.config.autodoc_mock_imports != mocks:
        # A module another section imported for real is mocked again here,
        # as it is when this library builds alone.
        for name in list(sys.modules):
            if any(name == m or name.startswith(m + ".") for m in mocks):
                del sys.modules[name]
        app.config.autodoc_mock_imports = list(mocks)
    app.config.autodoc_default_options = dict(lib.autodoc_options if lib else app.config.pd_site_autodoc_options)


def _included_file(app, relative_path, parent_docname, content):
    """An included file's links are read as if they were in the page that includes it."""
    # MyST passes the including file's stem, not its docname; the page being read is the parent.
    docname = app.env.docname
    lib = _library_for(app, docname)
    if lib is not None and "/" in docname:
        content[0] = _repo_links(app, lib, docname, content[0])


def _section_groups(app, lib: Library) -> list:
    """The captions of a section's toctrees ("Guides", "Reference"), each
    with the first page under it."""
    cache = app.env.__dict__.setdefault("_pd_groups", {})
    if lib.slug not in cache:
        from sphinx import addnodes

        groups = []
        root = f"{lib.slug}/{lib.root}"
        for toc in app.env.get_doctree(root).findall(addnodes.toctree):
            pages = [doc for _title, doc in toc["entries"] if doc != root]
            if toc.get("caption") and pages:
                groups.append((toc["caption"], pages[0]))
        cache[lib.slug] = groups
    return cache[lib.slug]


def _sidebar_captions(app, pagename, templatename, context, doctree):
    """Show the section's own captions in the sidebar.

    The theme shows a toctree's caption only at the top level, so a
    library's "Get started", "Guides" and "Reference" would run together
    under its name. They go back in as headings among its pages."""
    lib = _library_for(app, pagename)
    if lib is None or "toctree" not in context:
        return
    groups = _section_groups(app, lib)
    if not groups:
        return
    toctree = context["toctree"]
    pathto = context["pathto"]

    def with_captions(*args, **kwargs):
        html = toctree(*args, **kwargs)
        for caption, doc in groups:
            href = "#" if doc == pagename else pathto(doc)
            m = re.search(rf'<li class="toctree-l2[^"]*"><a class="[^"]*reference internal" href="{re.escape(href)}">', html)
            if m:
                heading = f'<li class="toctree-l2 pd-caption" role="presentation"><span>{caption}</span></li>'
                html = html[:m.start()] + heading + html[m.start():]
        return html

    context["toctree"] = with_captions


def _edit_link(app, pagename, templatename, context, doctree):
    """Point "Edit on GitHub" at the file in the library's own repository."""
    lib = _library_for(app, pagename)
    if lib is None or "/" not in pagename:
        return
    page = pagename.split("/", 1)[1]
    suffix = context.get("page_source_suffix", ".md")
    url = f"https://github.com/{lib.repo}/blob/main/{lib.docs.strip('/')}/{page}{suffix}"
    # sphinx_rtd_theme uses a page's github_url meta field in place of the link it builds.
    context["meta"] = {**(context.get("meta") or {}), "github_url": url}
    context["check_meta"] = True


class _SectionWarnings(logging.Filter):
    """A section's ``suppress_warnings`` applies to that section's pages only."""

    def __init__(self, app):
        super().__init__()
        self.dirs = []
        for lib in app.config.pd_libraries:
            if lib.suppress:
                # The section's pages, and its repository's code, whose docstrings autodoc reads.
                section = Path(app.srcdir) / lib.slug
                clone = Path(app.srcdir) / "_repos" / lib.repo_name
                prefixes = tuple(str(p) + os.sep for p in {section, section.resolve(), clone, clone.resolve()})
                self.dirs.append((prefixes, lib.suppress))

    def filter(self, record):
        location = getattr(record, "location", None)
        if not isinstance(location, str):
            return True
        for prefixes, suppress in self.dirs:
            if location.startswith(prefixes) and is_suppressed_warning(
                getattr(record, "type", None), getattr(record, "subtype", None), suppress
            ):
                return False
        return True


def _prefer_own_package():
    """When a short name matches objects in two libraries ("Screen" is both
    vtterm's and pdwidgets'), take the one in the referencing module's own
    package, which is the only one it would find in a build of its own."""
    from sphinx.domains.python import PythonDomain

    original = PythonDomain.find_obj
    if getattr(original, "_omnipython_site", False):
        return

    def find_obj(self, env, modname, classname, name, type, searchmode=0):
        matches = original(self, env, modname, classname, name, type, searchmode)
        if len(matches) > 1 and modname:
            package = modname.split(".", 1)[0]
            own = [m for m in matches if m[0] == package or m[0].startswith(package + ".")]
            if len(own) == 1:
                return own
        return matches

    find_obj._omnipython_site = True
    PythonDomain.find_obj = find_obj


def _builder_inited(app):
    flt = _SectionWarnings(app)
    if flt.dirs:
        for handler in logging.getLogger(sphinx_logging.NAMESPACE).handlers:
            handler.addFilter(flt)


def setup(app):
    _prefer_own_package()
    app.add_config_value("pd_libraries", [], "env")
    app.add_config_value("pd_site_autodoc_options", {}, "env")
    srcdir = Path(app.srcdir)
    for lib in app.config.pd_libraries:
        if lib.slug in _SETUPS:
            _SETUPS[lib.slug](_SectionApp(app, srcdir / lib.slug))
    app.config.pd_site_autodoc_options = dict(app.config.autodoc_default_options)
    app.connect("source-read", _use_section_settings)
    app.connect("include-read", _included_file)
    app.connect("builder-inited", _builder_inited, priority=900)
    app.connect("html-page-context", _edit_link)
    app.connect("html-page-context", _sidebar_captions)
    return {"version": "1", "parallel_read_safe": True, "parallel_write_safe": True}
