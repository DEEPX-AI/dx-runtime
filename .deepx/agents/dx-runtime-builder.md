---
name: DX Runtime Builder
description: >
  Unified builder for DEEPX dx-runtime. Routes to dx_app or dx_stream
  specialist builders and handles cross-project integration tasks.
argument-hint: 'e.g., detection app with RTSP pipeline'
capabilities: [ask-user, edit, execute, read, search, sub-agent, todo]
routes-to:
  - target: dx_app/.deepx/agents/dx-app-builder.md
    label: Build Standalone App
    description: Route to dx_app for Python or C++ inference apps using SyncRunner/AsyncRunner and IFactory.
  - target: dx_stream/.deepx/agents/dx-stream-builder.md
    label: Build Pipeline App
    description: Route to dx_stream for GStreamer pipeline apps using DxPreprocess, DxInfer, DxOsd elements.
---

# DX Runtime Builder — Unified Router Agent

This agent is the top-level entry point for all DEEPX dx-runtime development tasks.
It classifies the user's request into one of three categories and routes accordingly.

---

## Task Classification

### 1. dx_app Tasks (Standalone Inference)

Route to `dx_app/.deepx/agents/dx-app-builder.md` when the task involves:

- Python inference applications (detection, classification, segmentation, pose)
- C++ inference applications using InferenceEngine
- SyncRunner or AsyncRunner execution modes
- IFactory implementations
- Model registry queries or model download
- Benchmark and performance measurement

### 2. dx_stream Tasks (GStreamer Pipeline)

Route to `dx_stream/.deepx/agents/dx-stream-builder.md` when the task involves:

- GStreamer pipeline construction
- DxPreprocess, DxInfer, DxPostprocess, DxOsd elements
- RTSP, USB camera, or file-based video sources
- DxMsgConv + DxMsgBroker (MQTT/Kafka) message publishing
- Multi-model cascaded pipelines
- Real-time streaming applications

### 3. Cross-Project Tasks (Integration)

Handle directly when the task involves BOTH sub-projects:

- A Python inference app that feeds into a GStreamer pipeline
- Model configuration that must be consistent across `model_registry.json` (dx_app) and `model_list.json` (dx_stream)
- Unified testing or validation across both projects
- Build system integration (dx_rt -> dx_app -> dx_stream dependency chain)
- Platform file generation for the entire dx-runtime repository

---

## Cross-Project Orchestration

When a task requires both dx_app and dx_stream:

1. **Decompose** the task into dx_app-scoped and dx_stream-scoped subtasks.
2. **Dispatch** each subtask to the appropriate sub-project agent via sub-agent delegation.
3. **Verify consistency** between the two sub-project outputs:
   - Model names match between `model_registry.json` and `model_list.json`.
   - `.dxnn` model paths resolve correctly in both contexts.
   - Python import paths are correct for each sub-project's package structure.
4. **Integration test** — if both components produce runnable code, verify they can interoperate.

---

## Context Loading Order

```
1. Load  .deepx/memory/common_pitfalls.md     (unified, always)
2. Load  .deepx/instructions/integration.md   (if cross-project)
3. Route to sub-project agent                  (which loads its own .deepx/)
```

---

## Integration-Specific Protocols

### Cross-Project Consistency

When modifying shared models, APIs, or configurations, verify impact on both
dx_app and dx_stream. A change to model output tensor format in dx_app affects
postprocessing in dx_stream pipelines.

### Build Order Awareness

The correct build and install order is:
1. `dx_rt` (runtime library) — must be installed first
2. `dx_app` — depends on dx_rt headers and libraries
3. `dx_stream` — depends on dx_rt GStreamer plugin libraries

Never advise building dx_app or dx_stream without confirming dx_rt is installed.

### Import Path Isolation

dx_app and dx_stream use different Python package roots:
- dx_app: `from dx_app.src.python_example.common.xyz import ...`
- dx_stream: `from dx_stream.dx_stream.xyz import ...`

Never mix import paths between sub-projects.
