# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""The PyDevices tools' documentation site: every tool's docs in one build.

Run ``python docs-site/gather.py --site tools-docs-site`` first; it brings
each tool's ``docs`` folder in from its own repository.
"""

from pathlib import Path

from omnipython_docs.site import configure_site, read_libraries

LIBRARIES = read_libraries(Path(__file__).with_name("libraries.toml"))

globals().update(configure_site(
    __file__, LIBRARIES,
    title="PyDevices", logo="pydevices-logo.svg", website="https://pydevices.com", sections="Tools",
))
