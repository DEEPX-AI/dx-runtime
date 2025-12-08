# DEEPX DX-Runtime

## DXNN® - DEEPX NPU SDK (DX-AS: DEEPX All-Suite)

**DX-AS (DEEPX All-Suite)** is an integrated environment of frameworks and tools that enables inference and compilation of AI models using DEEPX devices. Users can build the integrated environment by installing individual tools, but DX-AS maintains optimal compatibility by aligning the versions of the individual tools.

![](./docs/source/img/deepx_dxnn_sdk_simple.png)
![](./docs/source/img/dxnn-workflow.png)

---

### [AI Model Runtime Environment](https://github.com/DEEPX-AI/dx-runtime) (Deployment Platform)

**Purpose**  
  - Must be installed on the Target system where the DEEPX M1 M.2 module is attached and the DEEPX AI model (.dxnn) will be executed.  

**Core Components**
  - DX-RT & DX-FW & NPU Driver: Foundational software for NPU control
  - DX-APP: C++ and Python examples to jump-start your projects
  - DX-Stream: GStreamer integration for seamless multimedia pipelines

**Flexibility & Support**
  - OS: Compatible with Debian-based Linux (Ubuntu 20.04, 22.04, 24.04)
  - Architecture: Supports both x86_64 and arm64

**Easy Installation**
  - Our script automates the entire process
  - One-time reboot is required after installation to finalize the NPU Driver setup

**You can install dx-runtime by following the instructions at this [LINK](https://github.com/DEEPX-AI/dx-all-suite/blob/staging/docs/source/installation.md#install-dx-runtime-environment).**

---

## Quick Guide (Install and Run)

DX-Runtime includes source code for each module. The repositories are managed as Git submodules(`dx_rt_npu_linux_driver`, `dx_rt`, `dx_app`, and `dx_stream`) under `./dx-runtime`.  

### Local Installation

DX-Runtime supports installation in local environments. 
You can install DX-Compiler by following the instructions at this [Link](https://github.com/DEEPX-AI/dx-all-suite/blob/main/docs/source/installation.md#install-dx-runtime-environment)

### Docker Installation

DX-Runtime support installation in docker envirionments.
You can install DX-Compiler by following the instructions at this [Link](https://github.com/DEEPX-AI/dx-all-suite/blob/main/docs/source/installation.md#install-dx-compiler-dx-runtime-and-dx-modelzoo-environment) 


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


