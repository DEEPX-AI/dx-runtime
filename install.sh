#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
PROJECT_ROOT=$(realpath "$SCRIPT_DIR")
RUNTIME_PATH=$(realpath -s "${SCRIPT_DIR}")
RT_PATH="${RUNTIME_PATH}/dx_rt"
DRIVER_PATH="${SCRIPT_DIR}/dx_rt_npu_linux_driver"

# Default VENV_PATH, can be overridden by --venv_path option
VENV_PATH_DEFAULT="${RUNTIME_PATH}/venv-dx-runtime"
VENV_PATH="${VENV_PATH_DEFAULT}" # Initialize with default

ENABLE_DEBUG_LOGS=0

# Global variables for script configuration
MIN_PY_VERSION="3.8.10"

# color env settings
source ${PROJECT_ROOT}/scripts/color_env.sh
source ${PROJECT_ROOT}/scripts/common_util.sh

show_help() {
    echo -e "Usage: ${COLOR_CYAN}$(basename "$0") [OPTIONS]${COLOR_RESET}"
    echo -e ""
    echo -e "Options:"
    echo -e "  ${COLOR_GREEN}--all${COLOR_RESET}                              Install all dx-runtime modules"
    echo -e "  ${COLOR_GREEN}--target=<module_name>${COLOR_RESET}             Install specify target dx-runtime module"
    echo -e "                                     (ex> dx_fw | dx_rt_npu_linux_driver | dx_rt | dx_app | dx_stream)"
    echo -e ""
    echo -e "  ${COLOR_GREEN}[--skip-uninstall]${COLOR_RESET}                 Skip uninstall dx-runtime modules before installation"
    echo -e "  ${COLOR_GREEN}[--driver-source-build]${COLOR_RESET}            Build NPU driver from source if set (default: install via DKMS)"
    echo -e ""
    echo -e "  ${COLOR_GREEN}[--exclude-fw]${COLOR_RESET}                     Install all dx-runtime modules except dx_fw"
    echo -e "  ${COLOR_GREEN}[--exclude-driver]${COLOR_RESET}                 Install all dx-runtime modules except dx_rt_npu_linux_driver"
    echo -e ""
    echo -e "  ${COLOR_GREEN}[--use-ort=<y|n>]${COLOR_RESET}                  Set 'USE_ORT' build option to 'ON or OFF' (default: y)"
    echo -e "  ${COLOR_GREEN}[--sanity-check=<y|n>]${COLOR_RESET}             Turn SanityCheck ON or OFF for dx_rt (default: y)"
    echo -e ""
    echo -e "  ${COLOR_GREEN}[-v|--verbose]${COLOR_RESET}                     Enable verbose (debug) logging"
    echo -e "  ${COLOR_GREEN}[-h|--help]${COLOR_RESET}                        Display this help message and exit"
    echo -e ""
    echo -e "${COLOR_BRIGHT_RED_ON_BLACK}** Virtual Environment options are applied only when --skip-uninstall is set **${COLOR_RESET}"
    echo -e "Virtual Environment Options:"
    echo -e "  ${COLOR_GREEN}[--venv_path=<PATH>]${COLOR_RESET}               Specify the path for the virtual environment"
    echo -e "                                     (Default: ${VENV_PATH_DEFAULT})"
    echo -e "Virtual Environment Sub-Options:"
    echo -e "  ${COLOR_GREEN}  [-f | --venv-force-remove]${COLOR_RESET}         (Default ON) Force remove existing virtual environment at --venv_path before creation"
    echo -e "  ${COLOR_GREEN}  [-r | --venv-reuse]${COLOR_RESET}                (Default OFF) Reuse existing virtual environment at --venv_path if it's valid, skipping creation"
    echo -e ""
    echo -e "${COLOR_BOLD}Examples:${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --all${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --all --exclude-fw --exclude-driver${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --target=dx_rt_npu_linux_driver${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --target=dx_app --skip-uninstall --venv-reuse${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --target=dx_rt --skip-uninstall --venv_path=/opt/my_runtime_venv --venv-force-remove${COLOR_RESET}"
    echo -e ""

    if [ "$1" == "error" ] && [[ ! -n "$2" ]]; then
        print_colored_v2 "ERROR" "Invalid or missing arguments."
        exit 1
    elif [ "$1" == "error" ] && [[ -n "$2" ]]; then
        print_colored_v2 "ERROR" "$2"
        exit 1
    elif [[ "$1" == "warn" ]] && [[ -n "$2" ]]; then
        print_colored_v2 "WARNING" "$2"
        return 0
    fi
    exit 0
}

