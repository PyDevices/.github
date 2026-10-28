# gallery path environment — source before running from gallery/lib/.
# Values match gallery README.md §3.2.1 and docs/utils.md (character-for-character).
#
#   cd gallery/lib
#   source ~/gh/pydevices/dotgithub/scripts/gallery-env.sh   # or this repo's path

_pydevices_examples_env_root() {
    if [[ -n "${PYDEVICES_EXAMPLES_ROOT:-}" && -d "${PYDEVICES_EXAMPLES_ROOT}/lib" ]]; then
        printf '%s' "$PYDEVICES_EXAMPLES_ROOT"
        return 0
    fi
    local repos="${PYDEVICES_REPOS_ROOT:-/agent/repos}"
    local candidate
    for candidate in \
        "$repos/gallery" \
        "${HOME}/gh/pydevices/gallery"; do
        if [[ -d "$candidate/lib" ]]; then
            printf '%s' "$candidate"
            return 0
        fi
    done
    return 1
}

if ! PYDEVICES_EXAMPLES_ROOT="$(_pydevices_examples_env_root)"; then
    echo "gallery-env: gallery checkout not found (set PYDEVICES_EXAMPLES_ROOT)" >&2
    return 1 2>/dev/null || exit 1
fi

export PATH="${PYDEVICES_EXAMPLES_ROOT}/bin:${PATH}"
PYDEVICES_PRODUCT_ROOT="$(cd "${PYDEVICES_EXAMPLES_ROOT}/../pydevices" 2>/dev/null && pwd || true)"
if [[ -n "$PYDEVICES_PRODUCT_ROOT" ]]; then
    export PYTHONPATH=".:utils:${PYDEVICES_PRODUCT_ROOT}/drivers/display:${PYDEVICES_PRODUCT_ROOT}/lib:${PYDEVICES_PRODUCT_ROOT}/utils"
    export MICROPYPATH=".:.frozen:utils:${PYDEVICES_PRODUCT_ROOT}/drivers/display:${PYDEVICES_PRODUCT_ROOT}/lib:${PYDEVICES_PRODUCT_ROOT}/utils:~/.micropython/lib:/usr/lib/micropython"
else
    export PYTHONPATH=.:utils
    export MICROPYPATH=.:.frozen:utils:~/.micropython/lib:/usr/lib/micropython
fi
unset PYDEVICES_PRODUCT_ROOT
