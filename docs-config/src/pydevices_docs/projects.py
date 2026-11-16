# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Where the documentation site and its neighbours live.

Every library's documentation is one site, built from the ``docs-site``
folder beside this package (see `pydevices_docs.site`). A library's own
build, run in its repository's CI, links back to that site from the top bar
and resolves references through its inventory.
"""

# The site's address until a custom domain is canonical; Read the Docs
# redirects it to the canonical domain once there is one.
ROOT = "https://pydevices.readthedocs.io"
SITE = ROOT + "/en/latest/"
PORTAL = "https://pydevices.github.io"
GITHUB = "https://github.com/PyDevices"