install_dx_rt_npu_linux_driver() {
    # DX_RT_DRIVER_INCLUDED=1

    print_colored_v2 "INFO" "Installing dx_rt_npu_linux_driver..."
    pushd "${DRIVER_PATH}"
    ./install.sh --skip-reboot || { print_colored_v2 "ERROR" "dx_rt_npu_linux_driver install failed. Exiting."; exit 1; }
    popd
    print_colored_v2 "SUCCESS" "Installing dx_rt_npu_linux_driver completed."
}

set_use_ort() {
    pushd "${RUNTIME_PATH}/dx_rt"
    CMAKE_FILE="cmake/dxrt.cfg.cmake"

    if [ "${USE_ORT}" = "y" ]; then
        sed -i 's/option(USE_ORT *"Use ONNX Runtime" *OFF)/option(USE_ORT "Use ONNX Runtime" ON)/' "$CMAKE_FILE"
        print_colored "USE_ORT option has been set to ON in dx_rt/$CMAKE_FILE" "INFO"
    else
        sed -i 's/option(USE_ORT *"Use ONNX Runtime" *ON)/option(USE_ORT "Use ONNX Runtime" OFF)/' "$CMAKE_FILE"
        print_colored "USE_ORT option is set to '${USE_ORT}'. so, USE_ORT option has been set to OFF in dx_rt/$CMAKE_FILE" "INFO"
    fi 

    popd
}

sanity_check() {
    echo "--- sanity check... ---"
    local sanity_check_option="$1"

    if [ "${USE_SANITY_CHECK}" = "y" ]; then
        ${RUNTIME_PATH}/scripts/sanity_check.sh ${sanity_check_option}
        if [ $? -ne 0 ]; then
            print_colored "Sanity Check failed. Exiting." "ERROR"
            exit 1
        fi
    else
        print_colored "Skipped to Sanity Check..." "WARNING"
    fi
}

uninstall_dx_rt() {
    if [ "${SKIP_UNINSTALL}" = "y" ]; then
        print_colored_v2 "SKIP" "Skipping uninstall of dx-rt..."
        return
    fi

    print_colored_v2 "INFO" "Uninstalling dx_rt..."
    pushd "${RUNTIME_PATH}/dx_rt"
    if [ -f "uninstall.sh" ]; then
        ./uninstall.sh || { print_colored_v2 "ERROR" "dx_rt uninstall failed. Exiting."; exit 1; }
    else
        print_colored_v2 "SKIP" "dx_rt uninstall.sh not found. Skipping..."
    fi
    popd
    print_colored_v2 "SUCCESS" "Uninstalling dx_rt completed."
}

install_dx_rt() {
    print_colored_v2 "INFO" "=== Installing dx_rt... ==="
    uninstall_dx_rt

    DX_RT_INCLUDED=1
    set_use_ort

    . "${VENV_PATH}/bin/activate" || { print_colored_v2 "ERROR" "venv(${VENV_PATH}) activation failed. Exiting."; exit 1; }

    pushd "$SCRIPT_DIR/dx_rt"
    if [ "${USE_ORT}" = "y" ]; then
        ./install.sh --all
    else
        ./install.sh --dep
    fi || { print_colored_v2 "ERROR" "dx_rt install failed. Exiting."; exit 1; }
    
    ./build.sh --clean || { print_colored_v2 "ERROR" "dx_rt install failed. Exiting."; exit 1; }
    popd
    print_colored_v2 "SUCCESS" "Installing dx_rt completed."
}

