#!/bin/sh
# DEEPX dx-runtime one-line installer (runtime-only: NPU driver + dx_rt + firmware)
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/DEEPX-AI/dx-runtime/main/oneline-install.sh | sh
#
# Version selection:
#   Each component's version is read at run time from the `latest` symlink on its
#   own repo's main branch, so this script needs no manifest and no release assets.
#   Pin a specific component with:
#     DX_RT_VERSION=3.4.2      dx_rt (libdxrt-bin)
#     DX_DRIVER_VERSION=2.6.0  dx_rt_npu_linux_driver (DKMS)
#     DX_FW_VERSION=2.7.4      dx_fw — pins M1, M1M and H1 together; they are
#                              versioned as one firmware set, not individually
#
# NOTE: artifacts are served over HTTPS from raw.githubusercontent.com and are NOT
# checksum-verified — tracking a moving branch makes pinning a hash impossible.
# Transport trust (TLS + GitHub) is the only integrity guarantee here.
#
# NOTE: each component follows its own main branch independently. That is normally
# the same combination dx-runtime pins for a release, but between releases a sibling
# repo can move ahead, so a given run may install a combination that has not been
# validated together. Use the version overrides above, or the repo's install.sh, when
# you need a known-good set.
set -eu

RAW="https://raw.githubusercontent.com/DEEPX-AI"

log()  { printf '\033[1;34m[dx-runtime]\033[0m %s\n' "$1"; }
warn() { printf '\033[1;33m[dx-runtime][WARN]\033[0m %s\n' "$1"; }
die()  { printf '\033[1;31m[dx-runtime][ERROR]\033[0m %s\n' "$1" >&2; exit 1; }

# Read a `latest` symlink through raw.githubusercontent.com. raw does not traverse
# directory symlinks (release/latest/<file> is a 404) but it does serve the symlink
# blob itself, whose content is the target directory name — e.g. "3.4.2".
resolve_version() {
    _url="$1"; _label="$2"
    curl -fsSL "$_url" || die "cannot resolve latest ${_label} version from ${_url}"
}

# Every version string is spliced into a download URL, and it may come either from
# the repo (resolve_version) or from a DX_*_VERSION override the caller set. Validate
# both sources here so the override cannot skip the check. Versions are digits and
# dots only; ".." is rejected explicitly because it would otherwise pass that test
# while escaping the path (curl normalizes dot-segments client-side).
require_version() {
    case "$2" in
        ''|*..*|*[!0-9.]*) die "invalid ${1} version: ${2}" ;;
    esac
}

update_fw() {
    chip_id="$1"; chip_name="$2"; fw_bin="$3"
    if check_output="$(dxrt-cli "--check-${chip_id}" 2>&1)"; then
        log "Updating DX-${chip_name} firmware"
        # -g reads the image's version header and checks it against the device,
        # so a mismatched binary is rejected before -u writes anything to flash.
        dxrt-cli -g "$fw_bin" || die "DX-${chip_name} firmware version check failed"
        dxrt-cli -u "$fw_bin" || die "DX-${chip_name} firmware update failed"
        log "DX-${chip_name} firmware update completed"
    else
        warn "DX-${chip_name} check failed (dxrt-cli --check-${chip_id}): ${check_output}; skipping its firmware update"
    fi
}

