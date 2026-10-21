"""The PyDevices main documentation project: the organization overview."""

from pydevices_docs import configure

globals().update(configure(
    "PyDevices", __file__,
    repo="PyDevices/.github", edit_path="docs-site",
    version_file=None, main=True,
))
exclude_patterns = ["_build"]
