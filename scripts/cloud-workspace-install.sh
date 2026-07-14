#!/usr/bin/env bash
# Idempotent PyDevices cloud workspace layout: ~/gh/pydevices symlinks into /agent/repos.
# See AGENTS.md. Safe to run on every cloud VM boot (environment.json install).
set -euo pipefail

GH="${PYDEVICES_GH_ROOT:-/home/ubuntu/gh}"
PD="$GH/pydevices"
REPOS="${PYDEVICES_REPOS_ROOT:-/agent/repos}"

log() { printf 'cloud-workspace-install: %s\n' "$*"; }

mkdir -p "$PD"

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

[[ -d "$REPOS" ]] || {
    log "missing $REPOS — multi-repo cloud clone not ready yet"
    exit 0
}

link_pydevices cmods "$REPOS/cmods"
link_pydevices dotgithub "$REPOS/.github"
link_pydevices PyDevices.github.io "$REPOS/PyDevices.github.io"
link_pydevices pydisplay "$REPOS/pydisplay"
link_pydevices pydisplay_android "$REPOS/pydisplay_android"

for s in displayif graphics lv_bindings lv_circuitpython_mod lv_cpython_mod \
    lv_micropython_cmod usdl2; do
    [[ -d "$REPOS/$s" ]] && link_cmods_sibling "$s"
done

MP_TAG="${PYDEVICES_MP_TAG:-v1.28.0}"
CP_TAG="${PYDEVICES_CP_TAG:-10.2.1}"
shallow_clone_if_missing micropython https://github.com/micropython/micropython.git "$MP_TAG"
shallow_clone_if_missing circuitpython https://github.com/adafruit/circuitpython.git "$CP_TAG"

if [[ -d "$PD/cmods/lv_bindings/.git" ]]; then
    log "init lv_bindings/lvgl submodule"
    git -C "$PD/cmods/lv_bindings" submodule update --init --depth 1 lvgl
fi

lvcp_lvgl="$PD/cmods/lv_cpython_mod/lvgl"
if [[ -d "$PD/cmods/lv_cpython_mod" ]]; then
    if [[ -L "$lvcp_lvgl" ]]; then
        : ok
    elif [[ -e "$lvcp_lvgl" ]]; then
        log "skip $lvcp_lvgl (exists, not a symlink — remove manually to relink)"
    else
        log "link $lvcp_lvgl -> ../lv_bindings/lvgl"
        ln -s ../lv_bindings/lvgl "$lvcp_lvgl"
    fi
fi

log "done (workspace root: $PD)"
