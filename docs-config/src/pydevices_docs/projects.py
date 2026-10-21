"""The projects that share the PyDevices documentation site.

This list is the shared top bar and the cross-project reference map. A project
with `live = False` is planned: it is not in the bar and not in the
intersphinx map until the package release that flips it. Adding a project is
one entry here and a new package version.
"""

from dataclasses import dataclass

# Where the site lives until a custom domain is attached to the main project.
# Every address below hangs off it; the bar rewrites them to whatever host is
# serving the page (see theme/static/pydevices-bar.js).
ROOT = "https://pydevices.readthedocs.io"
PORTAL = "https://pydevices.github.io"
GITHUB = "https://github.com/PyDevices"


@dataclass(frozen=True)
class Project:
    name: str  # the Read the Docs subproject alias, and the name in the bar
    title: str
    summary: str
    repo: str  # "PyDevices/<repo>" or a repo plus folder
    live: bool = False
    main: bool = False

    @property
    def path(self) -> str:
        """Where the project sits under the main project's address."""
        return "/en/latest/" if self.main else f"/projects/{self.name}/en/latest/"

    @property
    def url(self) -> str:
        return ROOT + self.path

    @property
    def inventory(self) -> str:
        return self.url + "objects.inv"


# The main project is the organization overview; it is not a library.
MAIN = Project(
    name="home",
    title="PyDevices",
    summary="The organization overview: what each project is for and how to start.",
    repo="PyDevices/.github",
    live=True,
    main=True,
)

PROJECTS = (
    Project("palettes", "palettes", "Color palettes, RGB565 helpers and an HSV wheel.", "PyDevices/pydevices", live=True),
    Project("pygraphics", "pygraphics", "2D drawing primitives, fonts and blitting in C and Python.", "PyDevices/pygraphics", live=True),
    Project("pdwidgets", "pdwidgets", "A pure-Python widget toolkit for touch displays.", "PyDevices/pydevices", live=True),
)


def live_projects():
    return [MAIN, *[p for p in PROJECTS if p.live]]
