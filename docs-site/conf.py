# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""The OmniPython documentation site: every library's docs in one build.

Run ``python docs-site/gather.py`` first; it brings each library's ``docs``
folder in from its own repository.
"""

from pathlib import Path

from omnipython_docs.site import configure_site, read_libraries

LIBRARIES = read_libraries(Path(__file__).with_name("libraries.toml"))

globals().update(configure_site(__file__, LIBRARIES))
