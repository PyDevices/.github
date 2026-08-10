#!/usr/bin/env bash
# Idempotent pydisplay desktop dev environment for the PyDevices cloud workspace.
#
# Complements cloud-workspace-install.sh and cloud-python-deps.sh:
#   - pip install pydisplay requirements.txt (TestPyPI runtime stack for CPython)
#   - mip install desktop board_config, palettes, pdwidgets into ~/.micropython/lib
#   - ensure shell env (PATH, PYTHONPATH, MICROPYPATH) via pydisplay-env.sh + bashrc hook
#
# Run from pydisplay/src/ after sourcing pydisplay-env.sh (or open a new shell).
# See micropython-hardware docs/install-workflows.md (CircuitPython-compatible mip, mpy=False).
#
# Safe to re-run. Intentionally does not `set -e` on optional TestPyPI steps.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPOS="${PYDEVICES_REPOS_ROOT:-/agent/repos}"
PYDISPLAY="${PYDISPLAY_ROOT:-$REPOS/pydisplay}"
MIP_INDEX="https://PyDevices.github.io/micropython-lib/mip/PyDevices"
MPY_LIB="${HOME}/.micropython"
BASHRC="${HOME}/.bashrc"
ENV_FILE="${SCRIPT_DIR}/pydisplay-env.sh"
BASHRC_BEGIN="# >>> pydevices pydisplay dev env >>>"
BASHRC_END="# <<< pydevices pydisplay dev env <<<"

log() { printf 'cloud-pydisplay-dev-env: %s\n' "$*"; }

die() {
    log "ERROR: $*"
    exit 1
}

# shellcheck source=pydisplay-env.sh
source "${ENV_FILE}" || die "cannot source ${ENV_FILE}"

ensure_pydisplay_venv() {
    if [[ ! -d "$PYDISPLAY" ]]; then
        die "pydisplay not found at $PYDISPLAY"
    fi
    local vpy="$PYDISPLAY/.venv/bin/python"
    local vpip="$PYDISPLAY/.venv/bin/pip"
    if [[ ! -x "$vpy" ]]; then
        log "create venv: $PYDISPLAY/.venv"
        python3 -m venv "$PYDISPLAY/.venv" || die "venv creation failed"
    fi
    if ! "$vpy" -c "import pip" 2>/dev/null; then
        log "recreate broken venv: $PYDISPLAY/.venv"
        rm -rf "$PYDISPLAY/.venv"
        python3 -m venv "$PYDISPLAY/.venv" || die "venv recreation failed"
    fi
    "$vpip" install -q --upgrade pip || true
    log "pip install -r $PYDISPLAY/requirements.txt"
    "$vpip" install -q -r "$PYDISPLAY/requirements.txt" || \
        log "warn: pydisplay requirements.txt install failed"
}

ensure_micropython_bin() {
    if command -v micropython >/dev/null 2>&1; then
        return 0
    fi
    die "micropython not on PATH (expected ${PYDISPLAY_ROOT}/bin/micropython)"
}

mip_install_micropython_lib() {
    mkdir -p "${MPY_LIB}/lib"
    log "mip install desktop board_config, palettes, pdwidgets -> ${MPY_LIB}/lib"
    (
        cd "${MPY_LIB}" || exit 1
        INDEX="https://PyDevices.github.io/micropython-lib/mip/PyDevices"
        micropython -m mip install --no-mpy -t lib -i "$INDEX" \
            github:PyDevices/micropython-hardware/board_configs/desktop \
            palettes \
            pdwidgets
        micropython <<'PY'
import board_config
import board_devices
import palettes
import pdwidgets
print("board_config:", board_config.__file__)
print("palettes:", palettes.__file__)
print("pdwidgets:", pdwidgets.__file__)
PY
    ) || die "micropython mip install failed"
}

install_bashrc_hook() {
    if [[ ! -f "$BASHRC" ]]; then
        touch "$BASHRC"
    fi
    if grep -qF "$BASHRC_BEGIN" "$BASHRC" 2>/dev/null; then
        log "bashrc hook already present"
        return 0
    fi
    log "append pydisplay env hook to $BASHRC"
    cat >>"$BASHRC" <<EOF

${BASHRC_BEGIN}
# Added by cloud-pydisplay-dev-env.sh — run examples from pydisplay/src/
if [[ -f "${ENV_FILE}" ]]; then
    # shellcheck source=/dev/null
    source "${ENV_FILE}"
fi
${BASHRC_END}
EOF
}

ensure_pydisplay_venv
ensure_micropython_bin
mip_install_micropython_lib
install_bashrc_hook

log "done — cd ${PYDISPLAY}/src and run micropython/circuitpython/python examples"
