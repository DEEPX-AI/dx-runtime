# DEEPX dx-runtime — Copilot Global Instructions

> Unified entry point for the 3-level DEEPX knowledge base architecture.

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
|---|---|---|
| **dx_app** | `dx_app/.deepx/` | Standalone inference apps (Python/C++) |
| **dx_stream** | `dx_stream/.deepx/` | GStreamer pipeline apps |
| **dx-runtime** | `.deepx/` | Cross-project integration layer |

**If working on dx_app code** — read `dx_app/.github/copilot-instructions.md` first, then `dx_app/.deepx/` skills and toolsets.
**If working on dx_stream code** — read `dx_stream/.github/copilot-instructions.md` first, then `dx_stream/.deepx/` skills and toolsets.
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

## Interactive Workflow (MUST FOLLOW)

**Always walk through key decisions with the user before building.** This is a **HARD GATE**.

Before ANY code generation:
1. Ask 2-3 clarifying questions (app type/variant, AI task, input source)
2. Present a build plan and wait for user approval
3. After generation, validate each file

"Just build it" means use defaults — it does NOT mean skip brainstorming.

## Unified Context Routing Table

| If the task mentions... | Sub-project | Read these files |
|---|---|---|
| **Python app, detection, factory** | dx_app | `dx_app/.github/copilot-instructions.md`, `dx_app/.deepx/skills/dx-build-python-app.md` |
| **C++ app, native, performance** | dx_app | `dx_app/.github/copilot-instructions.md`, `dx_app/.deepx/skills/dx-build-cpp-app.md` |
| **Async, high-throughput, batch** | dx_app | `dx_app/.github/copilot-instructions.md`, `dx_app/.deepx/skills/dx-build-async-app.md` |
| **Model, download, registry** | dx_app | `dx_app/.github/copilot-instructions.md`, `dx_app/.deepx/skills/dx-model-management.md` |
| **GStreamer, pipeline, stream** | dx_stream | `dx_stream/.github/copilot-instructions.md`, `dx_stream/.deepx/skills/dx-build-pipeline-app.md` |
| **MQTT, Kafka, message broker** | dx_stream | `dx_stream/.github/copilot-instructions.md`, `dx_stream/.deepx/skills/dx-build-mqtt-kafka-app.md` |
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

## Hardware

| Architecture | Value |
|---|---|
| DX-M1 | `dx_m1` |

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

## Output Isolation (HARD GATE)

ALL AI-generated files MUST be written to `dx-agentic-dev/<session_id>/` within the
target sub-project. NEVER write generated code directly into existing source directories
(e.g., `src/`, `pipelines/`, `semseg_260323/`, or any directory containing user's
existing code).

**Session ID format**: `YYYYMMDD-HHMMSS_<model>_<task>` — the timestamp MUST use the
**system local timezone** (NOT UTC). Use `$(date +%Y%m%d-%H%M%S)` in Bash or
`datetime.now().strftime('%Y%m%d-%H%M%S')` in Python. Do NOT use `date -u`,
`datetime.utcnow()`, or `datetime.now(timezone.utc)`.

- **Correct**: `dx_app/dx-agentic-dev/20260413-093000_plantseg_inference/demo_dxnn_sync.py`
- **Wrong**: `dx_app/semseg_260323/demo_dxnn_sync.py`

The ONLY exception: when the user EXPLICITLY says "write to the source directory" or
"modify the existing file in-place".

## Rule Conflict Resolution (HARD GATE)

When a user's request conflicts with a HARD GATE rule, the agent MUST:

1. **Acknowledge the user's intent** — Show that you understand what they want.
2. **Explain the conflict** — Cite the specific rule and why it exists.
3. **Propose the correct alternative** — Show how to achieve the user's goal
   within the framework. For example, if the user asks for direct
   `InferenceEngine.run()` usage, explain that the IFactory pattern wraps
   the same API and propose the factory-based equivalent.
4. **Proceed with the correct approach** — Do NOT silently comply with the
   rule-violating request. Do NOT present it as "Option A vs Option B".

