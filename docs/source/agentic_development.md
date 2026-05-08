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
2. **`.deepx/`** — the canonical source for all generated platform files. Holds
   agents, skills, templates, toolsets, instructions, memory, scripts, and
   structured knowledge (YAML). `dx-agentic-gen` generates `.github/`, `.claude/`,
   `.opencode/`, and `.cursor/rules/` from `.deepx/`. Agents read `.deepx/` files
   for context — **not source code**.

`CLAUDE.md` stays small and stable. `.deepx/` evolves as the project grows. Agents
load only the files they need via the context routing table, keeping token usage low.

### Generation Pipeline

Platform-specific files (`.github/`, `.claude/`, `.opencode/`, `.cursor/rules/`) are
generated from `.deepx/` by `dx-agentic-gen`. **Do not edit platform files directly** —
they will be overwritten on the next generation run.

```bash
# Generate all platform files from .deepx/
dx-agentic-gen generate --repo dx-runtime
```

A pre-commit hook runs `dx-agentic-gen` automatically to keep platform files in sync.

## Supported AI Tools

Four AI coding tools are supported. Each auto-loads the `.deepx/` knowledge base
through its own configuration files.

| Tool | Type | Config Files | Agent Invocation |
|---|---|---|---|
| **Claude Code** | CLI | `CLAUDE.md` | Free-form conversation; routing table dispatches |
| **GitHub Copilot** | VS Code | `.github/copilot-instructions.md`, `.github/agents/`, `.github/skills/` | `@agent-name "prompt"` |
| **Cursor** | IDE | `.cursor/rules/*.mdc` | Free-form conversation; rules auto-apply |
| **OpenCode** | CLI | `AGENTS.md`, `opencode.json`, `.opencode/agents/`, `.deepx/skills/` | `@agent-name` or `/skill-name` |

### Auto-Load Details

| Tool | Always Loaded | Loaded Per-File | On Demand |
|---|---|---|---|
| Claude Code | `CLAUDE.md` | — | `.deepx/skills/` via routing table |
| Copilot | `.github/copilot-instructions.md` | — | `.github/agents/*.agent.md` (via `@name`), `.github/skills/` (13 skill directories) |
| Cursor | `.cursor/rules/*.mdc` with `alwaysApply: true` | `.cursor/rules/*.mdc` with `globs: [...]` | — |
| OpenCode | `AGENTS.md` + `opencode.json` instructions | — | `.opencode/agents/*.md` (via `@name`), `.deepx/skills/*/SKILL.md` (via `/name`) |

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

### Platform File Loading Reference

Each AI coding agent auto-loads different configuration files at the dx-runtime level.

#### Auto-Loaded Files

| File | Copilot Chat/CLI | OpenCode | Claude Code | Cursor | Loading |
|------|:---:|:---:|:---:|:---:|---------|
| `.github/copilot-instructions.md` | ✅ | — | — | — | Auto |
| `CLAUDE.md` | — | — | ✅ | — | Auto |
| `AGENTS.md` + `opencode.json` | — | ✅ | — | — | Auto |
| `.cursor/rules/dx-runtime.mdc` | — | — | — | ✅ | Auto |

> **Cursor rules detail:** `.cursor/rules/` contains 16 `.mdc` files: `dx-runtime.mdc`,
> `dx-runtime-builder.mdc`, `dx-validator.mdc`, and 13 `skill-*.mdc` files (one per skill).

#### Agent Files (Manual @mention)

| Agent | Claude Code | Copilot (`@mention`) | OpenCode (`@mention`) |
|-------|------|------|---------|
| `dx-runtime-builder` | `.claude/agents/dx-runtime-builder.md` | `.github/agents/dx-runtime-builder.agent.md` | `.opencode/agents/dx-runtime-builder.md` |
| `dx-validator` | `.claude/agents/dx-validator.md` | `.github/agents/dx-validator.agent.md` | `.opencode/agents/dx-validator.md` |

#### Skill Files (All Platforms — `/slash-command`)

