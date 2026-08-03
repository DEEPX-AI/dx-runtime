# RELEASE_NOTES

## DX-Runtime v2.4.1 / 2026-08-03

- DX_FW: v2.7.4
- NPU Driver: v2.6.0
- DX-RT: v3.4.1
- DX-Stream: v3.1.1
- DX-APP: v3.2.1

---

Here are the **DX-Runtime v2.4.1** Release Notes for each module.

### DX_FW (v2.7.4)

**_1. Changed_**  

**_2. Fixed_**  
- Added PCIe message API for MSI IMWR to support VM environments

**_3. Added_**  

---

### NPU Driver (v2.6.0)

**_1. Changed_**  
- Enhanced MSI handling for virtualization support in eDMA driver

**_2. Fixed_**  
- Added support for kernel version 4.4.0
- Fixed issue where forked child's close() could cancel parent's ioctl wait

**_3. Added_**  

---

### DX-RT (v3.4.1)

**Packages unchanged:** libdxrt, libdxrt-bin, and dx_engine wheels remain at v3.4.0. This release contains documentation updates only.

**_1. Changed_**  

**_2. Fixed_**  
- Corrected supported OS list: removed Ubuntu 18.04 (EOL), added Ubuntu 26.04
- Clarified ONNX Runtime version recommendation wording
- Removed stray emoji characters from C++ and Python tutorial pages

**_3. Added_**  
- Added bundled wheel installation guide for virtual environments
- Added info note documenting `/usr/share/libdxrt-bin/python/` bundled wheel directory

---

### DX-Stream (v3.1.1)

**_1. Changed_**  

**_2. Fixed_**  
- Fixed typos and added missing details in documentation

**_3. Added_**  

---

### DX-APP (v3.2.1)

**_1. Changed_**  
- Updated all example commands in README and docs to the new model filename convention (e.g. YoloV9S.dxnn -> yolov9-s_640x640.dxnn)
- Super-resolution now saves both a side-by-side comparison (sr_input_output.jpg) and the standalone upscaled output.

**_2. Fixed_**  
- Fixed RealESRGAN discolored output vs. C++: corrected color rounding and RGB -> BGR channel order, and stopped routing 3-channel SR models through the luminance-only tiled path

**_3. Added_**  

---

## DX-Runtime v2.4.0 / 2026-07-22

- DX_FW: v2.7.3
- NPU Driver: v2.5.1
- DX-RT: v3.4.0
- DX-Stream: v3.1.0
- DX-APP: v3.2.0

---

Here are the **DX-Runtime v2.4.0** Release Notes for each module.

### DX-RUNTIME (v2.4.0)

**_1. Changed_**  
- `install.sh` installs dx_rt from the prebuilt Debian package by default (no compiler toolchain, much faster); use `--rt-source-build` for the previous source build
- Supported OS extended to Ubuntu 26.04 and Debian 13

**_2. Fixed_**  
- `--exclude-*` modules are no longer uninstalled before an install, so `--all --exclude-<module>` keeps the existing module intact
- Reinstall/uninstall of dx_rt now cleans up a previously package-installed runtime instead of leaving stale files behind

**_3. Added_**  
- `--runtime-only` to install only the runtime stack (NPU driver, dx_rt, dx_fw)
- `--target=` accepts multiple modules at once (e.g. `--target=dx_rt,dx_app`)
- `--exclude-rt`, `--exclude-app`, `--exclude-stream` to skip individual modules

---

### DX_FW (v2.7.3)

**_1. Changed_**  
- Revert M1/M1M IC and M.2 module and DX-H1 Quattro board products PCIe device id to `0x0000`.
- Adjust cpu reset delay from 20ms to 200ms to ensure stable PLL lock.
- Updated OTP Revision.  
- Disabled Root Complex Tx Equalization Preset 10 by default during PCIe link equalization, as it is strictly reserved for compliance test and can cause the link to enter compliance/test loops during normal boot.  
- Changed BAR0 type from prefetchable to non-prefetchable on VNPU board type.  

**_2. Fixed_**  
- Clear input queues when all bound option is deleted.  
- Solving PCIe enumeration issue on RZ/G3E. 
  
**_3. Added_**  

---

### NPU Driver (v2.5.1)

**_1. Changed_**  
- Improved device connection and reconnection handling to enhance resilience during temporary connectivity instability.
- Optimized data flow for large-scale data transfers to improve operational consistency under high-load environments.

