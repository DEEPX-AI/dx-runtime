# RELEASE_NOTES

## DX-Runtime v2.1.0 / 2025-11-28
- DX_FW: v2.4.0
- NPU Driver: v1.8.0
- DX-RT: v3.1.0
- DX-Stream: v2.1.0
- DX-APP: v2.1.0

---

Here are the **DX-Runtime v2.1.0** Release Note for each module. 

### DX_FW (v2.2.0 ~ v2.4.0)
***1. Changed***  
- LPDDR Training Margin: Value reduced from 0.7 to 0.62. Enhanced test logic added (training at +200Mhz) with margin info saved to boot_env.
- Inference Host Response: Response to Host restricted to occur only if the bound is not zero.
- FCT Mode: Updated to be selectable (1: full test / 2: simple test).

***2. Fixed***  
- LPDDR Stability: Corrected LPDDR frequency showing 0 after CPU reset. Fixed PRBS training fail judge (DQS offset not applied on fail) and minor LPDDR4 build error.
- PCIe/Boot: Fixed minor PCIe link-up bugs and supported safe link-up on RPi5 (warm boot). Fixed hash calculation/index format in firmware update logic.  

***3. Added***  
- PPCPU Model Support: Added support for DXNNv8 PPU models (requires DX-RT 3.1.0+).
- Diagnostics/Security: Added Secure Debug and Model Profiling mode (for voltage drop analysis).
- Connectivity: Added option for NPU inference over USB.
- System: Supported Single MSI. Added Hash & Header check in the boot environment.
- FCT: Enhanced checks include buck IC slave address and LPDDR Training Margin.

### NPU Driver (v1.8.0)
***1. Changed***  
- Updated various driver and header files.  

***2. Fixed***  
- Corrected a device identification error and build-related issues.  

***3. Added***  
- Added a PCIe status command, an uninstall script, and new NPU-related files.

### DX-RT (v3.1.0)
***1. Changed***  
- Minimum Version Updates: Increased minimum required versions for Driver (1.8.0), PCIe Driver (1.5.1), and Firmware (2.4.0).
- DXNN File Format: The .dxnn file format was updated to V7 (from V6), and checks for the maximum supported version were added.
- CLI/Examples Standardization: All Python and C++ examples now use standardized command-line argument parsing and a unified argument format.
- Installation/Build: Added system requirement checks (RAM: 8GB, Arch: x86_64 or aarch64) to the install script. C++ exception handling now translates errors into Python exceptions.

***2. Fixed***  
- Multi-Model Stability: A critical bug affecting models with multi-output and multi-tail configurations was resolved.
- Multi-Tasking/Buffers: Fixed bugs related to CPU offloading buffer management, PPU output buffer mis-pointing, and other multi-tasking issues.
- Non-ORT Mode: Resolved tensor mapping errors and memory address configuration flaws occurring in non-ORT inference mode.
- Stability: Fixed Windows environment compile errors/warnings and a bounding issue on service.

***3. Added***  
- DXNN V8 Model Support: Added support for the V8 DXNN file format and PPU support for V8 models.
- Performance & Tuning Tools:
  - Added the DX-Fit tuning toolkit.
  - Added dxbenchmark (CLI tool for performance comparison) and the model voltage profiler (run_model_prof.py).
- Asynchronous API: Implemented Asynchronous NPU Format Handler (NFH) and included C++/Python examples for asynchronous inference with profiling.
- System/Device:
  - PPCPU Firmware loading is now done upon service initialization.
  - Added PCIe bus number display for dxtop.
  - Added new Python APIs for device configuration and status retrieval.

### DX-Stream (v2.1.0)
***1. Changed***  
- Performance Optimization: Synchronization was disabled in the Video Sink (secondary mode) for improved performance. Buffer processing was enhanced to use direct buffer manipulation.
- Model/Configuration: Default YOLOv5 model updated from YOLOV5S_3 to YOLOV5S_4. Message conversion settings were simplified, and JSON payload structure was improved.
- Logic/Compatibility: Event handling logic in elements (dxpreprocess, dxinfer, etc.) was modified to align with dxinputselector updates. Dependency installation for Debian 12 was enhanced.

***2. Fixed***  
- Pipeline Stability: A critical event processing timing issue in dxinputselector that caused compositor pipeline freezes was fixed.
- Setup/Memory: Improved error handling in setup scripts to prevent excessive download retries. Buffer handling in preprocessing/postprocessing pipelines and shutdown signal processing in dx-infer were improved.
- Compatibility: Added detection and installation of Rockchip-specific dependencies (librga-dev).

***3. Added***  
- PPU Support: Integrated Post-Processing Unit (PPU) functionality for key models (YOLOv5s, SCRFD500M, YOLOv5Pose).
   - This enables NPU-based bounding box decoding and NMS to reduce CPU overhead.
- Performance Analysis: GstShark integration was added, along with documentation and a script for comprehensive pipeline performance evaluation.
- Download Reliability: Setup scripts were enhanced with timeout limits and file integrity verification for more reliable downloads.
- Features/Build: Added preprocess skip functionality for conditional processing and build configuration for v3 architecture.


### DX-APP (v2.1.0)
***1. Changed***  
- Model Support: Updated model package version from 2.0.0 to 2.1.0 to support PPU models.
- Demos: Improved demo script with additional PPU-Demos (1, 4, 6, 8, 11).
- Dependencies: Added CPU-specific PyTorch wheel source in requirements.txt.
- Documentation/Build: Enhanced build script documentation; updated CMake to use C++17 and v143 (Visual Studio 2022) for Windows builds.

***2. Fixed***  
- Stability/Correctness: Fixed Windows MSBuild compilation warnings using explicit static_cast. Improved tensor allocation and numBoxes calculation logic.
- Usability: Fixed errors when using VAAPI with camera input. Enhanced application to display final FPS even when terminated during camera usage. Added VSCode configuration files.

***3. Added***  
- Windows Environment Support: Full support for Windows 10 / 11 has been added, including an automated build script (build.bat) and Visual Studio solution generation.
   - Requires M1 Driver v1.7.1+, Runtime Lib v3.1.0+, Python 3.8+, and Visual Studio 2022.
- PPU Data Types: Added support for three new PPU data types: BBOX (object detection), POSE (pose estimation keypoints), and FACE (face detection landmarks).
- Post-Processing: Enhanced post-processing functions to natively support the PPU inference output format.

***4. Known Issues***  
- Model Accuracy: DeepLabV3 Semantic Segmentation model accuracy may be slightly degraded (will be fixed in next release).
- PPU Converter: dx-compiler v2.1.0 does not yet support converting face detection and pose estimation models to PPU format.

For detailed updated items, refer to **each module's Release Note.**

---
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
