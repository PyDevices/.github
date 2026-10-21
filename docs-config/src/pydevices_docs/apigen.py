"""Write the API reference pages for a project from its package folders.

This stands in for the MkDocs `gen-files` script the three library sites used:
for each package named in `api_packages`, one `reference/<module>.rst` page
per public module, each an `automodule`, plus `reference/index.rst`. Modules
and packages whose name starts with an underscore are skipped.

The pages are generated into the source tree, so list `reference/` in the
project's .gitignore and put `reference/index` in a toctree.
"""

from __future__ import annotations

from pathlib import Path

OUT = "reference"


def _write(path: Path, text: str) -> None:
    if path.exists() and path.read_text() == text:
        return  # leave the mtime alone so Sphinx does not rebuild the page
    path.write_text(text)


def _modules(source_dirs, package, skip=()):
    for base in source_dirs:
        pkg_dir = Path(base) / package
        if not pkg_dir.is_dir():
            continue
        found = []
        for path in sorted(pkg_dir.rglob("*.py")):
            rel = path.relative_to(base).with_suffix("")
            parts = list(rel.parts)
            if parts[-1] == "__init__":
                parts = parts[:-1]
            if not parts or any(p.startswith("_") or p in skip for p in parts):
                continue
            found.append(".".join(parts))
        return found
    return []


def generate(app):
    srcdir = Path(app.srcdir)
    out = srcdir / OUT
    out.mkdir(exist_ok=True)
    names = []
    for package in app.config.api_packages:
        for module in _modules(app.config.api_source_dirs, package, app.config.api_skip):
            title = f"{module}"
            body = f"{title}\n{'=' * len(title)}\n\n.. automodule:: {module}\n"
            _write(out / f"{module}.rst", body)
            names.append(module)
    index = "API reference\n=============\n\n.. toctree::\n   :maxdepth: 1\n\n"
    index += "".join(f"   {n}\n" for n in names)
    _write(out / "index.rst", index)


def setup(app):
    app.add_config_value("api_packages", [], "env")
    app.add_config_value("api_source_dirs", [], "env")
    app.add_config_value("api_skip", [], "env")
    app.connect("builder-inited", generate)
    return {"version": "1", "parallel_read_safe": True, "parallel_write_safe": True}
