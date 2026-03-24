# `.deepx/` — DEEPX Runtime Integration Knowledge

This is the **integration layer** for the DEEPX dx-runtime knowledge system.
It does NOT duplicate content from the sub-project knowledge bases. Instead,
it provides cross-project routing, unified agents, and integration-specific
instructions for tasks that span both dx_app and dx_stream.

---

## Architecture

| Level | Path | Scope | When to Use |
|---|---|---|---|
| **dx_app** | `dx_app/.deepx/` | Standalone inference apps (Python/C++) | Developing in dx_app submodule alone |
| **dx_stream** | `dx_stream/.deepx/` | GStreamer pipeline apps | Developing in dx_stream submodule alone |
| **dx-runtime** (this) | `.deepx/` | Cross-project integration | Working across dx_app + dx_stream |

Each sub-project `.deepx/` is fully self-contained and works independently
when the submodule is cloned alone. This integration layer adds:

- **Unified routing** — a single context routing table that covers all task types
- **Cross-project agent** — a router that dispatches to the correct sub-project builder
- **Integration instructions** — build order, shared model paths, cross-validation
- **Unified memory** — common pitfalls tagged by domain, spanning both projects
- **Unified scripts** — validators and generators that operate across all three `.deepx/` directories

---

## Directory Structure

```
.deepx/
├── README.md                          # This file — integration layer index
├── agents/
│   ├── dx-runtime-builder.md          # Unified router agent
│   └── dx-validator.md                # Unified validation orchestrator
├── instructions/
│   ├── integration.md                 # Cross-project integration patterns
│   └── agent-protocols.md             # Behavioral protocols (integration-scoped)
├── knowledge/
│   └── feedback_rules.yaml            # Validation finding → knowledge base mapping rules
├── memory/
│   └── common_pitfalls.md             # Unified pitfalls with domain tags
├── scripts/
│   ├── validate_app.py                # Unified app validator (dx_app + dx_stream)
│   ├── validate_framework.py          # Validates all 3 .deepx/ directories
│   ├── generate_platforms.py          # Generates platform files for entire dx-runtime
│   ├── feedback_collector.py          # Collect validation findings into feedback proposals
│   └── apply_feedback.py             # Apply approved feedback fixes to .deepx/ files
├── skills/
│   ├── dx-validate-and-fix.md         # Full validate → collect → approve → apply → verify loop
│   ├── dx-brainstorm-and-plan.md      # Process skill — brainstorm and plan before code generation
│   ├── dx-tdd.md                      # Process skill — test-driven development, validate incrementally
│   └── dx-verify-completion.md        # Process skill — verify before claiming completion
└── templates/
    └── copilot-instructions.md        # Unified Copilot template
```

---

## Unified Context Routing Table

Agents use this table to determine which sub-project knowledge base to load.
All paths are relative to the dx-runtime repository root.

| If the task mentions... | Sub-project | Read these files |
|---|---|---|
| **Python app, detection, factory** | dx_app | `dx_app/.deepx/skills/dx-build-python-app.md`, `dx_app/.deepx/toolsets/common-framework-api.md` |
| **C++ app, native engine** | dx_app | `dx_app/.deepx/skills/dx-build-cpp-app.md`, `dx_app/.deepx/toolsets/dx-engine-api.md` |
| **Async, high-throughput** | dx_app | `dx_app/.deepx/skills/dx-build-async-app.md`, `dx_app/.deepx/memory/performance_patterns.md` |
| **Model, download, registry** | dx_app | `dx_app/.deepx/skills/dx-model-management.md`, `dx_app/.deepx/toolsets/model-registry.md` |
| **GStreamer, pipeline, stream** | dx_stream | `dx_stream/.deepx/skills/dx-build-pipeline-app.md`, `dx_stream/.deepx/toolsets/dx-stream-elements.md` |
| **MQTT, Kafka, message broker** | dx_stream | `dx_stream/.deepx/skills/dx-build-mqtt-kafka-app.md`, `dx_stream/.deepx/toolsets/dx-stream-elements.md` |
| **Cross-project, integration** | dx-runtime | `.deepx/instructions/integration.md`, `.deepx/memory/common_pitfalls.md` |
| **Validation, testing** | Both | `.deepx/scripts/validate_app.py`, sub-project `instructions/testing-patterns.md` |
| **Validation, feedback, fix** | dx-runtime | `.deepx/skills/dx-validate-and-fix.md`, `.deepx/knowledge/feedback_rules.yaml` |
| **ALWAYS read (every task)** | dx-runtime | `.deepx/memory/common_pitfalls.md` |

---

## Sub-Project Entry Points

| Sub-project | CLAUDE.md | .deepx/ |
|---|---|---|
| dx_app | `dx_app/CLAUDE.md` | `dx_app/.deepx/README.md` |
| dx_stream | `dx_stream/CLAUDE.md` | `dx_stream/.deepx/README.md` |

---

## Developer Workflow

```
1. Edit     →  Modify files in .deepx/ (this level or sub-projects)
2. Validate →  python .deepx/scripts/validate_framework.py
3. Generate →  python .deepx/scripts/generate_platforms.py --generate
4. Commit   →  git add .deepx/ && git commit
```

All changes flow from `.deepx/` outward. Never edit generated platform
files directly — they will be overwritten on the next regeneration.