**_2. Fixed_**  
- Reject in-flight mailbox cmds during FW reboot, harden recovery sleep
- Fixed an issue where the device failed to return to a normal state after a firmware update.
- Resolved module installation and loading errors that occurred in certain hardware environments.

**_3. Added_**  
- Added automatic recovery logic for critical runtime error scenarios.
- Expanded device identification support to recognize a wider range of hardware variants.
- Added a background preparation path to reduce latency during large-volume transfers.

---

### DX-RT (v3.4.0)

**_1. Changed_**  
- Debian package bundles `dx_engine` Python wheels for Python 3.8 – 3.14.
- CLI binary names updated: `dxrt-cli` → `dxcli`, `parse_model` → `dxparse`, `run_model` → `dxrun` (old names remain as backward-compatible aliases)
- Python bindings now use header-only dxrt_cxx_api.h instead of direct C++ linkage
- libdxrt.so exports C symbols only (dxrt_*); internal C++ symbols hidden via version script
- Updated minimum versions: Driver 2.5.0, PCIe Driver 2.4.0, Firmware 2.7.0
- Code style cleanup and dependency updates (cxxopts v3.1.1 → v3.3.1, lazy matplotlib loading)

**_2. Fixed_**  
- Fixed critical crash (nullptr) in pyRunBenchmark and SEGV in NFHLayer profiler instrumentation
- Improved shared-memory performance and temperature validation in dxtop
- Multiple API refinements: error messages, output formatting, ppcpu logic, multi-input dictionary handling

**_3. Added_**  
- Stable C ABI (dxrt_c_api.h, 103 functions) enabling prebuilt SDK distribution without recompilation
- Header-only C++ wrapper (dxrt_cxx_api.h) for single-include modern C++ usage
- SDK-compat bridge headers (legacy/) for backward compatibility with existing dxrt_api.h code
- H1M firmware compatibility check: distinguish H1M (LPDDR4) from H1 (LPDDR5/LPDDR5X); support mixed 4-pack / 6-pack H1M configurations
- Shared memory-based IPC infrastructure with packet-based protocol layer and cross-platform support (Linux/Windows)
- New device monitoring APIs (memory usage, per-core temperature, and utilization)
- Profiler enhancements: GetJobMetrics() API and Coefficient of Variation (CoV) metric
- HTML visualization tool (plot_html.py) for profiling data and input dtype validation
- Debian packaging improvements: prebuilt directory structure and `libdxrt-bin` with amd64/arm64 auto-detection

---

### DX-Stream (v3.1.0)

**_1. Changed_**  
- Multi-Stream Domain: Introduced `application/x-dxvideoraw` domain caps for unified multi-stream processing with different resolutions/formats
- Base class migration: `dxinputselector`/`dxgather` → `GstAggregator` for N:1 multiplexing; `dxvnpuoverlay` → `GstBaseSink` for proper render/preroll lifecycle
- TransformKernelPool: Automatic src-format-based kernel selection with libyuv fallback for dxscale, dxconvert, dxpreprocess, dxmsgconv
- InferBackend abstraction: Refactored dxinfer to use Put/Get async pattern with backend property (auto/dxrt/dxvnpu)
- Model list updated to include models compiled with DX-COM v2.4.0

**_2. Fixed_**  
- LATENCY reporting: All elements now correctly account for processing time, stabilizing synchronization and QoS behavior
- FLUSH recovery and push thread lifecycle: Proper reset of queues/threads/state on FLUSH, eliminating hangs on seek/replay
- Caps negotiation and error handling: Tightened pad template caps for immediate failure on incompatible connections; replaced `abort()` with proper `GST_ELEMENT_ERROR` messages

**_3. Added_**  
- Windows MSVC build and runtime environment: Full support including dependency check, build, demo launcher, test suite, Python binding (pydxs)
- DEEPX Agent-Driven Development (dx-agent-dev, Beta): Describe pipelines in natural language and an AI agent assembles GStreamer graphs from DEEPX elements
- Test Suite: 73 new test binaries under `test/base/{element,metadata,pipeline}/` covering element contracts, domain boundaries, end-to-end pipelines
- DxMsgConv: `include-frame` property for base64 JPEG frame encoding with Kafka/MQTT consumer display support

---

### DX-APP (v3.2.0)

