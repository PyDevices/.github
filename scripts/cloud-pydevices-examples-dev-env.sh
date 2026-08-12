#!/usr/bin/env bash
# Idempotent pydevices-examples desktop dev environment for the PyDevices cloud workspace.
#
# Complements cloud-workspace-install.sh and cloud-python-deps.sh:
#   - pip install pydevices-examples requirements.txt (TestPyPI runtime stack for CPython)
#   - mip install desktop board_config, eventsys, palettes, pdwidgets into ~/.micropython/lib
#   - ensure shell env (PATH, PYTHONPATH, MICROPYPATH) via pydevices-examples-env.sh + bashrc hook
#
# Run from pydevices-examples/lib/ after sourcing pydevices-examples-env.sh (or open a new shell).
# See pydevices docs/install-workflows.md (CircuitPython-compatible mip, mpy=False).
#
# Safe to re-run. Intentionally does not `set -e` on optional TestPyPI steps.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPOS="${PYDEVICES_REPOS_ROOT:-/agent/repos}"
EXAMPLES="${PYDEVICES_EXAMPLES_ROOT:-$REPOS/pydevices-examples}"
MIP_INDEX="https://PyDevices.github.io/micropython-lib/mip/PyDevices"
MPY_LIB="${HOME}/.micropython"
BASHRC="${HOME}/.bashrc"
ENV_FILE="${SCRIPT_DIR}/pydevices-examples-env.sh"
BASHRC_BEGIN="# >>> pydevices pydevices-examples dev env >>>"
BASHRC_END="# <<< pydevices pydevices-examples dev env <<<"

log() { printf 'cloud-pydevices-examples-dev-env: %s\n' "$*"; }

die() {
    log "ERROR: $*"
    exit 1
}

# shellcheck source=pydevices-examples-env.sh
source "${ENV_FILE}" || die "cannot source ${ENV_FILE}"

ensure_pydevices_examples_venv() {
    if [[ ! -d "$EXAMPLES" ]]; then
        die "pydevices-examples not found at $EXAMPLES"
    fi
    local vpy="$EXAMPLES/.venv/bin/python"
    local vpip="$EXAMPLES/.venv/bin/pip"
    if [[ ! -x "$vpy" ]]; then
        log "create venv: $EXAMPLES/.venv"
        python3 -m venv "$EXAMPLES/.venv" || die "venv creation failed"
    fi
    if ! "$vpy" -c "import pip" 2>/dev/null; then
        log "recreate broken venv: $EXAMPLES/.venv"
        rm -rf "$EXAMPLES/.venv"
        python3 -m venv "$EXAMPLES/.venv" || die "venv recreation failed"
    fi
    "$vpip" install -q --upgrade pip || true
    log "pip install -r $EXAMPLES/requirements.txt"
    "$vpip" install -q -r "$EXAMPLES/requirements.txt" || \
        log "warn: pydevices-examples requirements.txt install failed"
}

ensure_micropython_bin() {
    if command -v micropython >/dev/null 2>&1; then
        return 0
    fi
    die "micropython not on PATH (expected ${PYDEVICES_EXAMPLES_ROOT}/bin/micropython)"
}

mip_install_micropython_lib() {
    mkdir -p "${MPY_LIB}/lib"
    log "mip install desktop board_config, eventsys, palettes, pdwidgets -> ${MPY_LIB}/lib"
    (
        cd "${MPY_LIB}" || exit 1
        INDEX="https://PyDevices.github.io/micropython-lib/mip/PyDevices"
        micropython -m mip install --no-mpy -t lib -i "$INDEX" \
            github:PyDevices/pydevices/board_configs/desktop \
            eventsys \
            palettes \
            pdwidgets
        micropython <<'PY'
import board_config
import board_peripherals
import eventsys
import palettes
import pdwidgets
print("board_config:", board_config.__file__)
print("eventsys:", eventsys.__file__)
print("from_board_config:", hasattr(eventsys.Runtime, "from_board_config"))
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
    log "append pydevices-examples env hook to $BASHRC"
    cat >>"$BASHRC" <<EOF

${BASHRC_BEGIN}
# Added by cloud-pydevices-examples-dev-env.sh — run examples from pydevices-examples/lib/
if [[ -f "${ENV_FILE}" ]]; then
    # shellcheck source=/dev/null
    source "${ENV_FILE}"
fi
${BASHRC_END}
EOF
}

ensure_pydevices_examples_venv
ensure_micropython_bin
mip_install_micropython_lib
install_bashrc_hook

log "done — cd ${EXAMPLES}/lib and run micropython/circuitpython/python examples"
