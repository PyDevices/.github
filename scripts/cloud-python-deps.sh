#!/usr/bin/env bash
# Idempotent Python dev-environment setup for the PyDevices cloud workspace.
#
# Complements cloud-workspace-install.sh (which builds the symlink layout,
# clones missing siblings, and shallow upstream clones). This script:
#
#   - installs system packages needed for venv + pygame-ce when missing
#   - creates the repo-root `.venv` for runnable pure-Python products
#   - pydisplay  (flagship)  -> requirements-dev.txt + pygame-ce + lvgl-cpython
#   - palettes   pdwidgets   -> ruff
#
# Safe to run on every cloud VM boot (environment.json install). See AGENTS.md.
# Intentionally does NOT `set -e`: a single optional install (e.g. TestPyPI
# lvgl-cpython) must never abort VM startup for the whole team. Required
# failures (no ensurepip after apt) still exit non-zero at the end.
set -uo pipefail

REPOS="${PYDEVICES_REPOS_ROOT:-/agent/repos}"

log() { printf 'cloud-python-deps: %s\n' "$*"; }

# --- system packages (snapshot VMs may omit these) ----------------------------

ensure_system_packages() {
    local need=0
    if ! python3 -c "import ensurepip" 2>/dev/null; then
        need=1
    fi
    if ! pkg-config --exists sdl2 2>/dev/null; then
        need=1
    fi
    if ((need == 0)); then
        return 0
    fi
    if ! command -v sudo >/dev/null 2>&1; then
        log "warn: sudo unavailable; cannot install python3-venv/libsdl2-dev"
        return 1
    fi
    log "install apt packages: python3-venv libsdl2-dev"
    sudo DEBIAN_FRONTEND=noninteractive apt-get update -qq || {
        log "warn: apt-get update failed"
        return 1
    }
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
        python3-venv python3.12-venv libsdl2-dev || {
        log "warn: apt-get install failed"
        return 1
    }
}

# Create <repo>/.venv (idempotent) and upgrade pip. Echoes the venv bin path
# on success, nothing on failure/missing so callers can guard with `[ -n ... ]`.
ensure_venv() {
    local dir="$REPOS/$1"
    if [[ ! -d "$dir" ]]; then
        log "skip (repo missing): $dir" >&2
        return 1
    fi

    # Recreate broken leftovers from a prior boot without ensurepip.
    if [[ -d "$dir/.venv" ]] && ! "$dir/.venv/bin/python" -c "import pip" 2>/dev/null; then
        log "recreate broken venv: $dir/.venv" >&2
        rm -rf "$dir/.venv"
    fi

    if [[ ! -x "$dir/.venv/bin/python" ]]; then
        log "create venv: $dir/.venv" >&2
        python3 -m venv "$dir/.venv" >&2 || { log "venv creation failed: $dir" >&2; return 1; }
    fi
    "$dir/.venv/bin/pip" install -q --upgrade pip >&2 || true
    printf '%s' "$dir/.venv/bin"
}

ensure_system_packages || true

if ! python3 -c "import ensurepip" 2>/dev/null; then
    log "ERROR: ensurepip still unavailable after package install — cannot create venvs"
    exit 1
fi

# --- pydisplay: flagship dev tooling + desktop backend + LVGL binding ---------
if bin="$(ensure_venv pydisplay)"; then
    "$bin/pip" install -q -r "$REPOS/pydisplay/requirements-dev.txt" || \
        log "warn: pydisplay requirements-dev install failed"
    # pygame-ce is the desktop fallback backend / Windows default (PGDisplay);
    # deliberately not in requirements-dev.txt (SDL2 is the documented primary).
    "$bin/pip" install -q pygame-ce || log "warn: pygame-ce install failed"
    # CPython LVGL binding (import name `lvgl`) from TestPyPI — optional; the
    # LVGL examples/timer kits need it. Best-effort so TestPyPI outages don't
    # break startup.
    "$bin/pip" install -q -i https://test.pypi.org/simple/ \
        --extra-index-url https://pypi.org/simple/ lvgl-cpython || \
        log "warn: lvgl-cpython (TestPyPI) install skipped; LVGL examples unavailable"
    # Put the source-only sibling packages on pydisplay's venv path so examples
    # that `import palettes` / `import pdwidgets` resolve in the example matrix.
    sp="$("$bin/python" -c 'import site; print(site.getsitepackages()[0])' 2>/dev/null)"
    if [[ -n "${sp:-}" ]]; then
        printf '%s\n%s\n' "$REPOS/palettes/src" "$REPOS/pdwidgets/src" \
            > "$sp/pydevices_siblings.pth"
        log "wrote $sp/pydevices_siblings.pth"
    fi
else
    log "ERROR: pydisplay venv unavailable"
    exit 1
fi

# --- palettes / pdwidgets: source-only libs; venv just needs ruff -------------
for r in palettes pdwidgets; do
    if bin="$(ensure_venv "$r")"; then
        "$bin/pip" install -q ruff || log "warn: ruff install failed for $r"
    else
        log "warn: venv unavailable for $r"
    fi
done

log "done"
