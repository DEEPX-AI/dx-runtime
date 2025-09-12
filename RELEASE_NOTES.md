# RELEASE_NOTES

## DX-Runtime v2.0.0 / 2025-09-08
- DX_FW : v2.1.4
- NPU Driver : v1.7.1
- DX-RT : v3.0.0
- DX-Stream : v2.0.0
- DX-APP : v2.0.0

---

Here are the **DX-Runtime v2.0.0** Release Note for each module. 

### DX_FW (v2.1.1 ~ v2.1.4)
***1. Changed:***  
- Implemented a new "stop & go" inference function that splits large tiles for better performance.
 
***2. Fixed:***  
- Corrected a QSPI read logic bug to prevent underflow.  

***3. Added:***  
- Weight Data Monitoring: The NPU recover corrupted weight data from the host.
- CLI & Tool Support: Added a CLI command for PCIe/DMA status and a parser for the RX eye measurement tool.

### NPU Driver (v1.6.0 ~ v1.7.1)
***1. Changed:***  
- Updated various driver and header files.  

***2. Fixed:***  
- Corrected a device identification error and build-related issues.  

***3. Added:***  
- Added a PCIe status command, an uninstall script, and new NPU-related files.

### DX-RT (v3.0.0)
***1. Changed:***  
- Minimum Versions: Updated minimum versions for the driver, PCIe driver, and firmware.
- Performance: Increased the number of threads for `DeviceOutputWorker` from 3 to 4.
- Build Process: Changed the default build option to `USE_ORT=ON` and updated the compiler to version 14. Add automatic handling of input dummy padding and output dummy slicing when USE_ORT=OFF (build-time or via InferenceOption).    

***2. Fixed:***  
- Resolved a kernel panic issue caused by a wrong NPU channel number.
- Fixed a build error related to Python 3.6.9 incompatibility by adding automatic installation support for Python 3.8.2.  

***3. Added:***  
- Monitoring & Tools: Added a new dxtop monitoring tool and a `dxrt-cli --errorstat` option for PCIe details.
- New Features: Implemented a new USB inference module and Sanity Check features.
- APIs & Examples: Included new Python APIs and examples for configuration and device status.
- Add support for both `.dxnn` file formats: DXNN v6 (compiled with dx_com 1.40.2 or later) and DXNN v7 (compiled with dx_com 2.x.x).

### DX-Stream (v2.0.0)
***1. Changed:***  
- Code & Compatibility: Post-processing examples are now separated by model for clarity. This version is fully compatible with DX-RT v3.0.0 and now only supports inference for models (DXNN v7) created by DX-COM v2.0.0 or later.  
- Build & Logging: The build script now includes OS and architecture checks, and unnecessary print statements have been removed.  

***2. Fixed:***  
- Stability: Fixed a processing delay bug in dx-inputselector and corrected a post-processing logic error for the SCRFD model.
- Error Handling: Improved error handling for setup scripts and fixed a bug in dx_rt that affected multi-tail models.
- Compatibility: Added support for the X11 video sink on Ubuntu 18.04 to improve cross-OS compatibility.  

***3. Added:***  
- Utilities: Introduced a new uninstall.sh script to help clean up project files.

### DX-APP (v2.0.0)
***1. Changed:***  
- Code Structure: The YOLO post-processing guide was moved to a separate document, and demo applications were extensively refactored and restructured. Common utilities were consolidated, and deprecated code was removed.  
- YOLO Post-Processing: The YoloPostProcess now correctly filters tensors by output name when USE_ORT=ON. The yolo_pybind_example.py was refactored to use a RunAsync() + Wait() structure for improved output handling.  
- Build & Docs: The build script now includes OS and architecture checks. Documentation was updated to include Python requirements and to add a new YOLOv5s-6 JSON configuration. Command-line help messages were also improved for clarity.  

***2. Fixed:***  
- Bugs: Corrected an FPS calculation bug in yolo_multi and fixed a post-processing logic error to support new YOLO model output shapes when USE_ORT=OFF. A typo in a framebuffer path was also fixed.  
- Error Handling: Improved error messages for output tensor size mismatches and missing tensors.  
- Compatibility: Removed post-processing code for legacy PPU models.  

***3. Added:***  
- Utilities: Added a uninstall.sh script to clean up installed packages and build artifacts.
- YOLO Features: Added a feature to filter output tensors using a target_output_tensor_name key in the JSON configuration. Post-processing support was also added for YOLO_pose and YOLO_face models when USE_ORT=ON.
- Compatibility: Implemented version guards to ensure compatibility with DX-RT ≥ 3.0.0 and DXNN model version ≥ 7.

For detailed updated items, refer to **each module's Release Notes.**

---

## DX-Runtime v1.0.0 / 2025-07-23
- DX_FW : v2.1.0
- NPU Driver : v1.5.0
- DX-RT : v2.9.5
- DX-Stram : v1.7.0
- DX-APP : v1.11.0

We're excited to announce the **initial release of DX-Runtime v1.0.0.**

---

### What's New?

This v1.0.0 release introduces the foundational capabilities of DX-Runtime:

* **Initial version release of DX-Runtime (DX-RT).** This is the core runtime software for executing `.dxnn` models on DEEPX NPU hardware.
* **Direct NPU Interaction:** DX-RT directly interacts with DEEPX NPU through firmware and device drivers, utilizing PCIe for high-speed data transfer.
* **C/C++ and Python APIs:** Provides APIs for application-level inference control, enabling flexible integration into various projects.
* **Complete Runtime Environment:** Offers comprehensive features including model loading, I/O buffer management, inference execution, and real-time hardware monitoring.
* **Integrated Inference Workflow:** Supports an end-to-end inference flow from input/pre-processing (using OpenCV) to post-processing and display.
* **Configurable Inference Options:** Allows configuration of InferenceOption to specify target devices and available resources for optimized execution.

---
