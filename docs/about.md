# PyDevices GitHub Organization Summary

## Overview

PyDevices is an open-source GitHub organization focused on a **cross-platform Python display, graphics, and UI ecosystem** that works across:

* MicroPython
* CircuitPython
* CPython
* PyScript/Pyodide (browser PWAs)
* Android APKs

The project's goal is to let developers build display-driven applications that can run on microcontrollers, desktops, browsers, and Android with a largely consistent architecture.

## Architecture Overview

PyDevices describes its stack as:

1. **pydevices** (reusable product packages and drivers)
2. Optional graphics/color layers
3. Widget toolkits
4. Full LVGL integration when needed

This allows developers to start with lightweight Python display drivers and progressively add more advanced UI capabilities.

\---

# Key Repositories

## 1. pydevices

**Purpose:** Core product library, hardware driver suite, and PyDevices Board Contract owner.

Provides cross-runtime `displaydev`, `audiodev`, optional `eventsys`, timers,
board configurations (`board_config.py`), lazy peripherals (`boarddev`), and hardware drivers through prefixed TestPyPI
distributions and unprefixed MIP packages.

**Best for:** Core hardware integration, board configurations, embedded display/audio drivers, and cross-platform desktop/browser display backends.

\---

## 2\. pydevices-examples

**Purpose:** Examples, documentation, and PyScript showcase.

Shows the product in action across MicroPython, CircuitPython, CPython,
desktop, browser, and notebooks. It owns application examples and utilities,
not reusable product libraries.

\---

## 3\. mpftp

**Purpose:** Development tooling.

Provides:

* Dual-pane file transfer
* REPL access
* mip support
* circup support
* Firmware flashing

Useful for managing MicroPython boards.

\---

## 4\. palettes

**Purpose:** Color management library.

Includes:

* Color wheel generation
* Color cube utilities
* Material Design colors
* Windows 16-color palette support

\---

## 5\. pdwidgets

**Purpose:** Lightweight widget framework.

Provides:

* Buttons
* Forms
* Navigation controls
* Themes

Designed as a simpler alternative to full LVGL implementations.

\---

## 6\. lv\_bindings

**Purpose:** LVGL binding generator.

Generates bindings from the LVGL C API for:

* MicroPython
* CircuitPython
* CPython

\---

## 7. cmods

**Purpose:** Native module build workspace.

Contains build and integration infrastructure for native LVGL-related modules.

---

## 8. micropython-lib

**Purpose:** PyDevices MIP distribution fork & package index generator.

Aggregates PyDevices packages and drives the automated publication of the PyDevices custom MIP package index (`https://PyDevices.github.io/micropython-lib/mip/PyDevices`), generating both precompiled `.mpy` and source `.py` distributions for MicroPython.

---


# Native / Performance-Focused Repositories

## displayif

Native display bus and framebuffer implementations for MicroPython.

## pygraphics

Graphics primitives and framebuffer support with both native and pure-Python implementations.

## lvgl-python

Native LVGL extension module for CPython.

## lvgl-micropython

LVGL integration and user module support for MicroPython.

## lvgl-circuitpython

LVGL integration for CircuitPython builds.

\---

# Android and Web Efforts

## pydevices-examples\_android

Provides:

* Android APK packaging
* Buildozer examples
* python-for-android recipes
* Mobile runtime support

## Browser PWA Support

Supports installable browser applications using:

* PyScript
* Pyodide
* Shared runtime concepts with embedded targets

The same application architecture can be reused between MCU, desktop, browser, and Android deployments.

\---

# Overall Assessment

PyDevices appears to be a unified display and UI platform for Python spanning microcontrollers, desktop applications, browser applications, and Android devices.

It combines:

* Hardware drivers
* Graphics rendering
* UI widgets
* LVGL integration
* Development tools
* Android deployment
* Browser/PWA deployment

into a cohesive cross-platform ecosystem.