install_dx_rt_python_api() {
    print_colored_v2 "INFO" "=== Setup 'dx_engine' Python API... ==="

    pushd "${RT_PATH}/python_package"
    pip install . || { print_colored_v2 "ERROR" "'dx_engine' Python API setup failed. Exiting."; exit 1; }
    popd
    print_colored_v2 "INFO" "[OK] Setup 'dx_engine' Python API"
}

uninstall_dx_app() {
    if [ "${SKIP_UNINSTALL}" = "y" ]; then
        print_colored_v2 "SKIP" "Skipping uninstall of dx-app..."
        return
    fi
    
    print_colored_v2 "INFO" "Uninstalling dx_app..."
    pushd "${RUNTIME_PATH}/dx_app"
    if [ -f "uninstall.sh" ]; then
        ./uninstall.sh || { print_colored_v2 "ERROR" "dx_app uninstall failed. Exiting."; exit 1; }
    else
        print_colored_v2 "SKIP" "dx_app uninstall.sh not found. Skipping..."
    fi
    popd
    print_colored_v2 "SUCCESS" "Uninstalling dx_app completed."
}

install_dx_app() {
    print_colored_v2 "INFO" "=== Installing dx_app... ==="
    uninstall_dx_app

    DX_APP_INCLUDED=1

    pushd "$SCRIPT_DIR/dx_app"
    ./install.sh --all || { print_colored_v2 "ERROR" "dx_app install failed. Exiting."; exit 1; }
    ./build.sh --clean || { print_colored_v2 "ERROR" "dx_app build failed. Exiting."; exit 1; } 
    popd
    print_colored_v2 "SUCCESS" "Installing dx_app completed."
}

uninstall_dx_stream() {
    if [ "${SKIP_UNINSTALL}" = "y" ]; then
        print_colored_v2 "SKIP" "Skipping uninstall of dx-stream..."
        return
    fi
    
    print_colored_v2 "INFO" "Uninstalling dx_stream..."
    pushd "${RUNTIME_PATH}/dx_stream"
    if [ -f "uninstall.sh" ]; then
        ./uninstall.sh || { print_colored_v2 "ERROR" "dx_stream uninstall failed. Exiting."; exit 1; }
    else
        print_colored_v2 "SKIP" "dx_stream uninstall.sh not found. Skipping..."
    fi
    popd
    print_colored_v2 "SUCCESS" "Uninstalling dx_stream completed."
}

install_dx_stream() {
    print_colored_v2 "INFO" "=== Installing dx_stream... ==="

    uninstall_dx_stream

    pushd "$SCRIPT_DIR/dx_stream"
    ./install.sh || { print_colored_v2 "ERROR" "dx_stream install failed. Exiting."; exit 1; }
    ./build.sh --install || { print_colored_v2 "ERROR" "dx_stream build failed. Exiting."; exit 1; }
    # gst-inspect-1.0 dxstream
    popd
    print_colored_v2 "SUCCESS" "Installing dx_stream completed."
}

install_dx_fw() {
    print_colored_v2 "INFO" "=== Installing dx_fw... ==="
    if [ "${EXCLUDE_FW}" = "y" ]; then
        print_colored_v2 "WARNING" "Excluding firmware update."
        return
    fi

    if [ ! -f "$SCRIPT_DIR/dx_fw/m1/latest/mdot2/fw.bin" ]; then
        print_colored_v2 "ERROR" "firmware file not found!"
        exit 1
    fi

    if ! command -v dxrt-cli &> /dev/null; then
        print_colored_v2 "ERROR" "'dxrt-cli' not found!"
        exit 1
    fi

    dxrt-cli -g "$SCRIPT_DIR/dx_fw/m1/latest/mdot2/fw.bin" || { print_colored_v2 "ERROR" "dx_fw download failed. Exiting."; exit 1; }
    dxrt-cli -u "$SCRIPT_DIR/dx_fw/m1/latest/mdot2/fw.bin" || { print_colored_v2 "ERROR" "dx_fw update failed. Exiting."; exit 1; } 
    print_colored_v2 "HINT" "It is recommended to power off completely and reboot after the firmware update."
    print_colored_v2 "SUCCESS" "Installing dx_fw completed."
}

