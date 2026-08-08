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

1. **pydisplay** (foundation)
2. Optional graphics/color layers
3. Widget toolkits
4. Full LVGL integration when needed

This allows developers to start with lightweight Python display drivers and progressively add more advanced UI capabilities.

\---

# Key Repositories

## 1\. pydisplay

**Purpose:** Core display, input, and event framework.

Provides pure-Python display drivers and serves as the foundation for the entire ecosystem across MicroPython, CircuitPython, and CPython.

**Best for:** Embedded displays, touchscreens, desktop display backends.

\---

## 2\. micropython-hardware

**Purpose:** Hardware support package.

Contains:

* Board configurations
* Display drivers
* Touch drivers
* Hardware documentation

Designed for MicroPython and CircuitPython environments.

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

## 7\. cmods

**Purpose:** Native module build workspace.

Contains build and integration infrastructure for native LVGL-related modules.

\---

# Native / Performance-Focused Repositories

## displayif

Native display bus and framebuffer implementations for MicroPython.

## pygraphics

Graphics primitives and framebuffer support with both native and pure-Python implementations.

## lv\_cpython\_mod

Native LVGL extension module for CPython.

## lv\_micropython\_cmod

LVGL integration and user module support for MicroPython.

## lv\_circuitpython\_mod

LVGL integration for CircuitPython builds.

\---

# Android and Web Efforts

## pydisplay\_android

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

