#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
serve_portal.py — Centralized local development server for the PyDevices org portal.

Serves the entire PyDevices ecosystem locally with exact production path parity:
  /                        → PyDevices.github.io/             (Org portal & /simulator/)
  /vendor/micropython/     → PyDevices.github.io/vendor/      (Centralized WASM runtime)
  /assets/                 → PyDevices.github.io/assets/      (Shared brand chrome & apps)
  /pydevices-examples/     → pydevices-examples/.site/        (PyScript gallery & demos)
  /mip/                    → mip/.site/                       (MIP package index)
  /<repo>/                 → PyDevices.github.io/<repo>/      (Product landing pages)

Features:
1. Cross-Origin Isolation (COOP/COEP/CORP) headers for SharedArrayBuffer support.
2. X-PyDevices-Server: portal header for smart client probe detection.
3. Permissive /__debug log sink endpoint for browser-to-terminal log streaming.
4. Cache-Control: no-store, must-revalidate for instant live edits.
"""

from __future__ import annotations

import argparse
import datetime
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import sys
import urllib.parse

SCRIPT_DIR = Path(__file__).resolve().parent
DOTGITHUB_DIR = SCRIPT_DIR.parent
ORG_DIR = DOTGITHUB_DIR.parent
PORTAL_DIR = ORG_DIR / "PyDevices.github.io"
EXAMPLES_DIR = ORG_DIR / "pydevices-examples"
MIP_DIR = ORG_DIR / "mip"

DEBUG_PREFIX = "/__debug"


def _stamp() -> str:
    now = datetime.datetime.now(datetime.UTC)
    return now.strftime("%H:%M:%S.") + f"{now.microsecond // 1000:03d}"


class PortalRequestHandler(SimpleHTTPRequestHandler):
    """Virtual routing request handler for the PyDevices organization portal."""

    coi_enabled = True
    server_signature = "portal"

    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".mjs": "application/javascript",
        ".wasm": "application/wasm",
        ".toml": "text/plain",
        ".json": "application/json",
        ".svg": "image/svg+xml",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".css": "text/css",
        ".html": "text/html",
        ".py": "text/plain",
    }

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("X-PyDevices-Server", self.server_signature)
        if self.coi_enabled:
            self.send_header("Cross-Origin-Opener-Policy", "same-origin")
            self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
            self.send_header("Cross-Origin-Resource-Policy", "cross-origin")
        super().end_headers()

    def translate_path(self, path: str) -> str:
        """Translate a URL path into the appropriate org repository file system path."""
        parsed_url = urllib.parse.urlparse(path)
        clean_path = urllib.parse.unquote(parsed_url.path)
        
        # 1. Gallery routes: /pydevices-examples/...
        if clean_path.startswith("/pydevices-examples/"):
            subpath = clean_path.removeprefix("/pydevices-examples/")
            # Direct mapping to .site if it exists there
            target = EXAMPLES_DIR / ".site" / subpath
            if target.exists() or not subpath or subpath.endswith("/"):
                return str(target)
            # Check if referencing source lib/
            target_lib = EXAMPLES_DIR / subpath
            if target_lib.exists():
                return str(target_lib)
            return str(target)

        # 2. MIP package index routes: /mip/...
        if clean_path.startswith("/mip/"):
            subpath = clean_path.removeprefix("/mip/")
            target = MIP_DIR / ".site" / subpath
            if target.exists() or not subpath or subpath.endswith("/"):
                return str(target)
            target_raw = MIP_DIR / subpath
            if target_raw.exists():
                return str(target_raw)
            return str(target)

        # 3. Default: PyDevices.github.io portal root
        subpath = clean_path.lstrip("/")
        target = PORTAL_DIR / subpath
        return str(target)

    def _is_debug(self) -> bool:
        return self.path == DEBUG_PREFIX or self.path.startswith(DEBUG_PREFIX + "/")

    def _send_cors(self, status: int = 204) -> None:
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_OPTIONS(self) -> None:
        if self._is_debug():
            self._send_cors()
            return
        self.send_response(204)
        self.end_headers()

    def do_POST(self) -> None:
        if not self._is_debug():
            self.send_error(404, "Not Found")
            return
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        self._log_debug(raw)
        self._send_cors()

    def do_GET(self) -> None:
        if self._is_debug():
            self._send_cors(200)
            return
        super().do_GET()

    def do_HEAD(self) -> None:
        if self._is_debug():
            self._send_cors(200)
            return
        super().do_HEAD()

    def _log_debug(self, raw: bytes) -> None:
        stamp = _stamp()
        text = raw.decode("utf-8", "replace").strip()
        payload = None
        try:
            payload = json.loads(text)
            text = json.dumps(payload, ensure_ascii=False, indent=2)
        except (ValueError, TypeError):
            pass
        client = self.address_string()
        if isinstance(payload, dict) and payload.get("level") == "timing":
            label = (payload.get("args") or ["?"])[0]
            sys.stdout.write(f"\n[timing {stamp}] {label}\n")
        else:
            sys.stdout.write(f"\n[debug {stamp} {client}] {self.path}\n{text}\n")
        sys.stdout.flush()

    def log_message(self, fmt: str, *args) -> None:
        stamp = _stamp()
        sys.stderr.write(f"[{stamp}] {self.address_string()} {fmt % args}\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-p", "--port", type=int, default=8000, help="port (default: 8000)")
    parser.add_argument(
        "-b", "--bind", default="127.0.0.1", help="bind address (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--no-coi", action="store_true", help="do not send cross-origin isolation headers"
    )
    args = parser.parse_args(argv)

    PortalRequestHandler.coi_enabled = not args.no_coi
    handler = partial(PortalRequestHandler, directory=str(PORTAL_DIR))

    httpd = ThreadingHTTPServer((args.bind, args.port), handler)
    base = f"http://{args.bind}:{args.port}"

    print(f"PyDevices Organization Portal Server")
    print(f"  base URL:               {base}/")
    print(f"  portal root:            {PORTAL_DIR}")
    print(f"  gallery mount:          {base}/pydevices-examples/pyscript/")
    print(f"  simulator mount:        {base}/simulator/")
    print(f"  mip index mount:        {base}/mip/")
    print(f"  cross-origin isolation: {'on' if PortalRequestHandler.coi_enabled else 'off'}")
    print(f"  server signature:       X-PyDevices-Server: {PortalRequestHandler.server_signature}")
    print(f"  debug log sink:         POST {base}{DEBUG_PREFIX}")
    print("")
    print("Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down portal server.")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
