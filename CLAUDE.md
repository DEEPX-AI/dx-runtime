# DEEPX dx-runtime — Claude Code Entry Point

> Unified entry point for the 3-level knowledge base architecture.

## Knowledge Base Architecture

| Level | Path | Scope |
|-------|------|-------|
| **dx_app** | `dx_app/.deepx/` | Standalone inference (Python/C++, IFactory, SyncRunner/AsyncRunner) |
| **dx_stream** | `dx_stream/.deepx/` | GStreamer pipelines (13 elements, 6 pipeline categories) |
| **dx-runtime** (this) | `.deepx/` | Integration layer — cross-project patterns, unified routing |

Each sub-project is **self-contained**. This layer adds cross-project orchestration only.

## Routing Logic

Read the entry point that matches your task scope:

| Working on... | Read first |
|---|---|
| dx_app code (Python/C++ inference, IFactory, runners) | `dx_app/CLAUDE.md` |
| dx_stream code (GStreamer pipelines, DxInfer, DxOsd) | `dx_stream/CLAUDE.md` |
| Cross-project integration (shared models, build order, unified testing) | This file + `.deepx/instructions/integration.md` |
| Unsure which sub-project | This file — use the Unified Context Routing Table below |

## Interactive Workflow (MUST FOLLOW)

**Always walk through key decisions with the user before building.** Ask 2-3 targeted
questions to confirm app type, features, and input source. This creates a collaborative
workflow and catches misunderstandings early. Only skip questions if the user explicitly
says "just build it" or "use defaults".

## Quick Reference

```bash
# dx_app
dx_app/install.sh && dx_app/build.sh   # Build C++ and pybind11 bindings
dx_app/setup.sh                        # Download models and test media

# dx_stream
dx_stream/install.sh                   # Install GStreamer plugin bindings
dx_stream/setup.sh                     # Download sample models and videos

# Verification
dxrt-cli -s                            # Verify NPU availability
gst-inspect-1.0 dxinfer                # Verify DxInfer plugin is registered
```

## All Skills (merged)

### dx_app Skills

| Command | Description |
|---------|-------------|
| /dx-build-python-app | Build Python inference app (sync, async, cpp_postprocess, async_cpp_postprocess) |
| /dx-build-cpp-app | Build C++ inference app with InferenceEngine |
| /dx-build-async-app | Build async high-performance inference app |

### dx_stream Skills

| Command | Description |
|---------|-------------|
| /dx-build-pipeline-app | Build GStreamer pipeline app (6 categories: single-model, multi-model, cascaded, tiled, parallel, broker) |
| /dx-build-mqtt-kafka-app | Build MQTT/Kafka message broker pipeline app |

### Shared Skills

| Command | Description |
|---------|-------------|
| /dx-model-management | Download, register, and configure .dxnn models |
| /dx-validate | Run validation checks at every phase gate |
| /dx-validate-and-fix | Full feedback loop: validate, collect, approve, apply, verify |

## Unified Context Routing Table

Based on what the task involves, read **only** the matching rows:

