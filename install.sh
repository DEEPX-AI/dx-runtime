#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
RUNTIME_PATH=$(realpath -s "${SCRIPT_DIR}")
VENV_PATH="${RUNTIME_PATH}/venv-dx-runtime"
RT_PATH="${RUNTIME_PATH}/dx_rt"

# color env settings
source ${RUNTIME_PATH}/scripts/color_env.sh

function show_help()
{
    echo "Usage: $(basename "$0") OPTIONS(--all | --target=<module_name>) [--help]"
    echo "Example 1) $0 --all"
    echo "Example 2) $0 --target=dx_rt_npu_linux_driver"
    echo "Example 2) $0 --target=dx_rt"
    echo "Options:"
    echo "  --all                        : Install all dx-runtime modules (without firmware)"
    echo "  --target=<module_name>       : Install specify target dx-runtime module (ex> dx_fw | dx_rt_npu_linux_driver | dx_rt | dx_app | dx_stream)"
    echo "  [--use-ort=<y|n>]            : set 'USE_ORT' build option to 'ON or OFF' (default: y)"
    echo "  [--help]                     : Show this help message"

    if [ "$1" == "error" ] && [[ ! -n "$2" ]]; then
        echo -e "${TAG_ERROR} Invalid or missing arguments."
        exit 1
    elif [ "$1" == "error" ] && [[ -n "$2" ]]; then
        echo -e "${TAG_ERROR} $2"
        exit 1
    elif [[ "$1" == "warn" ]] && [[ -n "$2" ]]; then
        echo -e "${TAG_WARN} $2"
        return 0
    fi
    exit 0
}

function install_dx_rt_npu_linux_driver()
{
    DX_RT_DRIVER_INCLUDED=1
    sudo apt update && sudo apt-get -y install pciutils kmod build-essential make linux-headers-6.11.0-17-generic
    
    pushd $SCRIPT_DIR/dx_rt_npu_linux_driver
    # if .gitmodules file is exist, submodule init and update.
    if [ -f .gitmodules ]; then
        git submodule update --init --recursive
    fi
    popd
    
    pushd $SCRIPT_DIR/dx_rt_npu_linux_driver/modules

    sudo ./build.sh -c uninstall
    ./build.sh
    yes n | sudo ./build.sh -c install
    sudo modprobe dx_dma
    lsmod | grep dx

    popd
}

function set_use_ort()
{
    pushd ${RUNTIME_PATH}/dx_rt
    CMAKE_FILE="cmake/dxrt.cfg.cmake"

    if [ "${USE_ORT}" = "y" ]; then
        sed -i 's/option(USE_ORT *"Use ONNX Runtime" *OFF)/option(USE_ORT "Use ONNX Runtime" ON)/' "$CMAKE_FILE"
        echo -e "${TAG_INFO} USE_ORT option has been set to ON in dx_rt/$CMAKE_FILE"
    else
        sed -i 's/option(USE_ORT *"Use ONNX Runtime" *ON)/option(USE_ORT "Use ONNX Runtime" OFF)/' "$CMAKE_FILE"
        echo -e "${TAG_INFO} USE_ORT option is set to '${USE_ORT}'. so, USE_ORT option has been set to OFF in dx_rt/$CMAKE_FILE"
    fi 

    popd
}

function install_dx_rt()
{
    DX_RT_INCLUDED=1
    set_use_ort

    pushd $SCRIPT_DIR/dx_rt
    if [ "${USE_ORT}" = "y" ]; then
        sudo ./install.sh --all
    else
        sudo ./install.sh --dep
    fi
    ./build.sh --clean
    popd
}

function install_dx_rt_python_api()
{
    echo -e "=== Setup 'dx_engine' Python API... ${TAG_START} ==="
    . ${VENV_PATH}/bin/activate && \
    pushd ${RT_PATH}/python_package && \
    pip install . && \
    popd
    echo -e "=== Setup 'dx_engine' Python API... ${TAG_DONE} ==="
}

function install_dx_app()
{
    DX_APP_INCLUDED=1

    pushd $SCRIPT_DIR/dx_app
    sudo ./install.sh --all
    ./build.sh --clean
    popd
}

function install_dx_stream()
{
    pushd $SCRIPT_DIR/dx_stream
    sudo ./install.sh
    ./build.sh --install
    # gst-inspect-1.0 dxstream
    popd
}

function install_dx_fw()
{
    if [ ! -f "$SCRIPT_DIR/dx_fw/m1/latest/mdot2/fw.bin" ]; then
        echo "Error: firmware file not found!"
        exit 1
    fi
    if ! command -v dxrt-cli &> /dev/null; then
        echo "Error: 'dxrt-cli' not found!"
        exit 1
    fi
    dxrt-cli -g $SCRIPT_DIR/dx_fw/m1/latest/mdot2/fw.bin
    dxrt-cli -u $SCRIPT_DIR/dx_fw/m1/latest/mdot2/fw.bin
    echo "It is recommended to power off completely and reboot after the firmware update."
}

