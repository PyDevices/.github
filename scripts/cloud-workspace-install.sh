#!/usr/bin/env bash
# Idempotent PyDevices cloud workspace layout: ~/gh/pydevices symlinks into /agent/repos.
# See AGENTS.md. Safe to run on every cloud VM boot (environment.json install).
#
# Self-heals when Cursor did not materialize sibling checkouts under /agent/repos
# (common for repo-file environments: repositoryDependencies expands the GitHub
# token scope but does not always clone those repos). Missing siblings are
# shallow-cloned here so agents can start real work without a setup chat.
set -euo pipefail

GH="${PYDEVICES_GH_ROOT:-/home/ubuntu/gh}"
PD="$GH/pydevices"
REPOS="${PYDEVICES_REPOS_ROOT:-/agent/repos}"
ORG="${PYDEVICES_GITHUB_ORG:-PyDevices}"

# Sibling checkouts expected under $REPOS (names match GitHub repo names).
SIBLINGS=(
    cmods
    displayif
    graphics
    lv_bindings
    lv_circuitpython_mod
    lv_cpython_mod
    lv_micropython_cmod
    palettes
    pdwidgets
    pydisplay
    pydisplay_android
    PyDevices.github.io
    usdl2
)

log() { printf 'cloud-workspace-install: %s\n' "$*"; }

die() {
    log "ERROR: $*"
    exit 1
}

mkdir -p "$PD"

# --- /agent/repos bootstrap ---------------------------------------------------

ensure_repos_root() {
    if [[ -d "$REPOS" ]]; then
        return 0
    fi
    if mkdir -p "$REPOS" 2>/dev/null; then
        log "created $REPOS"
        return 0
    fi
    if command -v sudo >/dev/null 2>&1; then
        sudo mkdir -p "$REPOS"
        sudo chown "$(id -u):$(id -g)" "$REPOS"
        log "created $REPOS (via sudo)"
        return 0
    fi
    die "cannot create $REPOS"
}

# Link this .github checkout into $REPOS/.github when Cursor only mounted it
# at /workspace (or wherever this script lives).
ensure_dotgithub() {
    local path="$REPOS/.github"
    if [[ -L "$path" || -d "$path/.git" ]]; then
        return 0
    fi
    if [[ -e "$path" ]]; then
        log "skip $path (exists, not a git checkout or symlink)"
        return 0
    fi

    local src
    src="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    if [[ ! -f "$src/AGENTS.md" || ! -d "$src/.cursor" ]]; then
        if [[ -f /workspace/AGENTS.md && -d /workspace/.cursor ]]; then
            src=/workspace
        else
            log "warn: cannot locate .github checkout to link at $path"
            return 0
        fi
    fi
    log "link $path -> $src"
    ln -s "$src" "$path"
}

