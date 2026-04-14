# DEEPX dx-runtime — Claude Code Entry Point

> Unified entry point for the 3-level knowledge base architecture.

## Response Language

Match your response language to the user's prompt language — when asking questions
or responding, use the same language the user is using.

**Technical term rule**: When responding in Korean, keep English technical terms in
their original English form. Do NOT transliterate English terms into Korean phonetics
(한글 음차 표기 금지). Established Korean loanwords (모델, 서버, 파일, 데이터) are acceptable.

## Recommended Model (Pre-Flight Check)

DX Agentic Development requires strong instruction following and knowledge base
utilization. Before starting any task, check if you are running as one of the
recommended models:

- **Claude Sonnet 4.6** or later
- **Claude Opus 4.6** or later

If you are NOT one of these models (e.g., GPT-4.1, GPT-4o, Gemini, etc.),
output the following notice at the beginning of your first response:

```
══════════════════════════════════════════════════════════════
⚠  DX-AGENTIC-DEV: MODEL NOTICE

DX Agentic Development recommends Claude Sonnet 4.6+ or
Opus 4.6+. Your current model may produce lower quality
in instruction following, knowledge base utilization, and
API accuracy. Please switch to a recommended model.
══════════════════════════════════════════════════════════════
```

After the box notice, proceed with the task normally. This is an informational
warning, not a blocking gate.

### Model Notice Repeat (Non-Recommended Model Only)

If you output the MODEL NOTICE box above (i.e., you are NOT a recommended model),
you MUST also output this shortened reminder **immediately before the actual question
line** that the user needs to answer — NOT at the beginning of the brainstorming flow.

**Timing**: After all file reading, context analysis, and preamble text, right before
the line that contains the `?` (the actual question), insert this reminder:

```
---
⚠ **Non-recommended model** — output quality may be degraded. Recommended: Claude Sonnet 4.6+ / Opus 4.6+
---
```

**Example — WRONG** (repeat scrolls past with the box):
```
[DX-AGENTIC-DEV: START]
══ MODEL NOTICE ══
---  ⚠ Non-recommended model ---     ← TOO EARLY, scrolls past
... (reads files, analyzes context) ...
First question: ...?
```

**Example — CORRECT** (repeat appears right before the question):
```
[DX-AGENTIC-DEV: START]
══ MODEL NOTICE ══
... (reads files, analyzes context) ...
---  ⚠ Non-recommended model ---     ← RIGHT BEFORE the question
First question: ...?
```

Only output this reminder ONCE (before the first question), not before every question.

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

**Always walk through key decisions with the user before building.** This is a **HARD GATE**.

Ask 2-3 targeted questions to confirm app type, features, and input source. This creates
a collaborative workflow and catches misunderstandings early. Only skip questions if the
user explicitly says "just build it" or "use defaults" — but even then, present a build
plan and wait for confirmation before generating code.

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

### Process Skills (available at every level)

| Command | Description |
|---------|-------------|
| /dx-brainstorm-and-plan | Brainstorm and plan before any code generation |
| /dx-tdd | Test-driven development — validate each file immediately after creation |
| /dx-verify-completion | Verify before claiming completion — evidence before assertions |

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
| **Brainstorm, plan, design** | all levels | `.deepx/skills/dx-brainstorm-and-plan.md` |
| **TDD, validation, incremental** | all levels | `.deepx/skills/dx-tdd.md` |
| **Completion, verify, evidence** | all levels | `.deepx/skills/dx-verify-completion.md` |

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

## No Placeholder Code (MANDATORY)

NEVER generate stub/placeholder code. This includes:
- Commented-out imports: `# from dxnn_sdk import InferenceEngine`
- Fake results: `result = np.zeros(...)`
- TODO markers: `# TODO: implement actual inference`
- "Similar to sync version" without actual async implementation

All generated code MUST be functional, using real APIs from the knowledge base.
If the required SDK/API is unknown, read the relevant skill document first.

## Experimental Features — Prohibited

Do NOT offer, suggest, or implement experimental or non-existent features. This includes:
- "웹 기반 비주얼 컴패니언" (web-based visual companion)
- Local URL-based diagram viewers or dashboards
- Any feature requiring the user to open a local URL for visualization
- Any capability that does not exist in the current toolset

**Superpowers brainstorming skill override**: The superpowers `brainstorming` skill
includes a "Visual Companion" step (step 2 in its checklist). This step MUST be
SKIPPED in the DEEPX project. The visual companion does not exist in our environment.
When the brainstorming checklist says "Offer visual companion", skip it and proceed
directly to "Ask clarifying questions" (step 3).

If a feature does not exist, do not pretend it does. Stick to proven, documented
capabilities only.

**Autopilot / autonomous mode override**: When the user is absent (autopilot mode,
auto-response "work autonomously", or `--yolo` flag), the brainstorming skill's
"Ask clarifying questions" step MUST be replaced with "Make default decisions per
knowledge base rules". Do NOT call `ask_user` — skip straight to producing the
brainstorming spec using knowledge base defaults. All subsequent gates (spec review,
plan, TDD, mandatory artifacts, execution verification) still apply without exception.

## Brainstorming — Spec Before Plan (HARD GATE)