function setup_venv() {
    echo "--- setup python venv... ---"

    REQUIRED_PKGS=(python3 python3-dev python3-venv)

    for pkg in "${REQUIRED_PKGS[@]}"; do
        if dpkg -s "$pkg" &> /dev/null; then
            echo "Package '$pkg' is already installed. Skipping."
        else
            echo "Package '$pkg' is not installed. Installing..."
            sudo apt-get install -y "$pkg"
        fi
    done

    if [ ! -d "${VENV_PATH}" ]; then
        python3 -m venv "${VENV_PATH}"
    else
        echo "Virtual environment already exists at ${VENV_PATH}. Skipping creation."
    fi

    . ${VENV_PATH}/bin/activate && \
    echo "Upgrade pip wheel setuptools..." && \
    UBUNTU_VERSION=$(lsb_release -rs) && \
    echo "*** UBUNTU_VERSION(${UBUNTU_VERSION}) ***" && \
    if [ "$UBUNTU_VERSION" = "24.04" ]; then \
      pip install --upgrade setuptools; \
    elif [ "$UBUNTU_VERSION" = "22.04" ]; then \
      pip install --upgrade pip wheel setuptools; \
    elif [ "$UBUNTU_VERSION" = "20.04" ] || [ "$UBUNTU_VERSION" = "18.04" ]; then \
      pip install --upgrade pip wheel setuptools; \
    else \
      echo "Unspported Ubuntu version: $UBUNTU_VERSION" && exit 1; \
    fi
}

function host_reboot() {
	echo -e "${TAG_INFO} The 'dx_rt_npu_linux_driver' has been installed."
    echo -e "To complete the installation, the system must be restarted."
    echo -e -n "${COLOR_BRIGHT_GREEN_ON_BLACK}  Would you like to reboot now? (y/n): ${COLOR_RESET}"
	read -r answer
	if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
		echo "Start reboot..."
		sudo reboot now
	fi
}

function show_information_message()
{
    if [[ ${DX_RT_INCLUDED} -eq 1 || ${DX_APP_INCLUDED} -eq 1 ]]; then
        echo -e "${TAG_INFO} To activate the virtual environment, run:"
        echo -e "${COLOR_BRIGHT_YELLOW_ON_BLACK}  source ${VENV_PATH}/bin/activate ${COLOR_RESET}"
    fi

    if [ ${DX_RT_DRIVER_INCLUDED} -eq 1 ]; then
        host_reboot
    fi
}

DX_RT_INCLUDED=0
DX_APP_INCLUDED=0
DX_RT_DRIVER_INCLUDED=0

TARGET_PKG=""
USE_ORT="y"
USE_COMPILED_VERSION_CHECK="y"

# parse args
for i in "$@"; do
    case "$1" in
        --all)
            TARGET_PKG=all
            ;;
        --target=*)
            TARGET_PKG="${1#*=}"
            ;;
        --use-ort=*)
            USE_ORT="${1#*=}"
            ;;
        --help) 
            show_help
            ;;
        *)
            show_help "error" "Invalid option '$1'"
            ;;
    esac
    shift
done

case $TARGET_PKG in
    dx_rt_npu_linux_driver)
        echo -e "Installing dx_rt_npu_linux_driver ${TAG_START}"
        install_dx_rt_npu_linux_driver
        show_information_message
        echo -e "Installing dx_rt_npu_linux_driver ${TAG_END}"
        ;;
    dx_rt)
        echo -e "Installing dx_rt ${TAG_START}"
        setup_venv
        install_dx_rt
        install_dx_rt_python_api
        show_information_message
        echo -e "Installing dx_rt ${TAG_END}"
        ;;
    dx_app)
        echo -e "Installing dx_app ${TAG_START}"
        setup_venv
        install_dx_rt_python_api
        install_dx_app
        show_information_message
        echo -e "Installing dx_app ${TAG_END}"
        ;;
    dx_stream)
        echo -e "Installing dx_stream ${TAG_START}"
        install_dx_stream
        show_information_message
        echo -e "Installing dx_stream ${TAG_END}"
        ;;
    dx_fw)
        echo -e "Installing dx_fw ${TAG_START}"
        install_dx_fw
        show_information_message
        echo -e "Installing dx_fw ${TAG_DONE}"
        ;;
    all)
        echo -e "Installing all runtime modules ${TAG_START}"
        setup_venv
        install_dx_rt
        install_dx_rt_python_api
        install_dx_app
        install_dx_stream
        install_dx_rt_npu_linux_driver
        show_information_message
        echo -e "Installing all runtime modules ${TAG_DONE}"
        ;;
    *)
        show_help "warn" "The '--all' option was not specified, or the '--target' option is invalid. Target packages will not be installed."
        ;;
esac


