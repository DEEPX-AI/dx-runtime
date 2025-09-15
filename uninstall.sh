#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
PROJECT_ROOT=$(realpath "$SCRIPT_DIR")
DOWNLOAD_DIR="$SCRIPT_DIR/download"
PROJECT_NAME=$(basename "$SCRIPT_DIR")
VENV_PATH="$PROJECT_ROOT/venv-$PROJECT_NAME"

pushd "$PROJECT_ROOT" >&2

# color env settings
source ${PROJECT_ROOT}/scripts/color_env.sh
source ${PROJECT_ROOT}/scripts/common_util.sh

ENABLE_DEBUG_LOGS=0

# Global variables for tracking uninstall results
declare -A UNINSTALL_RESULTS

# Function to record uninstall result
record_result() {
    local module_name="$1"
    local result="$2"  # "success", "fail", or "skip"
    UNINSTALL_RESULTS["$module_name"]="$result"
}

# Function to print final results summary
print_results_summary() {
    echo -e "${COLOR_BOLD}${COLOR_CYAN}=== dx-runtime Submodules Uninstall Results ===${COLOR_RESET}"
    
    local has_results=false
    for module in "${!UNINSTALL_RESULTS[@]}"; do
        has_results=true
        local result="${UNINSTALL_RESULTS[$module]}"
        case "$result" in
            "success")
                echo -e "  $module: ${COLOR_GREEN}SUCCESS${COLOR_RESET}"
                ;;
            "fail")
                echo -e "  $module: ${COLOR_RED}FAILED${COLOR_RESET}"
                ;;
            "skip")
                echo -e "  $module: ${COLOR_YELLOW}SKIPPED${COLOR_RESET}"
                ;;
        esac
    done
    
    if [ "$has_results" = false ]; then
        print_colored_v2 "INFO" "  No submodules were processed."
    fi
    
    echo -e "${COLOR_BOLD}${COLOR_CYAN}================================================${COLOR_RESET}"
}

# Function to export results to parent process
export_results_to_parent() {
    local parent_results_file="$1"
    
    if [ -n "$parent_results_file" ]; then
        for module in "${!UNINSTALL_RESULTS[@]}"; do
            local result="${UNINSTALL_RESULTS[$module]}"
            echo "dx-runtime/$module:$result" >> "$parent_results_file"
        done
    fi
}

# Function to uninstall dx-runtime submodules
# Usage: uninstall_submodules "dx_rt dx_rt_npu_linux_driver dx_app dx_stream"
uninstall_submodules() {
    local submodules="$1"
    
    print_colored_v2 "INFO" "Starting dx-runtime submodule uninstallation..."
    
    for module in $submodules; do
        local uninstall_script="$module/uninstall.sh"
        
        if [ -f "$uninstall_script" ]; then
            print_colored_v2 "INFO" "Uninstalling $module..."
            
            # Execute uninstall script and capture result
            if (cd "$module" && yes n | ./uninstall.sh); then
                print_colored_v2 "INFO" "$module uninstall completed successfully"
                record_result "$module" "success"
            else
                print_colored_v2 "ERROR" "$module uninstall failed"
                record_result "$module" "fail"
            fi
        else
            print_colored_v2 "WARNING" "$module: uninstall.sh not found, skipping"
            record_result "$module" "skip"
        fi
    done
    
    # Print final results
    print_results_summary
}

show_help() {
    echo -e "Usage: ${COLOR_CYAN}$(basename "$0") [OPTIONS]${COLOR_RESET}"
    echo -e ""
    echo -e "Options:"
    echo -e "  ${COLOR_GREEN}[-v|--verbose]${COLOR_RESET}                        Enable verbose (debug) logging"
    echo -e "  ${COLOR_GREEN}[-h|--help]${COLOR_RESET}                           Display this help message and exit"
    echo -e ""
    echo -e "${COLOR_BOLD}Description:${COLOR_RESET}"
    echo -e "  This script uninstalls dx-runtime and all its submodules."
    echo -e "  It will automatically process: dx_rt, dx_rt_npu_linux_driver, dx_app, dx_stream"
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

uninstall_common_files() {
    print_colored_v2 "INFO" "Uninstalling common files..."
    delete_symlinks "$DOWNLOAD_DIR"
    delete_symlinks "$PROJECT_ROOT"
    delete_symlinks "${VENV_PATH}"
    delete_symlinks "${VENV_PATH}-local"
    delete_dir "${VENV_PATH}"
    delete_dir "${VENV_PATH}-local"
    delete_dir "${DOWNLOAD_DIR}" 
}

uninstall_project_specific_files() {
    print_colored_v2 "INFO" "Uninstalling ${PROJECT_NAME} specific files..."
}

main() {
    echo "Uninstalling ${PROJECT_NAME} ..."

    # Uninstall all submodules first
    print_colored_v2 "INFO" "=== Uninstalling dx-runtime Submodules ==="
    uninstall_submodules "dx_rt dx_rt_npu_linux_driver dx_app dx_stream"
    
    # Export results to parent if requested
    if [ -n "$DX_UNINSTALL_RESULTS_FILE" ]; then
        export_results_to_parent "$DX_UNINSTALL_RESULTS_FILE"
    fi
    
    print_colored_v2 "INFO" "=== Uninstalling dx-runtime Main Project ==="
    
    # Remove symlinks from DOWNLOAD_DIR and PROJECT_ROOT for 'Common' Rules
    uninstall_common_files

    # Uninstall the project specific files
    uninstall_project_specific_files

    echo "Uninstalling ${PROJECT_NAME} done"
}

# parse args
for i in "$@"; do
    case "$1" in
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

popd >&2

exit 0