When using the superpowers `brainstorming` skill or `/dx-brainstorm-and-plan`:

1. **Spec document is MANDATORY** — Before transitioning to `writing-plans`, a spec
   document MUST be written to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`.
   Skipping the spec and going directly to plan writing is a violation.
2. **User approval gate is MANDATORY** — After writing the spec, the user MUST review
   and approve it before proceeding to plan writing. Do NOT treat unrelated user
   responses (e.g., answering a different question) as spec approval.
3. **Plan document MUST reference the spec** — The plan header must include a link
   to the approved spec document.
4. **Prefer `/dx-brainstorm-and-plan`** — Use the project-level brainstorming skill
   instead of the generic superpowers `brainstorming` skill. The project-level skill
    has domain-specific questions and pre-flight checks.

## Autopilot Mode Guard (MANDATORY)

When the user is absent — autopilot mode, `--yolo` flag, or system auto-response
"The user is not available to respond" — the following rules apply:

1. **"Work autonomously" means "follow all rules without asking", NOT "skip rules".**
   Every mandatory gate still applies: brainstorming spec, plan, TDD, mandatory
   artifacts, execution verification, and self-verification checks.
2. **Do NOT call `ask_user`** — Make decisions using knowledge base defaults and
   documented best practices. Calling `ask_user` in autopilot wastes a turn and
   the auto-response does not grant permission to bypass any gate.
3. **User approval gate adaptation** — In autopilot, the spec approval gate is
   satisfied by writing the spec and self-reviewing it against the knowledge base.
   Do NOT skip the spec entirely.
4. **setup.sh FIRST** — Generate infrastructure artifacts (`setup.sh`, `config.json`)
   before writing any application code. This is especially critical in autopilot
   because there is no human to catch missing dependencies.
5. **Execution verification is NOT optional** — Run the generated code and verify it
   works before declaring completion. In autopilot, there is no user to catch errors.

## Hardware

| Architecture | Value | Use case |
|---|---|---|
| DX-M1 | `dx_m1` | Full performance NPU |

## Memory

Persistent knowledge in `.deepx/memory/`. Read at task start, update when learning.
The unified `common_pitfalls.md` contains entries tagged [UNIVERSAL], [DX_APP], [DX_STREAM], and [INTEGRATION].

## Git Safety — Superpowers Artifacts

**NEVER `git add` or `git commit` files under `docs/superpowers/`.** These are temporary
planning artifacts generated by the superpowers skill system (specs, plans). They are
`.gitignore`d, but some tools may bypass `.gitignore` with `git add -f`. Creating the
files is fine — committing them is forbidden.

## Session Sentinels (MANDATORY for Automated Testing)

When processing a user prompt, output these exact markers for automated session
boundary detection by the test harness:

- **First line of your response**: `[DX-AGENTIC-DEV: START]`
- **Last line after ALL work is complete**: `[DX-AGENTIC-DEV: DONE (output-dir: <relative_path>)]`
  where `<relative_path>` is the session output directory (e.g., `dx-agentic-dev/20260409-143022_yolo26n_detection/`)

Rules:
1. **CRITICAL — Output `[DX-AGENTIC-DEV: START]` as the absolute first line of your
   first response.** This must appear before ANY other text, tool calls, or reasoning.
   Even if the user instructs you to "just proceed" or "use your own judgment",
   the START sentinel is non-negotiable — automated tests WILL fail without it.
2. Output `[DX-AGENTIC-DEV: DONE (output-dir: <path>)]` as the very last line after all work, validation,
   and file generation is complete
3. If you are a **sub-agent** invoked via handoff/routing from a higher-level agent,
   do NOT output these sentinels — only the top-level agent outputs them
4. If the user sends multiple prompts in a session, output START/DONE for each prompt
5. The `output-dir` in DONE must be the relative path from the project root to the
   session output directory. If no files were generated, omit the `(output-dir: ...)` part.
6. **NEVER output DONE after only producing planning artifacts** (specs, plans, design
   documents). DONE means all deliverables are produced — implementation code, scripts,
   configs, and validation results. If you completed a brainstorming or planning phase
   but have not yet implemented the actual code, do NOT output DONE. Instead, proceed
   to implementation or ask the user how to proceed.
7. **Pre-DONE mandatory deliverable check**: Before outputting DONE, verify that all
   mandatory deliverables exist in the session directory. If any mandatory file is
   missing, create it before outputting DONE. Each sub-project defines its own mandatory
   file list in its skill document (e.g., `dx-build-pipeline-app.md` File Creation Checklist).
8. **Session HTML export guidance** (Copilot CLI only): Immediately before the DONE
   sentinel line, output: `To save this session as HTML, type: /share html`
   — this tells the user they can preserve the full conversation. The `/share html`
   command is specific to GitHub Copilot CLI; it does not work in Claude Code,
   Copilot Chat (VS Code), or OpenCode. The test harness (`test.sh`) will automatically
   detect and copy the exported HTML file to the session output directory.

## Plan Output (MANDATORY)

When generating a plan document (e.g., via writing-plans or brainstorming skills),
**always print the full plan content in the conversation output** immediately after
saving the file. Do NOT only mention the file path — the user should be able to
review the plan directly in the prompt without opening a separate file.