**_1. Changed_**  
- Image-only examples (embedding/reid/attribute) now reject stream inputs with input hints instead of exposing unused video options
- Detection-family examples expose explicit config.json runtime knobs (score/nms/top_k/obj) with output-preserving defaults
- Standardized DX-APP user-facing message level tags to `[DXAPP] [INFO/WARN/ERROR]`
- Migrated model-zoo manifest to `2_4_0` URL hierarchy and replaced sample images to remove licensing risk
- Generalized float-input preprocessing (FLOAT dtype → normalized float32 buffer)
- Default build mode changed to minimal in build.sh/build.bat with interactive prompts

**_2. Fixed_**  
- Super-resolution now preserves input resolution via dynamic tile padding
- Fixed `--save` option not producing output files in C++ sync runners for multiple AI tasks
- Multiple post-processor fixes: DOPE, YOLOPv2, RetinaFace, Depth Anything V2 normalization
- Build fixes: pybind missing includes, Windows x64 library paths, async runner metrics, E2E test model matching

**_3. Added_**  
- DEEPX Agent-Driven Development (dx-agent-dev) — Beta: Generate standalone Python/C++ inference apps from plain language
- Native C++ post-processing for model zoo (YOLO families, semantic seg, Face3D, embedding/classification/attribute, restoration, YOLO-PPU)
- Opt-in `--fast-postprocess` path for object detection and instance segmentation
- Windows Visual Studio solution package extraction workflow with automatic OpenCV/DXRT CMake configuration
- Build enhancements: `--demo-models` download option, minimal/category-based builds, Windows build selection TUI, `--all` flag
- Knowledge base (`.deepx/`): specialized agents, app-building/SWE skills, multi-platform agent-instruction generation via `dx-agent-gen`
- Supported for 67 net-new models (280 → 347 models) across 22 AI task categories
- 5 new AI tasks: 3D Object Detection (SFA3D), Keypoint Detection (SuperPoint), Object Pose Estimation (DOPE), Panoptic Driving Perception (YOLOPv2), Hand Detection (MediaPipe Hand)
- 7 new post-processors + pybind bindings (43 → 50 classes), 3 C++ factory interfaces, 3 visualizers
- Per-model Python examples (4 variants) and C++ examples (sync/async) for all new models
- YOLO Customizing Guide documentation

---

## DX-Runtime v2.3.3 / 2026-05-14

- DX_FW: v2.5.6
- NPU Driver: v2.4.1
- DX-RT: v3.3.2
- DX-APP: v3.1.1
- DX-STREAM: v3.0.1

---

Here are the **DX-Runtime v2.3.3** Release Notes for each module.

### NPU Driver (v2.4.1)

**_1. Changed_**  

**_2. Fixed_**  
- Added missing Debian package files for `dx_rt_npu_linux_driver`

**_3. Added_**  

---

## DX-Runtime v2.3.2 / 2026-05-11

- DX_FW: v2.5.6
- NPU Driver: v2.4.1
- DX-RT: v3.3.2
- DX-APP: v3.1.1
- DX-STREAM: v3.0.1

---

Here are the **DX-Runtime v2.3.2** Release Notes for each module.


### DX-RT (v3.3.2)

**_1. Changed_**
- Removed redundant build artifacts and temporary directories from the Debian package.

**_2. Fixed_**
- Improved Python extension module linking for _pydxrt build.

**_3. Added_**  
- Added conditional pip upgrade (v21.3+) to ensure build stability on legacy OS environments.

---

## DX-Runtime v2.3.1 / 2026-05-06

- DX_FW: v2.5.6
- NPU Driver: v2.4.1
- DX-RT: v3.3.1
- DX-APP: v3.1.1
- DX-STREAM: v3.0.1

---

Here are the **DX-Runtime v2.3.1** Release Notes for each module.


### DX-RT (v3.3.1)

**_1. Changed_**
- Changed the version of pre-built onnxruntime(1.23.2 -> 1.22.0) and openvino(25.4 -> 25.1)

**_2. Fixed_**
- Fixed error in uninstall logic

**_3. Added_**  

### DX-APP (v3.1.1)

**_1. Changed_**  

**_2. Fixed_**  

**_3. Added_**  
- Added license information for third-party models & datasets

### DX-Stream (v3.0.1)

**_1. Changed_**  

**_2. Fixed_**  
- Fixed uninstall not removing apps build directories and pydxs build cache

**_3. Added_**  
- Added license information for third-party models & datasets

---

## DX-Runtime v2.3.0 / 2026-04-10

- DX_FW: v2.5.6
- NPU Driver: v2.4.1
- DX-RT: v3.3.0
- DX-Stream: v3.0.0
- DX-APP: v3.1.0

---

Here are the **DX-Runtime v2.3.0** Release Notes for each module.

