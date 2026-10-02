#!/bin/sh
# DEEPX dx-runtime one-line uninstaller (runtime-only: NPU driver + dx_rt)
#
# Removes what oneline-install.sh installed, without needing a clone:
#   curl -fsSL https://raw.githubusercontent.com/DEEPX-AI/dx-runtime/main/oneline-uninstall.sh | sh
#
# Both install routes — this one and the repository's install.sh — end up with
# the same Debian packages, so this removes either. The repository's
# uninstall.sh does the same thing, but reaches dpkg through
# dx_rt_npu_linux_driver/modules/build.sh and therefore needs the submodule
# checked out; this script is for the case where there is no clone.
#
# Not covered: dx_app and dx_stream, which oneline-install.sh never installs —
# use the repository's uninstall.sh for those.
set -eu

# dxrt-driver-dkms: the NPU kernel driver. libdxrt-bin: the runtime; libdxrt is
# its legacy source-built package name, purged too so an upgraded host is clean.
PACKAGES="dxrt-driver-dkms libdxrt-bin libdxrt"

log()  { printf '\033[1;34m[dx-runtime]\033[0m %s\n' "$1"; }
warn() { printf '\033[1;33m[dx-runtime][WARN]\033[0m %s\n' "$1" >&2; }
die()  { printf '\033[1;31m[dx-runtime][ERROR]\033[0m %s\n' "$1" >&2; exit 1; }

main() {
    command -v dpkg >/dev/null 2>&1 || die "Debian/Ubuntu (dpkg) is required"

    SUDO=""
    if [ "$(id -u)" -ne 0 ]; then
        command -v sudo >/dev/null 2>&1 \
            || die "need root to remove system packages. Run as root, or: apt-get purge -y $PACKAGES"
        SUDO="sudo"
    fi

    REMOVED=""
    for pkg in $PACKAGES; do
        # Only touch packages that are actually installed, so a host that never
        # had one of them sees nothing about it.
        if dpkg-query -W -f='${Status}' "$pkg" 2>/dev/null | grep -q "install ok installed"; then
            log "Removing $pkg"
            $SUDO apt-get purge -y "$pkg" || die "failed to remove $pkg"
            REMOVED="$REMOVED $pkg"
        fi
    done

    if [ -z "$REMOVED" ]; then
        log "Nothing to remove: none of [$PACKAGES] is installed"
        return 0
    fi

    log "Removed:$REMOVED"
    log "A reboot is required to unload the NPU driver still resident in the kernel:  sudo reboot"
    warn "Firmware already flashed to the device is NOT reverted — no uninstall path exists for it."
    # libdxrt-bin's own postrm explains this in detail, including the venv case;
    # point at it rather than restating it and risking the two drifting apart.
    warn "The dx_engine Python wheel is user-managed and was left installed — see libdxrt-bin's removal notice above."
    warn "dx_app and dx_stream are untouched; use the repository's uninstall.sh if you installed those."
}

main "$@"