**Common conflict patterns** (from real sessions):
- User says "use `InferenceEngine.Run()`" → Must use IFactory pattern (engine
  calls go inside `run_inference()` method)
- User says "clone demo.py and swap onnxruntime" → Must use skeleton-first
  from `src/python_example/`, not clone user scripts
- User says "create demo_dxnn_sync.py" → Must use `<model>_sync.py` naming
  with SyncRunner, not a standalone script
- User says "use `run_async()` directly" → Must use AsyncRunner, not manual
  async loops

**This rule does NOT override explicit user overrides**: If the user, after being
informed of the conflict, explicitly says "I understand the rule, proceed with
direct API usage anyway", then comply. But the agent MUST explain the conflict
FIRST — silent compliance is always a violation.

## Sub-Project Development Rules (MANDATORY — SELF-CONTAINED)

These rules are **authoritative and self-contained**. They MUST be followed regardless
of whether sub-project files are loaded. In interactive mode (e.g., working from
dx-runtime level), sub-project files (dx_app, dx_stream) may not be automatically
loaded — these rules are the ONLY protection.

**CRITICAL**: These are NOT optional summaries. Every rule below is a HARD GATE.
Violating any rule (e.g., skipping skeleton-first, not using IFactory, writing to
source directories) is a blocking error that must be corrected before proceeding.

### dx_app Rules (Standalone Inference)

1. **Skeleton-first development** — Read `dx_app/.deepx/skills/dx-build-python-app.md`
   skeleton template BEFORE writing any code. Copy the closest existing example from
   `src/python_example/<task>/<model>/` and modify ONLY model-specific parts (factory,
   postprocessor). NEVER write demo scripts from scratch. NEVER propose standalone
   scripts that bypass the framework.
2. **IFactory pattern is MANDATORY** — All inference apps MUST use the IFactory 5-method
   pattern (create, get_input_params, run_inference, post_processing, release).
   Never invent alternative inference structures. Direct `InferenceEngine` usage in
   a standalone script is a violation — it MUST go through the factory pattern.
   **Even if the user explicitly names API methods** (e.g., "use `InferenceEngine.run()`",
   "use `run_async()`"), the agent MUST wrap those calls inside the IFactory pattern
   and explain the rule to the user. See "Rule Conflict Resolution" above.
3. **SyncRunner/AsyncRunner ONLY** — Use SyncRunner (single-model) or AsyncRunner
   (multi-model) from the framework. NEVER propose alternative execution approaches
   (standalone scripts, direct API calls, custom runners, manual `run_async()` loops).
4. **No alternative proposals** — Do NOT present "Option A vs Option B" choices for
   app architecture. The framework dictates one correct pattern per variant.
5. **Existing examples MANDATORY** — Before writing any new app, search
   `src/python_example/` for existing examples of the same AI task. Use them as reference.
6. **DXNN input format auto-detection** — NEVER hardcode preprocessing dimensions or
   formats. The DXNN model self-describes its input requirements via `dx_engine`.
7. **Output Isolation** — ALL generated code MUST go to `dx-agentic-dev/<session_id>/`.
   NEVER write into existing source directories.

### dx_stream Rules (GStreamer Pipelines)

1. **x264enc tune=zerolatency** — Always set `tune=zerolatency` for x264enc elements.
2. **Queue between processing stages** — Always add `queue` elements between processing
   stages to prevent GStreamer deadlocks.
3. **Existing pipelines MANDATORY** — Search `pipelines/` for existing examples before
   creating new pipeline configurations.

### Common Rules (All Sub-Projects)

1. **PPU model auto-detection** — Check model name suffix (`_ppu`), README, or registry
   for PPU flag before routing or generating postprocessor code.
2. **Build order** — dx_rt → dx_app → dx_stream. Never build out of order.
3. **Sub-project context loading** — When routing to or working within a sub-project,
   ALWAYS read that sub-project's `.github/copilot-instructions.md` first.