main() {
    command -v curl >/dev/null 2>&1 || die "curl is required"
    command -v dpkg >/dev/null 2>&1 || die "Debian/Ubuntu (dpkg) is required"
    ARCH="$(dpkg --print-architecture)"
    case "$ARCH" in
        amd64|arm64) ;;
        *) die "unsupported architecture: $ARCH (amd64/arm64 only)" ;;
    esac

    SUDO=""
    if [ "$(id -u)" -ne 0 ]; then
        command -v sudo >/dev/null 2>&1 || die "run as root or install sudo"
        SUDO="sudo"
    fi

    # world-readable so apt's sandbox user _apt can read the staged debs
    WORK="$(mktemp -d)"
    chmod 755 "$WORK"
    # HUP included so a dropped terminal during a curl | sh still cleans up.
    trap 'rm -rf "$WORK"' EXIT INT TERM HUP

    log "Resolving component versions"
    DRIVER_VER="${DX_DRIVER_VERSION:-$(resolve_version "$RAW/dx_rt_npu_linux_driver/main/release/latest" "driver")}"
    RT_VER="${DX_RT_VERSION:-$(resolve_version "$RAW/dx_rt/main/release/latest" "dx_rt")}"
    FW_VER="${DX_FW_VERSION:-$(resolve_version "$RAW/dx_fw/main/m1/latest" "firmware")}"
    FW_M1M_VER="${DX_FW_VERSION:-$(resolve_version "$RAW/dx_fw/main/m1m/latest" "M1M firmware")}"
    require_version driver "$DRIVER_VER"
    require_version dx_rt "$RT_VER"
    require_version firmware "$FW_VER"
    require_version "M1M firmware" "$FW_M1M_VER"
    log "driver ${DRIVER_VER}, dx_rt ${RT_VER}, firmware ${FW_VER} (M1M ${FW_M1M_VER})"

    # The DKMS package carries a Debian revision that the version directory name does
    # not encode. It has been -2 for every release from 1.7.1 through 2.6.0; if that
    # ever changes the download 404s loudly rather than installing something wrong.
    DRIVER_URL="$RAW/dx_rt_npu_linux_driver/main/release/${DRIVER_VER}/dxrt-driver-dkms_${DRIVER_VER}-2_all.deb"
    RT_URL="$RAW/dx_rt/main/release/${RT_VER}/libdxrt-bin_${RT_VER}_${ARCH}.deb"

    log "Downloading NPU driver (${DRIVER_VER})"
    curl -fL "$DRIVER_URL" -o "$WORK/driver.deb" \
        || die "failed to download NPU driver: $DRIVER_URL (if the file is missing, the package's Debian revision may no longer be -2)"
    log "Downloading dx_rt (${RT_VER}, ${ARCH})"
    curl -fL "$RT_URL" -o "$WORK/dxrt.deb" \
        || die "failed to download dx_rt: $RT_URL"
    log "Downloading firmware (${FW_VER})"
    curl -fL "$RAW/dx_fw/main/m1/${FW_VER}/mdot2/fw.bin"      -o "$WORK/fw_m1.bin" \
        || die "failed to download M1 firmware ${FW_VER}"
    curl -fL "$RAW/dx_fw/main/m1m/${FW_M1M_VER}/mdot2/fw.bin" -o "$WORK/fw_m1m.bin" \
        || die "failed to download M1M firmware ${FW_M1M_VER}"
    curl -fL "$RAW/dx_fw/main/m1/${FW_VER}/h1/fw.bin"         -o "$WORK/fw_h1.bin" \
        || die "failed to download H1 firmware ${FW_VER}"
    chmod 644 "$WORK"/*.deb

    log "Installing NPU driver (DKMS package)"
    # Non-fatal: the debs are already downloaded and installed by path, so a
    # stale or unreachable index only matters for resolving their dependencies,
    # and apt reports that itself on the install line below.
    $SUDO apt-get update -qq || true
    $SUDO apt-get install -y "$WORK/driver.deb"
    log "Installing dx_rt (libdxrt-bin)"
    $SUDO apt-get install -y "$WORK/dxrt.deb"

    if command -v dxrt-cli >/dev/null 2>&1; then
        update_fw m1  M1  "$WORK/fw_m1.bin"
        update_fw m1m M1M "$WORK/fw_m1m.bin"
        update_fw h1  H1  "$WORK/fw_h1.bin"
    else
        warn "dxrt-cli not found on PATH; skipping firmware update"
    fi

    log "Installation complete."
    log "A reboot is required to load the NPU driver:  sudo reboot"
    log "If firmware update was skipped (device not detected), rerun this script after reboot."
}

main "$@"
