# AI-Powered Development — dx-runtime Guide

## Overview

dx-runtime is the **integration layer** that orchestrates agentic development across
the DEEPX software stack. It unifies **dx_app** (standalone inference) and **dx_stream**
(GStreamer pipelines) under a single knowledge base, validation system, and feedback loop.

When you invoke an agent at the dx-runtime level, it acts as a **unified router** —
it determines which sub-project the request belongs to, loads the appropriate skill,
and delegates to the correct builder.

## How It Works — CLAUDE.md and the `.deepx/` Knowledge Base

Every project in the dx stack follows a two-layer architecture:

1. **`CLAUDE.md` / `AGENTS.md`** — the IDE entry point. Claude Code reads `CLAUDE.md`;
   OpenCode reads `AGENTS.md` (a verbatim copy). Both contain environment setup, import
   conventions, the context routing table, and pointers into `.deepx/`.
2. **`.deepx/`** — the actual knowledge base. Holds agents, skills, toolsets,
   instructions, memory, scripts, and structured knowledge (YAML). Agents read
   `.deepx/` files for context — **not source code**.

`CLAUDE.md` stays small and stable. `.deepx/` evolves as the project grows. Agents
load only the files they need via the context routing table, keeping token usage low.

## Supported AI Tools

Four AI coding tools are supported. Each auto-loads the `.deepx/` knowledge base
through its own configuration files.

| Tool | Type | Config Files | Agent Invocation |
|---|---|---|---|
| **Claude Code** | CLI | `CLAUDE.md` | Free-form conversation; routing table dispatches |
| **GitHub Copilot** | VS Code | `.github/copilot-instructions.md`, `.github/agents/`, `.github/instructions/` | `@agent-name "prompt"` |
| **Cursor** | IDE | `.cursor/rules/*.mdc` | Free-form conversation; rules auto-apply |
| **OpenCode** | CLI | `AGENTS.md`, `opencode.json`, `.opencode/agents/`, `.opencode/skills/` | `@agent-name` or `/skill-name` |

### Auto-Load Details

| Tool | Always Loaded | Loaded Per-File | On Demand |
|---|---|---|---|
| Claude Code | `CLAUDE.md` | — | `.deepx/skills/` via routing table |
| Copilot | `.github/copilot-instructions.md` | `.github/instructions/*.instructions.md` (matched by `applyTo:` glob) | `.github/agents/*.agent.md` (via `@name`) |
| Cursor | `.cursor/rules/*.mdc` with `alwaysApply: true` | `.cursor/rules/*.mdc` with `globs: [...]` | — |
| OpenCode | `AGENTS.md` + `opencode.json` instructions | — | `.opencode/agents/*.md` (via `@name`), `.opencode/skills/*/SKILL.md` (via `/name`) |

### Setup

```bash
# Claude Code — open project and start coding
cd dx-runtime && claude

# OpenCode — same workflow
cd dx-runtime && opencode

# GitHub Copilot — open in VS Code
code dx-runtime

# Cursor — open in Cursor
cursor dx-runtime
```

## All Agents (12 Total)

### dx-runtime (2 agents)

| Agent | Role |
|-------|------|
| **dx-runtime-builder** | Unified router — receives any request and delegates to the correct sub-project builder |
| **dx-validator** | Unified validation — runs validation scripts across all levels and collects feedback |

### dx_app (6 agents)

| Agent | Role |
|-------|------|
| **dx-app-builder** | Master router for standalone apps — selects Python, C++, or async builder |
| **dx-python-builder** | Builds Python inference apps using DxInfer and InferenceEngine |
| **dx-cpp-builder** | Builds C++ inference apps using the native DxRT SDK |
| **dx-benchmark-builder** | Creates performance benchmarking harnesses for .dxnn models |
| **dx-model-manager** | Resolves .dxnn model paths, downloads models, manages config YAML |
| **dx-validator** | Validates dx_app outputs — imports, structure, runtime checks |

### dx_stream (4 agents)

| Agent | Role |
|-------|------|
| **dx-stream-builder** | Master router for pipeline apps — selects pipeline or messaging builder |
| **dx-pipeline-builder** | Builds GStreamer pipeline apps with DX accelerator elements |
| **dx-model-manager** | Resolves .dxnn models for pipeline use, manages stream configs |
| **dx-validator** | Validates dx_stream outputs — pipeline syntax, element availability |

## All Skills