| Skill | File |
|-------|------|
| `/dx-swe-brainstorm` | `.deepx/skills/dx-swe-brainstorm/SKILL.md` |
| `/dx-swe-parallel-agents` | `.deepx/skills/dx-swe-parallel-agents/SKILL.md` |
| `/dx-swe-executing-plans` | `.deepx/skills/dx-swe-executing-plans/SKILL.md` |
| `/dx-swe-receiving-review` | `.deepx/skills/dx-swe-receiving-review/SKILL.md` |
| `/dx-swe-requesting-review` | `.deepx/skills/dx-swe-requesting-review/SKILL.md` |
| `/dx-skill-router` | `.deepx/skills/dx-skill-router/SKILL.md` |
| `/dx-swe-subagent-dev` | `.deepx/skills/dx-swe-subagent-dev/SKILL.md` |
| `/dx-swe-debugging` | `.deepx/skills/dx-swe-debugging/SKILL.md` |
| `/dx-swe-tdd` | `.deepx/skills/dx-swe-tdd/SKILL.md` |
| `/dx-agentic-runtime-validate` | `.deepx/skills/dx-agentic-runtime-validate/SKILL.md` |
| `/dx-swe-verify` | `.deepx/skills/dx-swe-verify/SKILL.md` |
| `/dx-swe-writing-plans` | `.deepx/skills/dx-swe-writing-plans/SKILL.md` |

#### Shared Knowledge Base (`.deepx/`)

The `.deepx/` directory is a platform-agnostic knowledge base read on demand by all
agent platforms. It is NOT auto-loaded — agents and skills reference specific files
as needed during task execution.

| Directory | Files | Description |
|-----------|-------|-------------|
| `.deepx/agents/` | `dx-runtime-builder.md`, `dx-validator.md` | Authoritative agent definitions (source of truth; `dx-agentic-gen` generates `.github/agents/`, `.claude/agents/`, and `.opencode/agents/` from these) |
| `.deepx/skills/` | 13 skill directories | Detailed skill workflows (see Skill Files table above) |
| `.deepx/templates/` | `en/`, `ko/` | Localized templates for generated platform files |
| `.deepx/instructions/` | Coding standards, guidelines | Architecture guidelines, import rules |
| `.deepx/toolsets/` | SDK/API references | DxInfer, InferenceEngine, IFactory, GStreamer elements |
| `.deepx/memory/` | Patterns and pitfalls | Persistent knowledge learned from past builds |
| `.deepx/knowledge/` | Structured YAML data | Model configs, element catalogs, error mappings |
| `.deepx/contextual-rules/` | Context-dependent rules | Rules applied based on task context |
| `.deepx/prompts/` | Prompt templates | Reusable prompt patterns for agents |
| `.deepx/scripts/` | Automation scripts | Validation and generation tools |

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

### dx-runtime Skills (13)

| Skill | Purpose |
|-------|---------|
| `/dx-swe-brainstorm` | Process: collaborative design session before code generation |
| `/dx-swe-parallel-agents` | Process: dispatch multiple independent agents in parallel |
| `/dx-swe-executing-plans` | Process: execute a written implementation plan with review checkpoints |
| `/dx-swe-receiving-review` | Process: handle incoming code review feedback with technical rigor |
| `/dx-swe-requesting-review` | Process: request and verify code review before merging |
| `/dx-skill-router` | Process: route requests to the appropriate skill |
| `/dx-swe-subagent-dev` | Process: execute implementation plans with independent sub-agents |
| `/dx-swe-debugging` | Process: systematic debugging before proposing fixes |
| `/dx-swe-tdd` | Process: test-driven development — write validation first, then implement |
| `/dx-agentic-runtime-validate` | Full feedback loop — validate, collect issues, apply fixes |
| `/dx-swe-verify` | Process: verify before claiming completion — evidence before assertions |
| `/dx-swe-writing-plans` | Process: write implementation plans from specs/requirements |

### Sub-Directory Skills (dx_app, dx_stream)

These skills are only available when working within their respective sub-directories.

