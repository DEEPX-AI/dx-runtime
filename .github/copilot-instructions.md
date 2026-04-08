# DEEPX dx-runtime — Copilot Global Instructions

> Unified entry point for the 3-level DEEPX knowledge base architecture.

## Response Language

Match your response language to the user's prompt language — when asking questions
or responding, use the same language the user is using.

## Knowledge Base Architecture

| Level | Path | Scope |
|---|---|---|
| **dx_app** | `dx_app/.deepx/` | Standalone inference apps (Python/C++) |
| **dx_stream** | `dx_stream/.deepx/` | GStreamer pipeline apps |
| **dx-runtime** | `.deepx/` | Cross-project integration layer |

**If working on dx_app code** — read `dx_app/.deepx/` skills and toolsets.
**If working on dx_stream code** — read `dx_stream/.deepx/` skills and toolsets.
**If working across both** — read `.deepx/instructions/integration.md`.

## Quick Reference

```bash
cd dx_app && ./install.sh && ./build.sh
cd dx_stream && ./install.sh
cd dx_app && ./setup.sh
cd dx_stream && ./setup.sh
cd dx_app && pytest tests/ -m "not npu_required"
cd dx_stream && pytest test/ -m "not npu_required"
python .deepx/scripts/validate_framework.py
```

## All Skills

| Command | Description | Sub-project |
|---------|-------------|-------------|
| /dx-build-python-app | Build Python inference app (4 variants) | dx_app |
| /dx-build-cpp-app | Build C++ inference app | dx_app |
| /dx-build-async-app | Build async high-performance app | dx_app |
| /dx-build-pipeline-app | Build GStreamer pipeline app | dx_stream |
| /dx-build-mqtt-kafka-app | Build message broker pipeline app | dx_stream |
| /dx-validate-and-fix | Full feedback loop: validate, collect, approve, apply, verify | dx-runtime |
| /dx-brainstorm-and-plan | Process: collaborative design session before code generation | all levels |
| /dx-tdd | Process: test-driven development — validate each file immediately after creation | all levels |
| /dx-verify-completion | Process: verify before claiming completion — evidence before assertions | all levels |

## Unified Context Routing Table

| If the task mentions... | Sub-project | Read these files |
|---|---|---|
| **Python app, detection, factory** | dx_app | `dx_app/.deepx/skills/dx-build-python-app.md` |
| **C++ app, native, performance** | dx_app | `dx_app/.deepx/skills/dx-build-cpp-app.md` |
| **Async, high-throughput, batch** | dx_app | `dx_app/.deepx/skills/dx-build-async-app.md` |
| **Model, download, registry** | dx_app | `dx_app/.deepx/skills/dx-model-management.md` |
| **GStreamer, pipeline, stream** | dx_stream | `dx_stream/.deepx/skills/dx-build-pipeline-app.md` |
| **MQTT, Kafka, message broker** | dx_stream | `dx_stream/.deepx/skills/dx-build-mqtt-kafka-app.md` |
| **Cross-project, integration** | dx-runtime | `.deepx/instructions/integration.md` |
| **Validation, feedback, fix** | dx-runtime | `.deepx/skills/dx-validate-and-fix.md` |
| **ALWAYS read (every task)** | dx-runtime | `.deepx/memory/common_pitfalls.md` |

## Critical Conventions

### Universal
1. **Logging**: `logging.getLogger(__name__)` — never bare `print()`
2. **NPU check**: `dxrt-cli -s` before any NPU operation
3. **No hardcoded model paths**: From CLI args or registry

### dx_app
4. **Factory pattern**: All Python apps implement IFactory (5 methods)
5. **Absolute imports**: `from dx_app.src.python_example.common.xyz import ...`
6. **CLI args**: `parse_common_args()` for all entry points

### dx_stream
7. **preprocess-id matching**: DxPreprocess and DxInfer share the same ID
8. **Queue elements**: `queue` between every processing stage
9. **DxRate for RTSP**: Always rate-limit RTSP sources

## Hardware

| Architecture | Value |
|---|---|
| DX-M1 | `dx_m1` |
| DX-M1A | `dx_m1a` |

## Python Imports

```python
from dx_app.src.python_example.common.runner.args import parse_common_args
from dx_app.src.python_example.common.runner.factory_runner import FactoryRunner
import logging
logger = logging.getLogger(__name__)
```

## Testing

```bash
cd dx_app && pytest tests/ -m "not npu_required"
cd dx_stream && pytest test/ -m "not npu_required"
python .deepx/scripts/validate_framework.py
```
