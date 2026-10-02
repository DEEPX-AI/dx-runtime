# DEEPX DX-Runtime

## DXNN® - DEEPX NPU SDK (DX-AS: DEEPX All-Suite)

**DX-AS (DEEPX All-Suite)** is an integrated environment of frameworks and tools that enables inference and compilation of AI models using DEEPX devices. Users can build the integrated environment by installing individual tools, but DX-AS maintains optimal compatibility by aligning the versions of the individual tools.

![](./docs/source/img/dxnn_sdk_illustration.png)
![](./docs/source/img/dxnn_sdk_illustration_simple.png)

---

### [AI Model Runtime Environment](https://github.com/DEEPX-AI/dx-runtime) (Deployment Platform)

**Purpose**  
  - Must be installed on the Target system where the DEEPX M1 M.2 module is attached and the DEEPX AI model (.dxnn) will be executed.  

**Core Components**
  - DX-RT & DX-FW & NPU Driver: Foundational software for NPU control
  - DX-APP: C++ and Python examples to jump-start your projects
  - DX-Stream: GStreamer integration for seamless multimedia pipelines

**Flexibility & Support**
  - OS: Compatible with Debian-based Linux (Ubuntu 26.04/24.04/22.04/20.04(LTS), Debian 13/12)
  - Architecture: Supports both x86_64 and arm64

**Easy Installation**
  - Our script automates the entire process
  - One-time reboot is required after installation to finalize the NPU Driver setup

**You can install dx-runtime by following the instructions at this [LINK](https://github.com/DEEPX-AI/dx-all-suite/blob/main/docs/source/02_Setting_Up_Environment.md#dx-runtime-installation-rt-driver-fw-app-stream).**

---

## Quick Guide (Install and Run)

DX-Runtime includes source code for each module. The repositories are managed as Git submodules(`dx_rt_npu_linux_driver`, `dx_rt`, `dx_app`, and `dx_stream`) under `./dx-runtime`.  

### Local Installation

DX-Runtime supports installation in local environments. 

You can install DX-Runtime by following the instructions at this [Link](https://github.com/DEEPX-AI/dx-all-suite/blob/main/docs/source/02_Setting_Up_Environment.md#dx-runtime-installation-rt-driver-fw-app-stream)

### Docker Installation

DX-Runtime support installation in docker envirionments.

You can install DX-Runtime by following the instructions at this [Link](https://github.com/DEEPX-AI/dx-all-suite/blob/main/docs/source/02_Setting_Up_Environment.md#docker-installation) 

### One-Line Installation (Runtime-Only)

For a quick setup of just the NPU driver, DX-RT, and DX-FW — without cloning this repository — run:

```bash
curl -fsSL https://raw.githubusercontent.com/DEEPX-AI/dx-runtime/main/oneline-install.sh | sh
```

This installs `dx_rt_npu_linux_driver`, `dx_rt`, and `dx_fw` from the prebuilt binaries on each component's `main` branch, so it always tracks the newest published build. It does **not** cover `dx_app` or `dx_stream` — for those, use the Local or Docker Installation above.

Pin a component instead of tracking `main` with `DX_RT_VERSION`, `DX_DRIVER_VERSION`, or
`DX_FW_VERSION`, e.g. `curl -fsSL ... | DX_RT_VERSION=3.4.0 sh`. `DX_FW_VERSION` covers M1,
M1M and H1 together — the three are released as one firmware set, and H1 ships inside the
M1 version directory. Because the versions are
resolved at run time, the artifacts are not checksum-verified, and the three components
follow their own branches independently — a run between releases may install a combination
that has not been validated together. Use the version pins or `install.sh` when you need a
known-good set.

- If no NPU device is detected, the firmware update step is skipped with a warning; rerun the same command once the device is available.

To remove it again without cloning the repository:
```bash
curl -fsSL https://raw.githubusercontent.com/DEEPX-AI/dx-runtime/main/oneline-uninstall.sh | sh
```
This purges the `dxrt-driver-dkms` and `libdxrt-bin` packages, which is what both install
routes produce, so it removes an `install.sh` install just as well. Firmware already flashed
to the device is not reverted — there is no uninstall path for it — and the `dx_engine` Python
wheel is user-managed, so `libdxrt-bin` leaves it in place and prints how to remove it. For
`dx_app` and `dx_stream`, which the one-liner never installs, use the repository's
`uninstall.sh`.

---

## Create User Manual

### Install Python Dependencies

To install the necessary Python packages, run the following command:

```bash
pip install mkdocs mkdocs-material mkdocs-video pymdown-extensions mkdocs-with-pdf 
```

### Generate Documentation (HTML and PDF)

To generate the user guide as both HTML and PDF files, execute the following command:

```bash
mkdocs build
```

This will create:
- **HTML documentation** in the `docs/` folder - open `docs/index.html` in your web browser
- **PDF file**: `DEEPX_[sub-module]_UM_[version]_[release_date].pdf` in the root directory