| Project | Skill | Purpose |
|---------|-------|---------|
| dx_app | `dx-agentic-app-build-python` | Build a Python standalone inference app |
| dx_app | `dx-agentic-app-build-cpp` | Build a C++ standalone inference app |
| dx_app | `dx-agentic-app-build-async` | Build an async/batch inference app |
| dx_app | `dx-agentic-app-model-management` | Download, resolve, and configure .dxnn models |
| dx_app | `dx-validate` | Run dx_app validation scripts |
| dx_stream | `dx-agentic-stream-build-pipeline` | Build a GStreamer pipeline app with DX elements |
| dx_stream | `dx-agentic-stream-build-mqtt-kafka` | Build a pipeline with MQTT/Kafka message output |
| dx_stream | `dx-agentic-stream-model-management` | Manage .dxnn models for streaming pipelines |
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
their respective sub-directories (`dx_app/` or `dx_stream/`), but working from dx-runtime
provides unified routing, cross-project validation, and the `dx-agentic-runtime-validate`
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
| **Claude Code** | Type the prompt directly. Routes to `dx-agentic-app-build-python` skill. |
| **GitHub Copilot** | `@dx-app-builder` followed by the prompt. |
| **Cursor** | Type the prompt directly. |
| **OpenCode** | `@dx-app-builder` followed by the prompt, or `/dx-agentic-app-build-python` skill. |

The agent will:
1. Ask about input source and output format
2. Load `dx-agentic-app-build-python` skill and yolo26n model config
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
| **Claude Code** | Type the prompt directly. Routes to `dx-agentic-stream-build-pipeline` skill. |
| **GitHub Copilot** | `@dx-stream-builder` followed by the prompt. |
| **Cursor** | Type the prompt directly. |
| **OpenCode** | `@dx-stream-builder` followed by the prompt, or `/dx-agentic-stream-build-pipeline` skill. |

The agent will:
1. Ask about RTSP URL, display preferences, and tracker type
2. Load `dx-agentic-stream-build-pipeline` skill and tracker toolset
3. Generate pipeline in `dx-agentic-dev/<session_id>/` (or standard location if requested)
4. Validate element availability and pipeline syntax
5. Report with launch command

> **Tip:** This same prompt works when issued directly in `dx_stream/`. Working from
> dx-runtime adds unified routing and the `dx-agentic-runtime-validate` feedback loop that
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
| `skills/` | Build skills (13 at runtime level) — step-by-step generation workflows |
| `templates/` | Localized templates (`en/`, `ko/`) for generated platform files |
| `instructions/` | Coding standards, architecture guidelines, import rules |
| `toolsets/` | SDK/API references — DxInfer, InferenceEngine, IFactory, GStreamer elements |
| `memory/` | Persistent patterns and pitfalls — learned from past builds |
| `scripts/` | Validation and generation tools — Python scripts for automation |
| `knowledge/` | Structured YAML data — model configs, element catalogs, error mappings |
| `contextual-rules/` | Context-dependent rules applied based on task type |
| `prompts/` | Reusable prompt templates for agents |

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

## Session Sentinels

When processing a user prompt, agents output these markers for automated session
boundary detection by the test harness:

| Marker | When |
|--------|------|
| `[DX-AGENTIC-DEV: START]` | First line of agent response |
| `[DX-AGENTIC-DEV: DONE (output-dir: <relative_path>)]` | Last line after all work is complete. `<relative_path>` is the session output directory relative to the project root. If no files were generated, omit the `(output-dir: ...)` part. |

Rules:
1. **CRITICAL** — Output `[DX-AGENTIC-DEV: START]` as the absolute first line of your first response, before ANY other text, tool calls, or reasoning. This is non-negotiable even if the user says "just proceed" or "use your own judgment" — automated tests WILL fail without it.
2. Output DONE as the very last line after all work, validation, and file generation is complete.
3. Sub-agents invoked via handoff do not output sentinels — only the top-level agent does.
4. If the user sends multiple prompts in a session, output START/DONE for each prompt.
5. The `output-dir` in DONE must be the relative path from the project root to the session output directory.
6. **Never output DONE after only producing planning artifacts** (specs, plans, design documents). DONE means all deliverables are produced — implementation code, scripts, configs, and validation results.
