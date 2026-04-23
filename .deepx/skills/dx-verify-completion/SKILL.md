---
name: dx-verify-completion
description: Verify work before claiming done
---

# Skill: Verify Before Completion (Cross-Project Integration)

> **RIGID skill** — follow this process exactly. No shortcuts, no exceptions.

> **Scope:** This is the cross-project integration version. For single-project work, use:
> - `dx_app/.deepx/skills/dx-verify-completion.md` (standalone inference)
> - `dx_stream/.deepx/skills/dx-verify-completion.md` (GStreamer pipelines)

## Overview

Never claim an integration task is complete without running verification commands
and confirming their output. Evidence before assertions, always.

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this response, you cannot
claim it passes.

## The Gate Function

```
BEFORE claiming any build is complete:

1. IDENTIFY: What commands prove this claim?
2. RUN: Execute ALL verification commands (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim
```

## Integration Verification Checklist

Run ALL of these before claiming any cross-project work is complete:

```bash
# 1. dx_app framework validator
python dx_app/.deepx/scripts/validate_framework.py && echo "OK: dx_app framework"

# 2. dx_stream framework validator
python dx_stream/.deepx/scripts/validate_framework.py && echo "OK: dx_stream framework"

# 3. Cross-project imports
python -c "
from dx_app.src.python_example.common.utils.model_utils import load_model_config
print('OK: dx_stream can import from dx_app')
"

# 4. Shared model configuration consistency
python -c "
import json
app_reg = json.load(open('dx_app/config/model_registry.json'))
stream_list = json.load(open('dx_stream/model_list.json'))
print(f'OK: dx_app has {len(app_reg)} models, dx_stream has {len(stream_list)} models')
"

# 5. Build order verification (dx_app first, then dx_stream)
cd dx_app && ./install.sh && ./build.sh && echo "OK: dx_app build"
cd dx_stream && ./install.sh && echo "OK: dx_stream install"
```

## Red Flags — STOP

- Using "should pass", "probably works", "looks correct"
- Expressing satisfaction before running checks ("Done!", "Complete!")
- Claiming completion without showing command output
- Trusting that the template "just works"
- Skipping the framework validator

## Completion Report Template

Only after ALL checks pass, present:

```
Integration Complete ✓
======================
Scope:    Cross-project integration
Changes:  <summary of what changed>

Verification:
  ✓ dx_app framework:  validate_framework.py PASS
  ✓ dx_stream framework: validate_framework.py PASS
  ✓ Cross-project imports: dx_stream → dx_app OK
  ✓ Model config consistency: OK
  ✓ Build order: dx_app → dx_stream OK

Next Steps:
  Run sub-project tests if individual apps were modified.
```

## Key Principle

**Evidence before claims.** Run the command. Read the output. THEN report
the result. Claiming integration success without verification is dishonesty, not
efficiency.
