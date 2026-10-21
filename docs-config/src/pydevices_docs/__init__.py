"""Shared Sphinx configuration and theme for the PyDevices documentation projects.

A project's ``conf.py`` is five lines:

    from pydevices_docs import configure

    globals().update(configure(
        "palettes", __file__, repo="PyDevices/pydevices", edit_path="palettes/docs",
        source_dirs=["../lib"], api_packages=["palettes"],
    ))

``configure`` returns the settings; the project sets only its name and where
its code is. The theme, the shared top bar, the cross-project reference map
and the Markdown setup all come from here.
"""

from __future__ import annotations

import os
import urllib.request
from pathlib import Path

from .projects import GITHUB, MAIN, PORTAL, PROJECTS, ROOT, live_projects

__version__ = "0.1.0"

THEME_DIR = Path(__file__).parent / "theme"
TEMPLATES_DIR = Path(__file__).parent / "templates"

__all__ = ["configure", "setup", "live_projects", "__version__"]


def _keep_property_docstrings_plain():
    """Napoleon reads "Face style: flat or raised." on a property as a type
    ("Face style") and a description, which swaps the two. Our property
    docstrings are sentences, so leave them alone.
    """
    from sphinx.ext.napoleon.docstring import GoogleDocstring

    original = GoogleDocstring._parse_attribute_docstring
    if getattr(original, "_pydevices_plain", False):
        return

    def _parse_attribute_docstring(self):
        if getattr(self, "_what", None) == "property":
            return self._consume_to_end()
        return original(self)

    _parse_attribute_docstring._pydevices_plain = True
    GoogleDocstring._parse_attribute_docstring = _parse_attribute_docstring


def setup(app):
    """Sphinx entry point: registers the `pydevices` theme."""
    _keep_property_docstrings_plain()
    app.add_html_theme("pydevices", str(THEME_DIR))
    return {"version": __version__, "parallel_read_safe": True, "parallel_write_safe": True}


def _reachable(url: str) -> bool:
    """True when a published inventory answers, so a project that is not on
    the site yet does not turn into an intersphinx warning (and a failed
    `-W` build)."""
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


def intersphinx_map(skip: str = "") -> dict:
    """The reference map: the Python and MicroPython manuals plus every other
    live PyDevices project whose inventory is published.

    Set ``PYDEVICES_DOCS_OFFLINE=1`` to leave out every sibling, for a build
    with no network.
    """
    mapping = {
        "python": ("https://docs.python.org/3", None),
        "micropython": ("https://docs.micropython.org/en/latest", None),
    }
    if os.environ.get("PYDEVICES_DOCS_OFFLINE"):
        return {}
    for p in live_projects():
        if p.name == skip:
            continue
        key = "pydevices" if p.main else p.name
        if _reachable(p.inventory):
            mapping[key] = (p.url, None)
    return mapping


def _read_version(conf_file: str, version_file: str | None) -> str:
    if not version_file:
        return ""
    path = (Path(conf_file).parent / version_file).resolve()
    try:
        return path.read_text().strip()
    except OSError:
        return ""