install_python_and_venv() {
    print_colored_v2 "INFO" "=== install python... ==="

    local INSTALL_PY_CMD_ARGS=""

    if [ -n "$VENV_PATH" ]; then
        INSTALL_PY_CMD_ARGS+=" --venv_path=$VENV_PATH"
    fi
    
    if [ "${VENV_FORCE_REMOVE}" = "y" ]; then
        INSTALL_PY_CMD_ARGS+=" --venv-force-remove"
    fi

    if [ "${VENV_REUSE}" = "y" ]; then
        INSTALL_PY_CMD_ARGS+=" --venv-reuse"
    fi

    # Pass the determined VENV_PATH and new options to install_python_and_venv.sh
    INSTALL_PY_CMD="${RUNTIME_PATH}/scripts/install_python_and_venv.sh ${INSTALL_PY_CMD_ARGS}"
    echo "CMD: ${INSTALL_PY_CMD}"
    ${INSTALL_PY_CMD}
    if [ $? -ne 0 ]; then
        print_colored "Python and Virtual environment setup failed. Exiting." "ERROR"
        exit 1
    fi

    print_colored_v2 "INFO" "[OK] Completed to install python" "INFO"
    print_colored_v2 "SUCCESS" "Installing python completed."
}

# host_reboot() {
#     print_colored "The 'dx_rt_npu_linux_driver' has been installed." "INFO"
#     print_colored "To complete the installation, the system must be restarted."
#     echo -e -n "${COLOR_BRIGHT_GREEN_ON_BLACK}  Would you like to reboot now? (y/n): ${COLOR_RESET}"
#     read -r answer
#     if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
#         echo "Start reboot..."
#         sudo reboot now
#     fi
# }

uninstall_all_runtime_modules() {
    if [ "${SKIP_UNINSTALL}" = "y" ]; then
        print_colored_v2 "SKIP" "Skipping uninstall of dx-runtime..."
        return
    fi

    print_colored_v2 "INFO" "=== Uninstalling all runtime modules... ==="
    pushd "${RUNTIME_PATH}"
    ./uninstall.sh || { print_colored_v2 "ERROR" "dx-runtime uninstall failed. Exiting."; exit 1; }
    popd
    print_colored_v2 "SUCCESS" "Uninstalling all runtime modules completed."
}

venv_activate() {
    print_colored_v2 "INFO" "venv activate..."
    local venv_path="$1"

    if [ -z "$venv_path" ]; then
        print_colored_v2 "ERROR" "VENV_PATH is not set. Exiting."
        exit 1
    fi

    if [ ! -d "$venv_path" ] || [ ! -f "$venv_path/bin/activate" ]; then
        print_colored_v2 "ERROR" "Virtual environment at '$venv_path' does not exist or is invalid. Please create it first."
        exit 1
    fi

    # Activate the virtual environment
    . "$venv_path/bin/activate" || { print_colored_v2 "ERROR" "Failed to activate virtual environment at '$venv_path'. Exiting."; exit 1; }
    print_colored_v2 "SUCCESS" "Virtual environment at '$venv_path' is activated."
}

show_information_message() {
    if [[ ${DX_RT_INCLUDED} -eq 1 || ${DX_APP_INCLUDED} -eq 1 ]]; then
        print_colored "To activate the virtual environment, run:" "HINT"
        print_colored "  source ${VENV_PATH}/bin/activate " "HINT"
    fi

    # if [ ${DX_RT_DRIVER_INCLUDED} -eq 1 ]; then
    #     host_reboot
    # fi
}

