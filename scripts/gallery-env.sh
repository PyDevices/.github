# gallery path environment — source before running from gallery/lib/.
# Values match gallery README.md §3.2.1 and docs/utils.md (character-for-character).
#
#   cd gallery/lib
#   source ~/gh/omnipython/dotgithub/scripts/gallery-env.sh   # or this repo's path

_omnipython_examples_env_root() {
    if [[ -n "${OMNIPYTHON_EXAMPLES_ROOT:-}" && -d "${OMNIPYTHON_EXAMPLES_ROOT}/lib" ]]; then
        printf '%s' "$OMNIPYTHON_EXAMPLES_ROOT"
        return 0
    fi
    local repos="${OMNIPYTHON_REPOS_ROOT:-/agent/repos}"
    local candidate
    for candidate in \
        "$repos/gallery" \
        "${HOME}/gh/omnipython/gallery"; do
        if [[ -d "$candidate/lib" ]]; then
            printf '%s' "$candidate"
            return 0
        fi
    done
    return 1
}

if ! OMNIPYTHON_EXAMPLES_ROOT="$(_omnipython_examples_env_root)"; then
    echo "gallery-env: gallery checkout not found (set OMNIPYTHON_EXAMPLES_ROOT)" >&2
    return 1 2>/dev/null || exit 1
fi

export PATH="${OMNIPYTHON_EXAMPLES_ROOT}/bin:${PATH}"
OMNIPYTHON_PRODUCT_ROOT="$(cd "${OMNIPYTHON_EXAMPLES_ROOT}/../omnipython" 2>/dev/null && pwd || true)"
if [[ -n "$OMNIPYTHON_PRODUCT_ROOT" ]]; then
    export PYTHONPATH=".:utils:${OMNIPYTHON_PRODUCT_ROOT}/drivers/display:${OMNIPYTHON_PRODUCT_ROOT}/lib:${OMNIPYTHON_PRODUCT_ROOT}/utils"
    export MICROPYPATH=".:.frozen:utils:${OMNIPYTHON_PRODUCT_ROOT}/drivers/display:${OMNIPYTHON_PRODUCT_ROOT}/lib:${OMNIPYTHON_PRODUCT_ROOT}/utils:~/.micropython/lib:/usr/lib/micropython"
else
    export PYTHONPATH=.:utils
    export MICROPYPATH=.:.frozen:utils:~/.micropython/lib:/usr/lib/micropython
fi
unset OMNIPYTHON_PRODUCT_ROOT
