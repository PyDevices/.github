# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Where the documentation site and its neighbours live.

Every library's documentation is one site, built from the ``docs-site``
folder beside this package (see `pydevices_docs.site`). A library's own
build, run in its repository's CI, links back to that site from the top bar
and resolves references through its inventory.
"""

# The site's canonical address. The old Read the Docs addresses redirect here.
ROOT = "https://docs.omnipython.org"
SITE = ROOT + "/en/latest/"
PORTAL = "https://omnipython.org"
GITHUB = "https://github.com/PyDevices"
