---
name: dx-tdd
description: Test-driven development for DEEPX cross-project integration
---

# Skill: Test-Driven Development for DEEPX (Cross-Project Integration)

> **RIGID skill** — follow this process exactly. No shortcuts, no exceptions.

> **Scope:** This is the cross-project integration version. For single-project work, use:
> - `dx_app/.deepx/skills/dx-tdd.md` (standalone inference)
> - `dx_stream/.deepx/skills/dx-tdd.md` (GStreamer pipelines)

## Overview

Write validation checks first, then implement. Verify each integration point
immediately. Never batch validation to the end.

## The Iron Law

```
NO APPLICATION CODE WITHOUT A VALIDATION CHECK FIRST
```

In the DEEPX cross-project context, "validation check" means:
- Build scripts pass for both sub-projects
- Cross-project imports resolve correctly
- Shared model configuration is consistent
- Integration tests pass across sub-projects

## Red-Green Cycle for DEEPX Apps

### RED — Define What Should Pass

Before making any cross-project change, define what integration checks must pass:

```bash
# Example: Before modifying shared model configuration
# These checks MUST pass after the change:
cd dx_app && ./install.sh && ./build.sh
cd dx_stream && ./install.sh
python -c "from dx_app.src.python_example.common.utils.model_utils import load_model_config; print('OK: cross-import')"
```

### GREEN — Create Minimal Change to Pass

Make the smallest cross-project change that passes all defined checks.

### VERIFY — Run Checks Immediately

After each integration change:

```bash
# 1. dx_app build
cd dx_app && ./install.sh && ./build.sh && echo "OK: dx_app build"

# 2. dx_stream install
cd dx_stream && ./install.sh && echo "OK: dx_stream install"

# 3. Cross-project imports
python -c "from dx_app.src.python_example.common.utils.model_utils import load_model_config; print('OK: cross-import')"

# 4. Shared model config
python -c "
import json
app_reg = json.load(open('dx_app/config/model_registry.json'))
stream_list = json.load(open('dx_stream/model_list.json'))
print('OK: model configs loaded')
"
```

### REPEAT — Next Integration Point

Move to the next cross-project change only after the current one passes all checks.

## Integration Validation Order

Validate cross-project integration in this order:

| Order | Check | Validation |
|---|---|---|
| 1 | dx_app build scripts | `./install.sh && ./build.sh` pass |
| 2 | dx_stream install | `./install.sh` passes |
| 3 | Cross-project imports | dx_stream can import from dx_app (never reverse) |
| 4 | Shared model paths | `model_registry.json` and `model_list.json` are consistent |
| 5 | Integration test | both sub-project `validate_framework.py` pass |

## Framework-Level Validation

After all integration changes are made, run both framework validators:

```bash
python dx_app/.deepx/scripts/validate_framework.py
python dx_stream/.deepx/scripts/validate_framework.py
```

This validates the complete integration across both sub-projects.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "I'll validate at the end" | Integration errors compound. Verify each change. |
| "py_compile is obvious" | Cross-project imports break silently. Check them. |
| "The factory pattern is simple" | Shared configs drift between sub-projects. |
| "I know this works" | Confidence ≠ evidence. Run the check. |

## Key Principle

**Validate incrementally.** Each integration point is a checkpoint. Never move to the
next change until the current one passes. This catches cross-project errors when they are
cheapest to fix.