### DX_FW (v2.5.1 ~ 2.5.6)

**_1. Changed_**  
- PPU Logic: Synchronized with `dxnn` compiler for improved consistency.  
- AVC Policy: Updated Automatic Voltage Control; increased minimum voltage (730 -> 750) and cold-temp start voltage for M1M.  

**_2. Fixed_**  
- Console Security: Added authentication to CLI console and fixed interrupt storms for abnormal IRQs.
- PPU Stability: Disabled QoS to resolve bitmatch failures; aligned PPU memory access (2-cell) for YOLO models.
- Power Saving: Re-enabled run mode NPU and hardened devMode race.

**_3. Added_**  

---

### NPU Driver (v2.2.0 ~ 2.4.1)

**_1. Changed_**  
- Distribution: Hardened DKMS package and modularized the build system.  
- Multi-process: Added concurrent process support with graceful `PROC_EXIT` termination.  

**_2. Fixed_**  
- Kernel Stability: Fixed ARM64 IOMMU DMA coherency bugs and `vunmap` crashes.  
- Compatibility: Resolved Raspberry Pi 4 PCIe errors via 32-bit MMIO enforcement.  
- Synchronization: Fixed race conditions in the PCIe driver synchronization.  

**_3. Added_**  
- Reliability: Implemented DMA abnormal recovery mechanism.  
- Development: Added `dx_mmio_compat.h` for 32-bit safe MMIO accessor helpers.  

---

### DX-RT (v3.3.0)

**_1. Changed_**  
- Dependencies: Updated minimum dependencies (Driver v2.4.0, PCIe v2.2.0, FW v2.5.2).  
- Parity: Synchronized Python and C++ module versions for parity.  

**_2. Fixed_**  
- Multi-Device: Resolved PPU transfer errors in multi-process and H1/M1 environments.
- Internal Logic: Fixed Python data lifecycle bugs and IPC message queue exceptions.

**_3. Added_**  
- CLI/Tools: Added `dxtop` for No Service Mode.
- Engine: Enabled direct memory-buffer inference (C++) and NumPy-based engine (Python).
- Optimization: Introduced optional build-time CPU acceleration features.

---

### DX-Stream (v3.0.0)

**_1. Changed (Breaking Changes)_**  
- Model Management: Migrated to `dx-modelzoo` (YOLOv26 default). Requires jq and `setup_sample_models.sh`.  
- Installation: Migrated to sudo-less installation via `~/.bashrc` and updated to C++14 (Breaking).  
- Architecture: Introduced `IVideoTransformKernel` abstraction and optimized YUV in-place OSD.  

**_2. Fixed_**  
- Buffers: Enabled DMA-Buffer zero-copy and fixed NV12/I420 stride/offset calculation errors.  
- Platform: Resolved RK3588 display corruption and Rockchip RGA build errors.  

**_3. Added_**   
- Plugins: New `DxScale` (HW scaling) and `DxConvert` (format conversion) elements.  
- V3 Support: Added V3 DSP preprocessor and OSD v3 RGB buffer drawing.  

---

### DX-APP (v3.1.0)

**_1. Changed_**  
- Unified Architecture: Standardized 5-layer design pattern (App/Runner/Factory/Component/Interface) for C++ and Python parity.  
- Interactive UI: Redesigned `run_demo.sh` and `run_examples.sh` with multi-stage interactive menus.  
- CLI UX: Optional `--model` and `--video` arguments with task-appropriate smart defaults.  

**_2. Fixed_**  

**_3. Added_**  
- AI Tasks: Support for Depth Estimation (FastDepth) and Image Restoration (DnCNN, Zero-DCE, ESPCN).  
- Model Zoo: Integrated 280+ models across 17 categories (including YOLOv8–v12 PPU models).  
- Automation: Manifest-based auto-download system for missing models or videos.  
- Monitoring: Real-time performance tables and `--verbose` log mode for Python.  

---

## DX-Runtime v2.2.2 / 2026-02-26

- DX-APP: v3.0.2
- DX-STREAM: v2.2.1

---

Here are the **DX-Runtime v2.2.2** Release Notes for each module.

### DX-APP (v3.0.2)

**_1. Changed_**
- Copy of dxrt and vkpkg DLLs into the dx-app/bin directory when building with MSVC.
- Updated sample models version from dx_com v2.2.0 to v2.2.1

**_2. Fixed_**
- Removed experimental filesystem includes and updated float literals in example cpp files for build error on windows
- Refactored apply_argmax to reduce nesting and fix gcovr warnings