| Project | Skill | Purpose |
|---------|-------|---------|
| dx-runtime | `/dx-brainstorm-and-plan` | Process: collaborative design session before code generation |
| dx-runtime | `/dx-tdd` | Process: test-driven development — write validation first, then implement |
| dx-runtime | `/dx-verify-completion` | Process: verify before claiming completion — evidence before assertions |
| dx-runtime | `dx-validate-and-fix` | Full feedback loop — validate, collect issues, apply fixes |
| dx_app | `dx-build-python-app` | Build a Python standalone inference app |
| dx_app | `dx-build-cpp-app` | Build a C++ standalone inference app |
| dx_app | `dx-build-async-app` | Build an async/batch inference app |
| dx_app | `dx-model-management` | Download, resolve, and configure .dxnn models |
| dx_app | `dx-validate` | Run dx_app validation scripts |
| dx_stream | `dx-build-pipeline-app` | Build a GStreamer pipeline app with DX elements |
| dx_stream | `dx-build-mqtt-kafka-app` | Build a pipeline with MQTT/Kafka message output |
| dx_stream | `dx-model-management` | Manage .dxnn models for streaming pipelines |
| dx_stream | `dx-validate` | Run dx_stream validation scripts |

## Interactive Workflow (5 Phases)

Every agent follows the same five-phase workflow:

### Phase 1 — Understand
Ask **2–3 targeted questions** (app type, input source, special requirements).
Present a build plan for user confirmation.

### Phase 2 — Load Context
Read relevant `.deepx/` files (skills, toolsets, instructions, memory) via the
context routing table. Do **not** read source code — all API references and
patterns live in the knowledge base.

### Phase 3 — Build
Generate application files in `dx-agentic-dev/<session_id>/` by default (or `src/`
if explicitly requested). Follow conventions in `.deepx/instructions/` — absolute
imports, IFactory patterns, proper DxInfer initialization.

### Phase 4 — Validate
Run validation scripts: import correctness, structure compliance, runtime
smoke test (syntax check, dry-run if applicable).

### Phase 5 — Report
Present results: files created (with full path in `dx-agentic-dev/` or `src/`),
validation status, run instructions, and any warnings.

## Quick Start Examples

The following scenarios illustrate workflows at the dx-runtime level. Scenario 1 is
unique to dx-runtime (cross-project). Scenarios 2 and 3 can also be run directly in
their respective submodules (`dx_app/` or `dx_stream/`), but working from dx-runtime
provides unified routing, cross-project validation, and the `dx-validate-and-fix`
feedback loop across all levels.

### Scenario 1: Build Both Standalone App and Streaming Pipeline

**Prompt:**

```
"Build a person detection standalone app and a streaming pipeline"
```

| Tool | How to Use |
|---|---|
| **Claude Code** | Type the prompt directly. `CLAUDE.md` routes via Unified Context Routing Table, recognizes the task spans both dx_app and dx_stream, loads appropriate skills for each. |
| **GitHub Copilot** | `@dx-runtime-builder` followed by the prompt. Classifies the request, hands off to `dx-app-builder` and `dx-stream-builder` via `handoffs:` mechanism. |
| **Cursor** | Type the prompt directly. `dx-runtime.mdc` (loaded via `alwaysApply: true`) provides the full context routing table. |
| **OpenCode** | `@dx-runtime-builder` followed by the prompt. `AGENTS.md` and `opencode.json` are loaded at session start. |

### Scenario 2: Build a Standalone Detection App (dx_app via routing)

When issued at the dx-runtime level, this request is routed to dx_app's builder.
Unlike working directly in `dx_app/`, dx-runtime provides unified validation
across both sub-projects and the ability to chain with other tasks in the same session.

**Prompt:**

```
"Build a person detection app with yolo26n"
```

| Tool | How to Use |
|---|---|
| **Claude Code** | Type the prompt directly. Routes to `dx-build-python-app` skill. |
| **GitHub Copilot** | `@dx-app-builder` followed by the prompt. |
| **Cursor** | Type the prompt directly. |
| **OpenCode** | `@dx-app-builder` followed by the prompt, or `/dx-build-python-app` skill. |

The agent will:
1. Ask about input source and output format
2. Load `dx-build-python-app` skill and yolo26n model config
3. Generate files in `dx-agentic-dev/<session_id>/` (or `src/` if requested)
4. Validate imports and structure
5. Report with run command

> **Tip:** This same prompt works when issued directly in `dx_app/`. Working from
> dx-runtime adds unified routing and the ability to chain this with other sub-project
> tasks (e.g., also building a streaming pipeline in the same session).

### Scenario 3: Build a Streaming Pipeline (dx_stream via routing)

