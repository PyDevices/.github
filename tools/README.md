# dotgithub `tools/`

Developer tools and local development servers for the PyDevices organization.

| Script | Purpose |
|---|---|
| [`serve_portal.py`](serve_portal.py) | Centralized local HTTP development server for the whole org portal with Cross-Origin-Isolation (COI) headers and virtual route dispatch |

## Organization Portal Server (`serve_portal.py`)

Serves the entire organization portal locally with exact production path parity:

```bash
python3 dotgithub/tools/serve_portal.py
```

### Route Dispatch:
- `http://127.0.0.1:8000/` → `PyDevices.github.io/` (Org portal homepage & product landing pages)
- `http://127.0.0.1:8000/vendor/micropython/` → `PyDevices.github.io/vendor/micropython/` (Centralized WebAssembly binary runtime)
- `http://127.0.0.1:8000/pydevices-examples/pyscript/` → `pydevices-examples/.site/pyscript/` (PyScript gallery & demos)
- `http://127.0.0.1:8000/mip/` → `mip/.site/` (MIP package index)

### Features:
- **Cross-Origin-Isolation**: Emits `COOP: same-origin`, `COEP: require-corp`, `CORP: cross-origin` for `SharedArrayBuffer` support on worker-backed pages (`repl.html`). Use `--no-coi` to disable.
- **Server Probe**: Emits `X-PyDevices-Server: portal` response header enabling CLI runners (`pyscript.py`) to discover and reuse the running server.
- **Instant Live Refresh**: Emits `Cache-Control: no-store, must-revalidate` for immediate live code editing.
- **Debug Log Sink**: Exposes `POST /__debug` accepting JSON and text logs from browser scripts and printing them to the terminal.