main() {
    # this function is defined in scripts/common_util.sh
    # Usage: os_check "supported_os_names" "ubuntu_versions" "debian_versions"
    os_check "ubuntu debian" "18.04 20.04 22.04 24.04" "12"

    # this function is defined in scripts/common_util.sh
    # Usage: arch_check "supported_arch_names"
    arch_check "amd64 x86_64 arm64 aarch64 armv7l"

    install_python_and_venv
    venv_activate "$VENV_PATH"

    case $TARGET_PKG in
        dx_rt_npu_linux_driver)
            print_colored "Installing dx_rt_npu_linux_driver..." "INFO"
            install_dx_rt_npu_linux_driver
            sanity_check "--dx_driver"
            show_information_message
            print_colored "[OK] Installing dx_rt_npu_linux_driver" "INFO"
            ;;
        dx_rt)
            print_colored "Installing dx_rt..." "INFO"
            install_dx_rt
            install_dx_rt_python_api
            sanity_check "--dx_rt"
            show_information_message
            print_colored "[OK] Installing dx_rt" "INFO"
            ;;
        dx_app)
            print_colored "Installing dx_app..." "INFO"
            install_dx_app
            sanity_check
            show_information_message
            print_colored "[OK] Installing dx_app" "INFO"
            ;;
        dx_stream)
            print_colored "Installing dx_stream..." "INFO"
            install_dx_stream
            sanity_check
            show_information_message
            print_colored "[OK] Installing dx_stream" "INFO"
            ;;
        dx_fw)
            print_colored "Installing dx_fw..." "INFO"
            sanity_check
            install_dx_fw
            show_information_message
            print_colored "[OK] Installing dx_fw" "INFO"
            ;;
        all)
            print_colored "Installing all runtime modules..." "INFO"
            uninstall_all_runtime_modules
            install_python_and_venv      # venv recreation
            venv_activate "$VENV_PATH"   # venv reactivate

            install_dx_rt_npu_linux_driver
            install_dx_rt
            install_dx_rt_python_api
            install_dx_fw
            install_dx_app
            install_dx_stream
            sanity_check
            show_information_message
            print_colored "[OK] Installing all runtime modules" "INFO"
            ;;
        *)
            show_help "error" "The '--all' option was not specified, or the '--target' option is invalid. Target packages will not be installed."
            ;;
    esac
}

DX_RT_INCLUDED=0
DX_APP_INCLUDED=0
# DX_RT_DRIVER_INCLUDED=0

TARGET_PKG=""
EXCLUDE_FW="n"
EXCLUDE_DRIVER="n"
SKIP_UNINSTALL="n"
USE_ORT="y"
# USE_SANITY_CHECK="y"
USE_COMPILED_VERSION_CHECK="y" # This variable is not used in the provided script, kept for consistency.

# variables for venv options
USE_DRIVER_SOURCE_BUILD="n"
VENV_PATH_ARG="" # Stores user-provided venv path
VENV_FORCE_REMOVE="y"
VENV_REUSE="n"

# parse args
for i in "$@"; do
    case "$1" in
        --all)
            TARGET_PKG=all
            ;;
        --exclude-fw)
            EXCLUDE_FW="y"
            ;;
        --exclude-driver)
            EXCLUDE_DRIVER="y"
            ;;
        --skip-uninstall)
            SKIP_UNINSTALL="y"
            ;;
        --target=*)
            TARGET_PKG="${1#*=}"
            ;;
        --use-ort=*)
            USE_ORT="${1#*=}"
            ;;
        --sanity-check=*)
            USE_SANITY_CHECK="${1#*=}"
            ;;
        # --sanity-check=*)
        #     USE_SANITY_CHECK="${1#*=}"
        #     ;;
        --driver-source-build)
            USE_DRIVER_SOURCE_BUILD="y"
            ;;
        --venv_path=*)
            VENV_PATH="${1#*=}"
            ;;
        -f|--venv-force-remove)
            VENV_FORCE_REMOVE="y"
            ;;
        -r|--venv-reuse)
            VENV_REUSE="y"
            VENV_FORCE_REMOVE="n"
            ;;
        -v|--verbose)
            ENABLE_DEBUG_LOGS=1
            ;;
        -h|--help)
            show_help
            ;;
        *)
            show_help "error" "Invalid option '$1'"
            ;;
    esac
    shift
done

main

exit 0
