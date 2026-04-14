---
name: dx-validate-and-fix
description: Full feedback loop — validate framework, collect findings, approve and apply fixes, verify results across all 3 levels of the dx-runtime knowledge base
---

# Validate and Fix — Full Feedback Loop

Run validation across the dx-runtime project, collect findings into actionable
feedback proposals, apply approved fixes, and verify results.

## Quick Start

```bash
# 1. Validate all levels
python .deepx/scripts/validate_framework.py
python dx_app/.deepx/scripts/validate_framework.py
python dx_stream/.deepx/scripts/validate_framework.py

# 2. Collect feedback
python .deepx/scripts/feedback_collector.py --framework-only

# 3. Apply fixes (dry-run first)
python .deepx/scripts/apply_feedback.py --dry-run
python .deepx/scripts/apply_feedback.py --report <path> --approve-all

# 4. Re-validate
python .deepx/scripts/feedback_collector.py --framework-only
```

## Workflow

1. **Validate** — Run `validate_framework.py` at each level
2. **Collect** — Run `feedback_collector.py` to generate proposals
3. **Review** — Present proposals to user for approval
4. **Apply** — Run `apply_feedback.py` with approved IDs
5. **Verify** — Re-run validators to confirm fixes

## CLI Flags

| Flag | Description |
|---|---|
| `--all` | Run against all levels |
| `--framework-only` | Validate .deepx/ structure only |
| `--app-dirs <dirs>` | Scope to specific sub-projects |
| `--approve-all` | Apply all proposals without review |
| `--approve FB-001,FB-003` | Apply specific proposals |
| `--dry-run` | Preview changes without writing |
