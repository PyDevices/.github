# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Descriptions shared by TestPyPI and MIP publications of pydevices packages."""

PYDEVICES_DESCRIPTIONS = {
    "pydevices": "Portable display, audio, event, and timing foundations for PyDevices",
    "pydevices-desktop": "Complete PyDevices desktop stack and board configuration",
    # MIP only: on PyPI bledev is inside the pydevices wheel.
    "bledev": "Portable async Bluetooth Low Energy for PyDevices, over aioble on boards",
    # MIP only, like bledev: on PyPI medialink is inside the pydevices wheel.
    "medialink": "Live audio and video between boards and computers: a walkie-talkie, an intercom, a baby monitor",
}