**_3. Added_**
- Added vcpkg installation script for windows build. 

### DX-Stream (v2.2.1)

**_1. Changed_**
- Updated sample models version from dx_com v2.2.0 to v2.2.1

---

## DX-Runtime v2.2.1 / 2026-02-06

- DX-APP: v3.0.1

---

Here are the **DX-Runtime v2.2.1** Release Notes for each module.

### DX-APP (v3.0.1)

**_1. Changed_**

**_2. Fixed_**

- Hardcoded attribute size in YOLO post-processing to dynamically adjust based on model output shape

**_3. Added_**

- Added yolov26 cls, yolo26 pose, yolo26 seg, yolo26 obb examples

---

## DX-Runtime v2.2.0 / 2026-01-16

- DX_FW: v2.5.0
- NPU Driver: v2.1.0
- DX-RT: v3.2.0
- DX-Stream: v2.2.0
- DX-APP: v3.0.0

---

Here are the **DX-Runtime v2.2.0** Release Notes for each module.

### DX_FW (v2.5.0)

**_1. Changed_**

- PCIe Stability: Added PERST# signal wait during initial boot stage.
- Thermal Priority: Changed to Emergency > User > Default.
- Inference Time: Updated inf_time to include both NPU and PPU runtimes.

**_2. Fixed_**

**_3. Added_**

- NPU QoS: Added Quality of Service to the NPU Scheduler.
- Flash Support: Added support for nand 2k flash images.

### NPU Driver (v2.0.0 ~ 2.1.0)

**_1. Changed_**

- System Stability: Added sleep/reschedule in polling to prevent soft lockups during slow ACKs.
- Performance: Optimized PCIe DMA by reducing CPU dependency (Best with DX-RT SDK v3.2.0+).
- Initialization: Added request ID (req-id) initialization for V3.

**_2. Fixed_**

**_3. Added_**

### DX-RT (v3.2.0)

**_1. Changed_**

- Optimization: Improved PCIe DMA sequence and updated Debian OS requirements in the docs.

**_2. Fixed_**

- Memory: Reduced device memory footprint for PPU models.

**_3. Added_**

- Event Handling: Added `RuntimeEventDispatcher` (C++ singleton & Python wrapper) for centralized system events.
- CLI Options: Added `--profiler` and `--buffer-count` to `run_model.py`.
- Build Script: Added options to toggle Service and ORT components (`--use_service_on/off`, `--use_ort_on/off`).
- Engine Features: Enabled direct `.dxnn` loading from memory and per-instance I/O buffer configuration.
- Metadata: Added `__version__` to the `dx_engine` namespace.

### DX-Stream (v2.2.0)

**_1. Changed_**

- Buffer Handling: Updated `gst-dxpreprocess` to auto-copy buffers when `ref_count > 1`.
- Metadata Architecture: Modularized metadata files (frame/object/user) and enhanced structures.
- Test & Docs: Refactored test framework for better performance and updated Debian OS requirements.

**_2. Fixed_**

- Stability: Resolved race conditions and segfaults in secondary inference mode.
- API/Errors: Migrated to new object metadata APIs and improved compilation error handling in tests.

**_3. Added_**

- Python Bindings: Introduced `pydxs` module with support for `DXFrameMeta`, `DXObjectMeta`, and `DXUserMeta`.
- User Metadata: New API/interface for custom metadata attachment and management.
- Tools & Samples: Added `writable_buffer` context manager and a new `usermeta_app.py` sample.
- Testing: Added a dedicated user metadata test suite (`test_usermeta.cpp`).

### DX-APP (v3.0.0)

**_1. Changed_**

- Project Structure: Complete overhaul from legacy `demos/` to a task-based example system in `src/cpp_example/` and `src/python_example/`.
- Build System: Updated to C++17 and Visual Studio 2022; improved CMake and cross-compilation support.
- Performance Profiling: Added stage-specific latency measurement (pre/inf/post), E2E FPS calculation, and automatic report generation.
- Expanded Support: Added YOLO26, YOLOv10/11/12, YOLOv8-seg, DeepLabv3, and PPU (Post-Processing Unit) module integration.

**_2. Fixed_**

- Code Quality: Implemented `try-catch` handling, replaced `using namespace std` with explicit `std::`, and improved argument validation.
- Input Processing: Optimized RTSP/Camera speed via buffer size adjustment and fixed memory reference issues in async inference.

**_3. Added_**