clone_missing_siblings() {
    local name path url
    local -a pids=()
    local -a names=()

    for name in "${SIBLINGS[@]}"; do
        path="$REPOS/$name"
        if [[ -d "$path/.git" || -L "$path" ]]; then
            continue
        fi
        if [[ -e "$path" ]]; then
            log "skip $path (exists, not a git checkout)"
            continue
        fi
        url="https://github.com/${ORG}/${name}.git"
        log "clone $url -> $path"
        git clone --depth 1 --filter=blob:none "$url" "$path" &
        pids+=("$!")
        names+=("$name")
    done

    if ((${#pids[@]} == 0)); then
        return 0
    fi

    local i ec=0
    for i in "${!pids[@]}"; do
        if ! wait "${pids[$i]}"; then
            log "clone failed: ${names[$i]}"
            ec=1
        fi
    done
    return "$ec"
}

# --- symlink helpers ----------------------------------------------------------

link_pydevices() {
    local name=$1
    local target=$2
    local path="$PD/$name"
    if [[ -L "$path" ]]; then
        return 0
    fi
    if [[ -e "$path" ]]; then
        log "skip $path (exists, not a symlink)"
        return 0
    fi
    if [[ ! -e "$target" ]]; then
        log "skip $path (target missing: $target)"
        return 0
    fi
    log "link $path -> $target"
    ln -s "$target" "$path"
}

link_cmods_sibling() {
    local name=$1
    local path="$PD/cmods/$name"
    if [[ -L "$path" ]]; then
        return 0
    fi
    if [[ -e "$path" ]]; then
        log "skip $path (exists, not a symlink)"
        return 0
    fi
    log "link $path -> $REPOS/$name"
    ln -s "$REPOS/$name" "$path"
}

shallow_clone_if_missing() {
    local dir=$1 url=$2 branch=$3
    local path="$PD/cmods/$dir"
    if [[ -d "$path/.git" ]]; then
        log "present: cmods/$dir"
        return 0
    fi
    if [[ -e "$path" ]]; then
        log "skip cmods/$dir (path exists but is not a git checkout)"
        return 0
    fi
    log "clone $url @ $branch -> cmods/$dir"
    git clone --depth 1 --filter=blob:none --branch "$branch" --single-branch \
        "$url" "$path"
}

# Uninitialized submodule checkout: empty dir or gitlink stub without sources.
is_empty_lvgl_placeholder() {
    local d=$1
    [[ -d "$d" && ! -L "$d" ]] || return 1
    [[ ! -e "$d/src" && ! -e "$d/lvgl.h" ]]
}

ensure_lv_cpython_lvgl_symlink() {
    local lvcp_lvgl="$PD/cmods/lv_cpython_mod/lvgl"
    [[ -d "$PD/cmods/lv_cpython_mod" ]] || return 0

    if [[ -L "$lvcp_lvgl" ]]; then
        return 0
    fi
    if is_empty_lvgl_placeholder "$lvcp_lvgl"; then
        log "replace empty $lvcp_lvgl with symlink -> ../lv_bindings/lvgl"
        rm -rf "$lvcp_lvgl"
        ln -s ../lv_bindings/lvgl "$lvcp_lvgl"
        return 0
    fi
    if [[ -e "$lvcp_lvgl" ]]; then
        log "skip $lvcp_lvgl (exists, not a symlink — remove manually to relink)"
        return 0
    fi
    log "link $lvcp_lvgl -> ../lv_bindings/lvgl"
    ln -s ../lv_bindings/lvgl "$lvcp_lvgl"
}

verify_ready() {
    local name missing=0
    for name in cmods displayif graphics lv_bindings pydisplay palettes pdwidgets; do
        if [[ ! -d "$REPOS/$name/.git" && ! -L "$REPOS/$name" ]]; then
            log "ERROR: required repo missing: $REPOS/$name"
            missing=1
        fi
    done
    if [[ ! -e "$REPOS/displayif/HANDOFF.md" && ! -e "$REPOS/displayif/handoff.md" ]]; then
        log "ERROR: displayif handoff doc missing under $REPOS/displayif"
        missing=1
    fi
    if [[ ! -d "$PD/cmods/micropython/.git" ]]; then
        log "ERROR: cmods/micropython shallow clone missing"
        missing=1
    fi
    if [[ ! -e "$PD/cmods/lv_bindings/lvgl/src" && ! -e "$REPOS/lv_bindings/lvgl/src" ]]; then
        log "ERROR: lv_bindings/lvgl submodule not initialized"
        missing=1
    fi
    if [[ ! -L "$PD/cmods/lv_cpython_mod/lvgl" ]]; then
        log "ERROR: lv_cpython_mod/lvgl is not a symlink to lv_bindings/lvgl"
        missing=1
    fi
    return "$missing"
}

# --- main ---------------------------------------------------------------------

ensure_repos_root
ensure_dotgithub
clone_missing_siblings || die "one or more sibling clones failed"

link_pydevices cmods "$REPOS/cmods"
link_pydevices dotgithub "$REPOS/.github"
link_pydevices PyDevices.github.io "$REPOS/PyDevices.github.io"
link_pydevices palettes "$REPOS/palettes"
link_pydevices pdwidgets "$REPOS/pdwidgets"
link_pydevices pydisplay "$REPOS/pydisplay"
link_pydevices pydisplay_android "$REPOS/pydisplay_android"

# cmods must exist before interior sibling links
[[ -d "$PD/cmods" ]] || die "cmods missing after link step ($PD/cmods)"

for s in displayif graphics lv_bindings lv_circuitpython_mod lv_cpython_mod \
    lv_micropython_cmod usdl2; do
    [[ -d "$REPOS/$s" || -L "$REPOS/$s" ]] && link_cmods_sibling "$s"
done

MP_TAG="${PYDEVICES_MP_TAG:-v1.28.0}"
CP_TAG="${PYDEVICES_CP_TAG:-10.2.1}"
shallow_clone_if_missing micropython https://github.com/micropython/micropython.git "$MP_TAG"
shallow_clone_if_missing circuitpython https://github.com/adafruit/circuitpython.git "$CP_TAG"

if [[ -d "$PD/cmods/lv_bindings/.git" ]]; then
    log "init lv_bindings/lvgl submodule"
    git -C "$PD/cmods/lv_bindings" submodule update --init --depth 1 lvgl
fi

ensure_lv_cpython_lvgl_symlink

verify_ready || die "workspace verification failed — agents cannot start real work yet"

log "done (workspace root: $PD)"