def configure(
    name: str,
    conf_file: str,
    *,
    repo: str | None = None,
    edit_path: str = "docs",
    source_dirs: list[str] | tuple[str, ...] = (),
    api_packages: list[str] | tuple[str, ...] = (),
    api_skip: list[str] | tuple[str, ...] = (),
    use_module_all: bool = False,
    mock_imports: list[str] | tuple[str, ...] = (),
    version_file: str | None = "../VERSION",
    main: bool = False,
    copyright_from: int = 2024,
    extra_extensions: list[str] | tuple[str, ...] = (),
) -> dict:
    """Return the Sphinx settings for one PyDevices project.

    name          the project's name, as the bar and the title show it
    conf_file     the project's ``conf.py`` (pass ``__file__``)
    repo          "PyDevices/<repo>", for the Edit on GitHub link (default PyDevices/<name>)
    edit_path     the folder holding ``conf.py``, relative to the repo root ("palettes/docs")
    source_dirs   folders, relative to ``conf.py``, put on ``sys.path`` for autodoc
    api_packages  packages to write API reference pages for (see ``pydevices_docs.apigen``)
    api_skip      folder names inside those packages to leave out of the API pages ("icons")
    use_module_all document what a package lists in ``__all__``, re-exports included, instead
                  of only what the module defines (for a package whose API is private modules)
    mock_imports  modules autodoc should treat as importable without importing
    version_file  file, relative to ``conf.py``, holding the version; None for no version
    main          True for the organization's main project
    """
    import sys

    conf_dir = Path(conf_file).resolve().parent
    for d in source_dirs:
        p = str((conf_dir / d).resolve())
        if p not in sys.path:
            sys.path.insert(0, p)

    repo = repo or f"PyDevices/{name}"
    release = _read_version(conf_file, version_file)
    conf_path = "/" + edit_path.strip("/") + "/"

    extensions = [
        "myst_parser",
        "sphinx_design",
        "sphinxcontrib.mermaid",
        "sphinx.ext.autodoc",
        "sphinx.ext.napoleon",
        "sphinx.ext.intersphinx",
        "sphinx.ext.viewcode",
        *extra_extensions,
    ]
    if api_packages:
        extensions.append("pydevices_docs.apigen")

    # A flag in autodoc_default_options is on whenever its key is present, even
    # with a False value, so add ignore-module-all only when it is wanted.
    autodoc_options = {"members": True, "show-inheritance": True}
    if not use_module_all:
        autodoc_options["ignore-module-all"] = True

    settings = {
        "project": name,
        "copyright": f"{copyright_from}-2026, Brad Barnett & PyDevices Contributors",
        "author": "PyDevices Contributors",
        "release": release,
        "version": release,
        "extensions": extensions,
        "exclude_patterns": ["_build", "README.md", "Thumbs.db", ".DS_Store"],
        "source_suffix": {".rst": "restructuredtext", ".md": "markdown"},
        "master_doc": "index",
        # A single backtick in a docstring is a cross-reference: `Palette` or `text <palettes.Palette.name>`.
        "default_role": "py:obj",
        # Markdown (MyST)
        "myst_enable_extensions": ["colon_fence", "deflist", "attrs_block", "attrs_inline", "html_image", "tasklist"],
        "myst_heading_anchors": 3,
        # Docstrings: Google style only.
        "mermaid_version": "11.4.1",
        "napoleon_google_docstring": True,
        "napoleon_numpy_docstring": False,
        "napoleon_use_param": True,
        "napoleon_use_rtype": False,
        "autodoc_member_order": "bysource",
        "autodoc_typehints": "none",
        "autodoc_default_options": autodoc_options,
        "autodoc_mock_imports": list(mock_imports),
        "api_packages": list(api_packages),
        "api_skip": list(api_skip),
        "api_source_dirs": [str((conf_dir / d).resolve()) for d in source_dirs],
        "intersphinx_mapping": intersphinx_map(skip="home" if main else name),
        "intersphinx_timeout": 10,
        # Theme
        "html_theme": "pydevices",
        "templates_path": [str(TEMPLATES_DIR)],
        "html_theme_options": {
            "navigation_depth": 3,
            "collapse_navigation": False,
            "sticky_navigation": True,
            "titles_only": False,
            "logo_only": False,
        },
        "html_title": name if main else f"{name} documentation",
        "html_favicon": None,
        "html_static_path": [],
        "html_show_sphinx": False,
        "html_context": {
            "display_github": True,
            "github_user": repo.split("/")[0],
            "github_repo": repo.split("/")[1],
            "github_version": "main",
            "conf_py_path": conf_path,
            "pd_project": name,
            "pd_is_main": main,
            "pd_projects": [
                {"name": p.name, "title": p.title, "url": p.url, "path": p.path}
                for p in live_projects()
            ],
            "pd_portal": PORTAL,
            "pd_github": GITHUB,
        },
    }
    return settings