- dx_postprocess: New Pybind11-based library providing C++ post-processing functions for Python.
- Test Framework: Added Pytest-based E2E integrated test system with >93% code coverage.
- New Features:
  - YOLO26 Support: Integration of the latest Ultralytics model optimized for edge deployment.
  - Expanded Utilities: Support for various input sources (RTSP, Camera, Video), `--no-display` mode for benchmarking, and skeleton drawing for Pose Estimation.

**_4. Removed or Replaced_**

- Legacy Demos: Completely removed `demos/` directory and all previous classification, detection, and segmentation examples.
- Configs: Deleted legacy JSON configuration files and Docker/Debian build files.
- Cleanup: Removed `demo_utils/`, redundant YOLOv5 code, and RISCV64 architecture support.

**_5. Migration Guide_**

- Breaking Changes: v3.0.0 is not backward compatible. Users must switch from `demos/` to the new `src/` example structure.
- Execution: Command-line arguments now replace JSON configuration files for Python examples.
- Upgrade Path: Refer to new documentation, install via `requirements.txt`, and use the updated `build.sh/bat` scripts.

**_6. Known Issues_**

- PPU Conversion: `dx-compiler v2.1.0/v2.2.0` does not currently support converting face/pose models to PPU format (use models converted with v1.0.0).

---

## DX-Runtime v2.1.0 / 2025-11-28

- DX_FW: v2.4.0
- NPU Driver: v1.8.0
- DX-RT: v3.1.0
- DX-Stream: v2.1.0
- DX-APP: v2.1.0

---

Here are the **DX-Runtime v2.1.0** Release Notes for each module.

### DX_FW (v2.2.0 ~ v2.4.0)

**_1. Changed_**

- LPDDR Training Margin: Value reduced from 0.7 to 0.62. Enhanced test logic added (training at +200Mhz) with margin info saved to boot_env.
- Inference Host Response: Response to Host restricted to occur only if the bound is not zero.

**_2. Fixed_**

- LPDDR Stability: Corrected LPDDR frequency showing 0 after CPU reset. Fixed PRBS training fail judge (DQS offset not applied on fail) and minor LPDDR4 build error.
- PCIe/Boot: Fixed minor PCIe link-up bugs and supported safe link-up on RPi5 (warm boot). Fixed hash calculation/index format in firmware update logic.

**_3. Added_**

- PPU Model Support: Added support for DXNNv8 PPU models (requires DX-RT 3.1.0+).
- Diagnostics/Security: Added Secure Debug and Model Profiling mode (for voltage drop analysis).
- System: Supported Single MSI. Added Hash & Header check in the boot environment.

### NPU Driver (v1.8.0)

**_1. Changed_**

- Updated various driver and header files.

**_2. Fixed_**

- Corrected a device identification error and build-related issues.

**_3. Added_**

- Added a PCIe status command, an uninstall script, and new NPU-related files.

### DX-RT (v3.1.0)

**_1. Changed_**

- Minimum Version Updates: Increased minimum required versions for Driver (1.8.0), PCIe Driver (1.5.1), and Firmware (2.4.0).
- DXNN File Format: The .dxnn file format was updated to V7 (from V6), and checks for the maximum supported version were added.
- CLI/Examples Standardization: All Python and C++ examples now use standardized command-line argument parsing and a unified argument format.
- Installation/Build: Added system requirement checks (RAM: 8GB, Arch: x86_64 or aarch64) to the install script. C++ exception handling now translates errors into Python exceptions.

**_2. Fixed_**

- Multi-Model Stability: A critical bug affecting models with multi-output and multi-tail configurations was resolved.
- Multi-Tasking/Buffers: Fixed bugs related to CPU offloading buffer management, PPU output buffer mis-pointing, and other multi-tasking issues.
- Non-ORT Mode: Resolved tensor mapping errors and memory address configuration flaws occurring in non-ORT inference mode.
- Stability: Fixed Windows environment compile errors/warnings and a bounding issue on service.

**_3. Added_**

- DXNN V8 Model Support: Added support for the V8 DXNN file format and PPU support for V8 models.
- Added dxbenchmark (CLI tool for performance comparison) and the model voltage profiler (run_model_prof.py).
- Asynchronous API: Implemented Asynchronous NPU Format Handler (NFH) and included C++/Python examples for asynchronous inference with profiling.
- System/Device:
  - PPU Firmware loading is now done upon service initialization.
  - Added PCIe bus number display for dxtop.
  - Added new Python APIs for device configuration and status retrieval.