| If the task mentions... | Sub-project | Read these files |
|---|---|---|
| **Python app, inference, factory** | dx_app | `dx_app/.deepx/skills/dx-build-python-app.md`, `dx_app/.deepx/toolsets/common-framework-api.md` |
| **C++ app, native, InferenceEngine** | dx_app | `dx_app/.deepx/skills/dx-build-cpp-app.md`, `dx_app/.deepx/toolsets/dx-engine-api.md` |
| **Async, performance, throughput** | dx_app | `dx_app/.deepx/skills/dx-build-async-app.md`, `dx_app/.deepx/memory/performance_patterns.md` |
| **Pipeline, GStreamer, stream** | dx_stream | `dx_stream/.deepx/skills/dx-build-pipeline-app.md`, `dx_stream/.deepx/toolsets/dx-stream-elements.md` |
| **Multi-model, cascaded, tiled** | dx_stream | `dx_stream/.deepx/skills/dx-build-pipeline-app.md`, `dx_stream/.deepx/toolsets/dx-stream-metadata.md` |
| **MQTT, Kafka, message broker** | dx_stream | `dx_stream/.deepx/skills/dx-build-mqtt-kafka-app.md`, `dx_stream/.deepx/toolsets/dx-stream-elements.md` |
| **Model, download, registry** | shared | `dx_app/.deepx/skills/dx-model-management.md`, `dx_app/.deepx/toolsets/model-registry.md` |
| **Validation, testing** | shared | `dx_app/.deepx/skills/dx-validate.md`, `dx_app/.deepx/instructions/testing-patterns.md` |
| **Validation, feedback, fix** | dx-runtime | `.deepx/skills/dx-validate-and-fix.md`, `.deepx/knowledge/feedback_rules.yaml` |
| **Cross-project, integration** | dx-runtime | `.deepx/instructions/integration.md`, `.deepx/instructions/agent-protocols.md` |
| **ALWAYS read (every task)** | dx-runtime | `.deepx/memory/common_pitfalls.md` |

## Python Imports (dx_app)

```python
from dx_app.src.python_example.common.runner.args import parse_common_args
from dx_app.src.python_example.common.runner.factory_runner import FactoryRunner
from dx_app.src.python_example.common.utils.model_utils import load_model_config
import logging

logger = logging.getLogger(__name__)
```

## Critical Conventions

### Universal

1. **Absolute imports**: `from dx_app.src.python_example.common.xyz import ...`
2. **Logging**: `logging.getLogger(__name__)` — no bare `print()`
3. **No hardcoded model paths**: All model paths from CLI args, model_registry.json, or model_list.json
4. **Skill doc is sufficient**: Read skill doc first. Do NOT read source code unless skill is insufficient.
5. **NPU check**: `dxrt-cli -s` before any inference operation

### dx_app Specific

6. **Factory pattern**: All apps implement IFactory with 5 methods (`create_preprocessor`, `create_postprocessor`, `create_visualizer`, `get_model_name`, `get_task_type`)
7. **CLI args**: Use `parse_common_args()` from `common/runner/args.py`
8. **4 variants**: Python apps have sync, async, sync_cpp_postprocess, async_cpp_postprocess

### dx_stream Specific

9. **preprocess-id matching**: Every `DxPreprocess` / `DxInfer` pair must share the same `preprocess-id`
10. **Queue elements**: Place `queue` between every GStreamer processing stage
11. **DxRate for RTSP**: Always insert `DxRate rate=<fps>` after RTSP sources
12. **DxMsgConv before DxMsgBroker**: Always serialize metadata before publishing

### Integration

13. **Build order**: dx_app first, then dx_stream (dx_stream links against dx_app libraries)
14. **Shared .dxnn models**: Both sub-projects share `dx_app/config/model_registry.json` as the single source of truth
15. **Import paths**: dx_stream may import from dx_app — never the reverse
16. **PPU model auto-detection**: When working with compiled .dxnn models, auto-detect PPU by checking model name suffix (`_ppu`), `model_registry.json` `csv_task: "PPU"`, or user context. PPU models use simplified postprocessing — no separate NMS needed.
17. **Existing example search**: Before generating any new example code, always search for existing examples. If found, present the user with options: (a) explain existing only, or (b) create new based on existing. Never silently overwrite.

## Hardware

| Architecture | Value | Use case |
|---|---|---|
| DX-M1 | `dx_m1` | Full performance NPU |
| DX-M1A | `dx_m1a` | Extended variant |

## Memory

Persistent knowledge in `.deepx/memory/`. Read at task start, update when learning.
The unified `common_pitfalls.md` contains entries tagged [UNIVERSAL], [DX_APP], [DX_STREAM], and [INTEGRATION].
