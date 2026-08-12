# pydisplay path environment — source before running from pydisplay/src/.
# Values match pydisplay README.md §3.2.1 and docs/utils.md (character-for-character).
#
#   cd pydisplay/src
#   source ~/gh/pydevices/dotgithub/scripts/pydisplay-env.sh   # or this repo's path

_pydisplay_env_root() {
    if [[ -n "${PYDISPLAY_ROOT:-}" && -d "${PYDISPLAY_ROOT}/src" ]]; then
        printf '%s' "$PYDISPLAY_ROOT"
        return 0
    fi
    local repos="${PYDEVICES_REPOS_ROOT:-/agent/repos}"
    local candidate
    for candidate in \
        "$repos/pydisplay" \
        "${HOME}/gh/pydevices/pydisplay"; do
        if [[ -d "$candidate/src" ]]; then
            printf '%s' "$candidate"
            return 0
        fi
    done
    return 1
}

if ! PYDISPLAY_ROOT="$(_pydisplay_env_root)"; then
    echo "pydisplay-env: pydisplay checkout not found (set PYDISPLAY_ROOT)" >&2
    return 1 2>/dev/null || exit 1
fi

export PATH="${PYDISPLAY_ROOT}/bin:${PATH}"
PYDEVICES_HARDWARE_ROOT="$(cd "${PYDISPLAY_ROOT}/../micropython-hardware" 2>/dev/null && pwd || true)"
if [[ -n "$PYDEVICES_HARDWARE_ROOT" ]]; then
    export PYTHONPATH=".:utils:${PYDEVICES_HARDWARE_ROOT}/drivers/display:${PYDEVICES_HARDWARE_ROOT}/lib:${PYDEVICES_HARDWARE_ROOT}/utils"
    export MICROPYPATH=".:.frozen:utils:${PYDEVICES_HARDWARE_ROOT}/drivers/display:${PYDEVICES_HARDWARE_ROOT}/lib:${PYDEVICES_HARDWARE_ROOT}/utils:~/.micropython/lib:/usr/lib/micropython"
else
    export PYTHONPATH=.:utils
    export MICROPYPATH=.:.frozen:utils:~/.micropython/lib:/usr/lib/micropython
fi
unset PYDEVICES_HARDWARE_ROOT