### DX-Stream (v2.1.0)

**_1. Changed_**

- Performance Optimization: Synchronization was disabled in the Video Sink (secondary mode) for improved performance. Buffer processing was enhanced to use direct buffer manipulation.
- Model/Configuration: Default YOLOv5 model updated from YOLOV5S_3 to YOLOV5S_4. Message conversion settings were simplified, and JSON payload structure was improved.
- Logic/Compatibility: Event handling logic in elements (dxpreprocess, dxinfer, etc.) was modified to align with dxinputselector updates. Dependency installation for Debian 12 was enhanced.

**_2. Fixed_**

- Pipeline Stability: A critical event processing timing issue in dxinputselector that caused compositor pipeline freezes was fixed.
- Setup/Memory: Improved error handling in setup scripts to prevent excessive download retries. Buffer handling in preprocessing/postprocessing pipelines and shutdown signal processing in dx-infer were improved.
- Compatibility: Added detection and installation of Rockchip-specific dependencies (librga-dev).

**_3. Added_**

- PPU Support: Integrated Post-Processing Unit (PPU) functionality for key models (YOLOv5s, SCRFD500M, YOLOv5Pose).
  - This enables NPU-based bounding box decoding and NMS to reduce CPU overhead.
- Performance Analysis: GstShark integration was added, along with documentation and a script for comprehensive pipeline performance evaluation.
- Download Reliability: Setup scripts were enhanced with timeout limits and file integrity verification for more reliable downloads.
- Features/Build: Added preprocess skip functionality for conditional processing and build configuration for v3 architecture.

### DX-APP (v2.1.0)

**_1. Changed_**

- Model Support: Updated model package version from 2.0.0 to 2.1.0 to support PPU models.
- Demos: Improved demo script with additional PPU-Demos (1, 4, 6, 8, 11).
- Dependencies: Added CPU-specific PyTorch wheel source in requirements.txt.
- Documentation/Build: Enhanced build script documentation; updated CMake to use C++17 and v143 (Visual Studio 2022) for Windows builds.

**_2. Fixed_**

- Stability/Correctness: Fixed Windows MSBuild compilation warnings using explicit static_cast. Improved tensor allocation and numBoxes calculation logic.
- Usability: Fixed errors when using VAAPI with camera input. Enhanced application to display final FPS even when terminated during camera usage. Added VSCode configuration files.

**_3. Added_**

- Windows Environment Support: Full support for Windows 10 / 11 has been added, including an automated build script (build.bat) and Visual Studio solution generation.
  - Requires M1 Driver v1.7.1+, Runtime Lib v3.1.0+, Python 3.8+, and Visual Studio 2022.
- PPU Data Types: Added support for three new PPU data types: BBOX (object detection), POSE (pose estimation keypoints), and FACE (face detection landmarks).
- Post-Processing: Enhanced post-processing functions to natively support the PPU inference output format.

**_4. Known Issues_**

- Model Accuracy: DeepLabV3 Semantic Segmentation model accuracy may be slightly degraded (will be fixed in next release).
- PPU Converter: dx-compiler v2.1.0 does not yet support converting face detection and pose estimation models to PPU format.

For detailed updated items, refer to **each module's Release Notes.**

---

## DX-Runtime v2.0.0 / 2025-09-08

- DX_FW : v2.1.4
- NPU Driver : v1.7.1
- DX-RT : v3.0.0
- DX-Stream : v2.0.0
- DX-APP : v2.0.0

---

Here are the **DX-Runtime v2.0.0** Release Notes for each module.

### DX_FW (v2.1.1 ~ v2.1.4)

**_1. Changed:_**

- Implemented a new "stop & go" inference function that splits large tiles for better performance.

**_2. Fixed:_**

- Corrected a QSPI read logic bug to prevent underflow.

**_3. Added:_**

- Weight Data Monitoring: The NPU recover corrupted weight data from the host.
- CLI & Tool Support: Added a CLI command for PCIe/DMA status and a parser for the RX eye measurement tool.

### NPU Driver (v1.6.0 ~ v1.7.1)

**_1. Changed:_**

- Updated various driver and header files.

**_2. Fixed:_**

- Corrected a device identification error and build-related issues.

**_3. Added:_**

- Added a PCIe status command, an uninstall script, and new NPU-related files.

### DX-RT (v3.0.0)

**_1. Changed:_**