When issued at the dx-runtime level, this request is routed to dx_stream's builder.
Unlike working directly in `dx_stream/`, dx-runtime provides unified validation
and cross-project coordination.

**Prompt:**

```
"Build a detection pipeline with tracking on RTSP camera"
```

| Tool | How to Use |
|---|---|
| **Claude Code** | Type the prompt directly. Routes to `dx-build-pipeline-app` skill. |
| **GitHub Copilot** | `@dx-stream-builder` followed by the prompt. |
| **Cursor** | Type the prompt directly. |
| **OpenCode** | `@dx-stream-builder` followed by the prompt, or `/dx-build-pipeline-app` skill. |

The agent will:
1. Ask about RTSP URL, display preferences, and tracker type
2. Load `dx-build-pipeline-app` skill and tracker toolset
3. Generate pipeline in `dx-agentic-dev/<session_id>/` (or standard location if requested)
4. Validate element availability and pipeline syntax
5. Report with launch command

> **Tip:** This same prompt works when issued directly in `dx_stream/`. Working from
> dx-runtime adds unified routing and the `dx-validate-and-fix` feedback loop that
> spans all sub-projects.

## Validation and Feedback Loop

Run these commands from the dx-runtime root:

```bash
# Validate all levels
python .deepx/scripts/validate_framework.py
python dx_app/.deepx/scripts/validate_framework.py
python dx_stream/.deepx/scripts/validate_framework.py

# Collect feedback from all validators into a single report
python .deepx/scripts/feedback_collector.py --all --output report.json

# Or scope to a specific sub-project
python .deepx/scripts/feedback_collector.py --app-dirs dx_app --output report.json

# Preview proposed fixes without applying them
python .deepx/scripts/apply_feedback.py --report report.json --dry-run

# Apply all approved fixes
python .deepx/scripts/apply_feedback.py --report report.json --approve-all

# Or selectively approve specific proposals
python .deepx/scripts/apply_feedback.py --report report.json --approve FB-001,FB-003
```

Iterate: validate → review → fix → repeat.

## Scripts Reference

| Script | Level | Purpose |
|--------|-------|---------|
| `validate_framework.py` | dx-runtime | Validates the unified knowledge base structure |
| `validate_framework.py` | dx_app | Validates dx_app knowledge base and generated apps |
| `validate_framework.py` | dx_stream | Validates dx_stream knowledge base and pipelines |
| `validate_app.py` | dx_app | Validates a specific generated application |
| `validate_app.py` | dx_stream | Validates a specific generated pipeline app |
| `feedback_collector.py` | dx-runtime | Aggregates validation results across all levels |
| `apply_feedback.py` | dx-runtime | Applies fixes from a feedback report |

## Knowledge Base Structure

Each `.deepx/` directory follows this layout:

| Directory | Content |
|-----------|---------|
| `agents/` | Agent definitions — role, capabilities, delegation rules |
| `skills/` | Build skills per app type — step-by-step generation workflows |
| `instructions/` | Coding standards, architecture guidelines, import rules |
| `toolsets/` | SDK/API references — DxInfer, InferenceEngine, IFactory, GStreamer elements |
| `memory/` | Persistent patterns and pitfalls — learned from past builds |
| `scripts/` | Validation and generation tools — Python scripts for automation |
| `knowledge/` | Structured YAML data — model configs, element catalogs, error mappings |

dx-runtime `.deepx/` holds **cross-cutting** knowledge (shared conventions, unified
validation). Sub-project `.deepx/` directories hold **domain-specific** knowledge.

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Agent says "skill not found" | Skill name misspelled or `.deepx/skills/` missing the file | Check available skills with `ls .deepx/skills/` and verify the exact filename |
| Validation fails on imports | Generated code uses relative imports instead of absolute | Re-run the builder — all agents enforce absolute imports from `dx_app.*` or `dx_stream.*` |
| Model file not found (.dxnn) | Model not downloaded or path not resolved through config | Run `@dx-model-manager` to download and register the model in `knowledge/models.yaml` |
| `feedback_collector.py` returns empty report | No validation scripts have been run yet | Run `validate_framework.py` at each level first, then collect feedback |
| Pipeline elements not available | DX GStreamer plugin not installed or not in `GST_PLUGIN_PATH` | Source `setup_env.sh` to set environment variables, verify plugin with `gst-inspect-1.0` |
| Agent generates code for wrong sub-project | Request was ambiguous between dx_app and dx_stream | Be explicit: mention "standalone" for dx_app or "pipeline"/"stream" for dx_stream |
