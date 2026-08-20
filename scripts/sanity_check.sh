#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
RUNTIME_PATH=$(realpath -s "${SCRIPT_DIR}/../") # repo root (parent of scripts/)
DRIVER_PATH="${RUNTIME_PATH}/dx_rt_npu_linux_driver"
DEBIAN_SANITY_SCRIPT="/usr/share/libdxrt-bin/SanityCheckForDebian.sh"

# load print_colored()
#   - usage: print_colored "message contents" "type"
#      - types: ERROR FAIL INFO WARNING DEBUG RED BLUE YELLOW GREEN
source "${RUNTIME_PATH}/scripts/color_env.sh"
source "${RUNTIME_PATH}/scripts/common_util.sh"

# Function to check and install required packages
check_and_install_package() {
    local pkg=$1
    local cmd=$2

    if ! command -v "$cmd" &> /dev/null; then
        print_colored "⚠️  $cmd command not found. Installing $pkg package..." "WARNING"
        sudo apt update
        sudo apt install -y "$pkg"
        if [ $? -eq 0 ]; then
            print_colored "✅ $pkg installed successfully." "GREEN"
        else
            print_colored "❌ Failed to install $pkg." "ERROR"
            exit 1
        fi
    else
        print_colored "✅ $cmd command is available ($pkg package is installed)." "INFO"
    fi
}

# dx_rt installed via Debian package (libdxrt-bin)?
# Legacy libdxrt is a source-build artifact, so it is not checked here.
is_dx_rt_debian_installed() {
    dpkg-query -W -f='${Status}' libdxrt-bin 2>/dev/null | grep -q "install ok installed"
}

print_sanity_result() {
    local status=$1
    local detail_hint=$2

    echo "---"
    print_colored "Sanity Check Result:" "INFO"

    if [[ $status -eq 0 ]]; then
        print_colored "✅ PASS: All sanity checks passed successfully." "GREEN"
    elif [[ $status -eq 1 ]]; then
        print_colored "❌ FAIL: One or more sanity checks failed." "FAIL"
        if [ -n "${detail_hint}" ]; then
            print_colored "${detail_hint}" "RED"
        fi
    elif [[ $status -eq 2 ]]; then
        print_colored "⚠️  ERROR: SanityCheck.sh was not run with sufficient permissions (e.g., as root)." "ERROR"
        print_colored "Please ensure you run this script with 'sudo'." "RED"
    else
        print_colored "❓ UNKNOWN: Sanity check exited with an unexpected status code: $status." "YELLOW"
    fi
}

run_debian_sanity_check() {
    echo "--- Debian package sanity check... ---"
    if [ ! -f "${DEBIAN_SANITY_SCRIPT}" ]; then
        print_colored "⚠️  ${DEBIAN_SANITY_SCRIPT} not found. Skipping Debian package sanity check." "WARNING"
        return 0
    fi
    bash "${DEBIAN_SANITY_SCRIPT}"
}

# Always use dx_rt_npu_linux_driver/sanity_check.sh for driver checks
# (same entrypoint as install.sh historically used).
run_driver_sanity_check() {
    echo "--- Driver sanity check... ---"
    if [ ! -f "${DRIVER_PATH}/sanity_check.sh" ]; then
        print_colored "⚠️  ${DRIVER_PATH}/sanity_check.sh not found. Skipping driver sanity check." "WARNING"
        return 0
    fi
    sudo "${DRIVER_PATH}/sanity_check.sh"
}

run_source_sanity_check() {
    local sanity_check_args=$1

    print_colored "Checking required packages for SanityCheck..." "INFO"
    check_and_install_package "kmod" "lsmod"
    check_and_install_package "pciutils" "lspci"
    check_and_install_package "dkms" "dkms"
    echo ""

    pushd "${RUNTIME_PATH}/dx_rt" > /dev/null || {
        print_colored "❌ ${RUNTIME_PATH}/dx_rt directory not found." "ERROR"
        return 1
    }

    echo "Attempting to run the DeepX SDK source-build sanity check..."
    echo "---"

    # Execute SanityCheck.sh and capture its exit status.
    # We use `sudo` here because SanityCheck.sh requires root privileges.
    # ${sanity_check_args} stays unquoted: empty must expand to zero args.
    sudo ./SanityCheck.sh ${sanity_check_args}
    local status=$?
    popd > /dev/null
    return $status
}

SANITY_CHECK_ARGS=""
# Parse command-line arguments
for i in "$@"; do
    case $i in
        --dx_driver)
            SANITY_CHECK_ARGS="dx_driver"
            shift # past argument=value
            ;;
        --dx_rt)
            SANITY_CHECK_ARGS="dx_rt"
            shift # past argument=value
            ;;
        *)
            print_colored "Unknown option: $i" "ERROR" >&2
            ;;
    esac
done

SANITY_STATUS=0

# --dx_driver: driver-only via dx_rt_npu_linux_driver/sanity_check.sh
# (debian vs source does not matter for the driver check itself).
if [ "${SANITY_CHECK_ARGS}" = "dx_driver" ]; then
    print_colored "Running driver sanity check (dx_rt_npu_linux_driver/sanity_check.sh)." "INFO"
    run_driver_sanity_check
    SANITY_STATUS=$?
    print_sanity_result "$SANITY_STATUS" "Please review the driver sanity check output for details."
    exit $SANITY_STATUS
fi

if is_dx_rt_debian_installed; then
    print_colored "Detected dx_rt Debian package (libdxrt-bin). Using SanityCheckForDebian.sh." "INFO"

    # The no-option case originally covered driver + rt, so run the driver
    # sanity check alongside the Debian RT package check.
    # --dx_rt alone skips the driver check.
    if [ "${SANITY_CHECK_ARGS}" != "dx_rt" ]; then
        run_driver_sanity_check
        SANITY_STATUS=$?
    fi

    if [ $SANITY_STATUS -eq 0 ]; then
        run_debian_sanity_check
        SANITY_STATUS=$?
    fi

    print_sanity_result "$SANITY_STATUS" "Please review the Debian / driver sanity check output for details."
else
    print_colored "dx_rt Debian package not detected. Using source-build SanityCheck.sh." "INFO"
    run_source_sanity_check "${SANITY_CHECK_ARGS}"
    SANITY_STATUS=$?
    print_sanity_result "$SANITY_STATUS" "Please review the logs generated by SanityCheck.sh for details."
fi

exit $SANITY_STATUS