- Minimum Versions: Updated minimum versions for the driver, PCIe driver, and firmware.
- Performance: Increased the number of threads for `DeviceOutputWorker` from 3 to 4.
- Build Process: Changed the default build option to `USE_ORT=ON` and updated the compiler to version 14. Added automatic handling of input dummy padding and output dummy slicing when USE_ORT=OFF (build-time or via InferenceOption).

**_2. Fixed:_**

- Resolved a kernel panic issue caused by a wrong NPU channel number.
- Fixed a build error related to Python 3.6.9 incompatibility by adding automatic installation support for Python 3.8.2.

**_3. Added:_**

- Monitoring & Tools: Added a new dxtop monitoring tool and a `dxrt-cli --errorstat` option for PCIe details.
- New Features: Implemented a new USB inference module and Sanity Check features.
- APIs & Examples: Included new Python APIs and examples for configuration and device status.
- Added support for both `.dxnn` file formats: DXNN v6 (compiled with dx_com 1.40.2 or later) and DXNN v7 (compiled with dx_com 2.x.x).

### DX-Stream (v2.0.0)

**_1. Changed:_**

- Code & Compatibility: Post-processing examples are now separated by model for clarity. This version is fully compatible with DX-RT v3.0.0 and now only supports inference for models (DXNN v7) created by DX-COM v2.0.0 or later.
- Build & Logging: The build script now includes OS and architecture checks, and unnecessary print statements have been removed.

**_2. Fixed:_**

- Stability: Fixed a processing delay bug in dx-inputselector and corrected a post-processing logic error for the SCRFD model.
- Error Handling: Improved error handling for setup scripts and fixed a bug in dx_rt that affected multi-tail models.
- Compatibility: Added support for the X11 video sink on Ubuntu 18.04 to improve cross-OS compatibility.

**_3. Added:_**

- Utilities: Introduced a new uninstall.sh script to help clean up project files.

### DX-APP (v2.0.0)

**_1. Changed:_**

- Code Structure: The YOLO post-processing guide was moved to a separate document, and demo applications were extensively refactored and restructured. Common utilities were consolidated, and deprecated code was removed.
- YOLO Post-Processing: The YoloPostProcess now correctly filters tensors by output name when USE_ORT=ON. The yolo_pybind_example.py was refactored to use a RunAsync() + Wait() structure for improved output handling.
- Build & Docs: The build script now includes OS and architecture checks. Documentation was updated to include Python requirements and to add a new YOLOv5s-6 JSON configuration. Command-line help messages were also improved for clarity.

**_2. Fixed:_**

- Bugs: Corrected an FPS calculation bug in yolo_multi and fixed a post-processing logic error to support new YOLO model output shapes when USE_ORT=OFF. A typo in a framebuffer path was also fixed.
- Error Handling: Improved error messages for output tensor size mismatches and missing tensors.
- Compatibility: Removed post-processing code for legacy PPU models.

**_3. Added:_**

- Utilities: Added a uninstall.sh script to clean up installed packages and build artifacts.
- YOLO Features: Added a feature to filter output tensors using a target_output_tensor_name key in the JSON configuration. Post-processing support was also added for YOLO_pose and YOLO_face models when USE_ORT=ON.
- Compatibility: Implemented version guards to ensure compatibility with DX-RT ≥ 3.0.0 and DXNN model version ≥ 7.

For detailed updated items, refer to **each module's Release Notes.**

---

## DX-Runtime v1.0.0 / 2025-07-23

- DX_FW : v2.1.0
- NPU Driver : v1.5.0
- DX-RT : v2.9.5
- DX-Stream : v1.7.0
- DX-APP : v1.11.0

We're excited to announce the **initial release of DX-Runtime v1.0.0.**

---

### What's New?

This v1.0.0 release introduces the foundational capabilities of DX-Runtime:

- **Initial version release of DX-Runtime (DX-RT).** This is the core runtime software for executing `.dxnn` models on DEEPX NPU hardware.
- **Direct NPU Interaction:** DX-RT directly interacts with DEEPX NPU through firmware and device drivers, utilizing PCIe for high-speed data transfer.
- **C/C++ and Python APIs:** Provides APIs for application-level inference control, enabling flexible integration into various projects.
- **Complete Runtime Environment:** Offers comprehensive features including model loading, I/O buffer management, inference execution, and real-time hardware monitoring.
- **Integrated Inference Workflow:** Supports an end-to-end inference flow from input/pre-processing (using OpenCV) to post-processing and display.
- **Configurable Inference Options:** Allows configuration of InferenceOption to specify target devices and available resources for optimized execution.

---
