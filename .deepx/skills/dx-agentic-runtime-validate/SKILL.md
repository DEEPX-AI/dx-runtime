---
name: dx-agentic-runtime-validate
description: Full validation and fix feedback loop
---

# Skill: Validate and Fix — Full Feedback Loop

> Run validation across the dx-runtime project, collect findings into actionable
> feedback proposals, apply approved fixes to the .deepx/ knowledge base, and
> verify the results. This skill covers the complete loop from detection to resolution.

## Overview

This skill differs from `dx-validate.md` (which exists in dx_app and dx_stream):

| Skill | Scope | What It Does |
|-------|-------|--------------|
| `dx-validate.md` | Per-component (dx_app or dx_stream) | Validation only — report findings |
| `dx-agentic-runtime-validate.md` | Unified (dx-runtime) | Full loop — validate, collect, approve, apply, verify |

The validate-and-fix loop works across all three levels:

- **dx-runtime unified** — framework-wide checks (cross-references, routing tables, shared config)
- **dx_app** — app-level checks (task configs, model paths, code patterns)
- **dx_stream** — stream-level checks (pipeline definitions, element configs, buffer settings)

Findings from any level feed into the same feedback pipeline, producing proposals
that target the correct `.deepx/` files regardless of where the issue was detected.

## Quick Start

```bash
# 1. Run validation across all levels
python .deepx/scripts/validate_framework.py
python dx_app/.deepx/scripts/validate_framework.py
python dx_stream/.deepx/scripts/validate_framework.py

# 2. Collect feedback proposals
python .deepx/scripts/feedback_collector.py --all --output report.json

# 3. Preview what would change (dry run)
python .deepx/scripts/apply_feedback.py --report report.json --dry-run

# 4. Apply approved fixes
python .deepx/scripts/apply_feedback.py --report report.json --approve-all

# 5. Re-validate to confirm
python .deepx/scripts/validate_framework.py
```

## Step-by-Step Workflow

### Step 1: Run Validation

Choose the scope that matches your task. Run the corresponding commands from
the dx-runtime root directory.

| Scope | Commands |
|-------|----------|
| Everything | All 6 validators (3 framework + 3 app-level) |
| Framework only | `validate_framework.py` in `.deepx/`, `dx_app/.deepx/`, `dx_stream/.deepx/` |
| dx_app only | `dx_app/.deepx/scripts/validate_framework.py` + `dx_app/.deepx/scripts/validate_app.py` |
| dx_stream only | `dx_stream/.deepx/scripts/validate_framework.py` + `dx_stream/.deepx/scripts/validate_app.py` |
| Specific app | `dx_app/.deepx/scripts/validate_app.py` or `dx_stream/.deepx/scripts/validate_app.py` with `--task`, `--model`, or `--pipeline` |

Example — validate everything:

```bash
python .deepx/scripts/validate_framework.py
python dx_app/.deepx/scripts/validate_framework.py
python dx_stream/.deepx/scripts/validate_framework.py
python dx_app/.deepx/scripts/validate_app.py
python dx_stream/.deepx/scripts/validate_app.py
```

Example — validate a specific dx_stream pipeline:

```bash
python dx_stream/.deepx/scripts/validate_app.py --pipeline detection_overlay
```

### Step 2: Collect Feedback

The feedback collector runs validators, normalizes results, matches them against
rules, and generates proposals.

```bash
# All levels (framework + app dirs)
python .deepx/scripts/feedback_collector.py --all --output report.json

# dx_app only
python .deepx/scripts/feedback_collector.py --app-dirs dx_app --output report.json

# dx_stream only
python .deepx/scripts/feedback_collector.py --app-dirs dx_stream --output report.json

# Framework only (skip app code checks)
python .deepx/scripts/feedback_collector.py --framework-only --output report.json
```

The collector performs these steps internally:

1. Runs the appropriate validators based on the selected scope
2. Normalizes results through adapters (3 different result models to unified format)
3. Matches findings against rules in `feedback_rules.yaml`
4. Generates proposals with target files, actions, and content previews

### Step 3: Review Proposals

The report JSON contains an array of proposals. Each proposal has this structure:

```json
{
  "id": 1,
  "check_name": "check_routing_table_paths",
  "severity": "error",
  "source_level": "dx_app",
  "action": "fix_reference",
  "target_file": "README.md",
  "description": "Fix broken file path reference",
  "preview": "- `skills/dx-validate.md` → `skills/dx-agentic-runtime-validate.md`"
}
```

For each proposal, verify:

- **target_file** — points to the correct `.deepx/` file
- **action** — the action type is appropriate for the finding
- **preview** — the proposed content change makes sense
- **severity** — errors should be fixed; warnings are discretionary

### Step 4: Apply Fixes

```bash
# Approve all proposals
python .deepx/scripts/apply_feedback.py --report report.json --approve-all

# Select specific proposals by ID
python .deepx/scripts/apply_feedback.py --report report.json --approve FB-001,FB-003,FB-005

# Interactive mode (approve/reject each proposal one by one)
python .deepx/scripts/apply_feedback.py --report report.json

# Dry run (preview changes without writing files)
python .deepx/scripts/apply_feedback.py --report report.json --dry-run
```

The apply script modifies only files inside `.deepx/` directories. It never touches
application source code. Each change is logged so it can be reviewed in version control.

### Step 5: Verify

Re-run the same validators you used in Step 1:

```bash
python .deepx/scripts/validate_framework.py
python dx_app/.deepx/scripts/validate_framework.py
python dx_stream/.deepx/scripts/validate_framework.py
```

Check that:

- Previous errors are resolved
- No new errors were introduced by the fixes
- Warning count decreased or stayed the same

If new issues appear, return to Step 2 and iterate.

## Feedback Actions Reference

| Action | Description | Target Files |
|--------|-------------|--------------|
| `append_pitfall` | Add new entry to common_pitfalls.md | `memory/common_pitfalls.md` |
| `append_rule` | Add new rule to contextual-rules file | `contextual-rules/*.md` |
| `fix_reference` | Fix broken file path or cross-reference | Any `.deepx/` file |
| `add_domain_tag` | Add missing `[DOMAIN]` tag to memory entry | `memory/*.md` |
| `update_skill` | Add to Common Failures table in skill doc | `skills/*.md` |
| `update_knowledge` | Add insight to knowledge YAML | `knowledge/*.yaml` |

Actions are idempotent — running the same proposal twice will not duplicate content.
The apply script checks for existing entries before appending.

## Feedback Rules

Rules are defined in `.deepx/knowledge/feedback_rules.yaml`. Each rule maps a
check pattern (regex) to a target file and action.

Example rule:

```yaml
- check_pattern: "check_routing_table_paths"
  source: "validate_framework"
  level: "any"
  target: "memory/common_pitfalls.md"
  action: "append_pitfall"
  severity_filter: "error"
  template:
    domain: "{detected_level}"
    title: "Broken routing table path"
    symptom: "Skill or instruction file not found at referenced path"
    cause: "File was moved or renamed without updating the routing table"
    fix: "Update the path in README.md routing table to match actual location"
```

To add new rules, append to `feedback_rules.yaml`:

```yaml
- check_pattern: "check_new_pattern"
  source: "validate_app"
  level: "any"
  target: "memory/common_pitfalls.md"
  action: "append_pitfall"
  severity_filter: "error"
  template:
    domain: "{detected_level}"
    title: "Issue Title"
    symptom: "What the user sees"
    cause: "Why it happens"
    fix: "How to fix it"
```

Key fields:

- **check_pattern** — regex matched against the check name from validation results
- **source** — which validator produced the finding (`validate_framework` or `validate_app`)
- **level** — `dx_app`, `dx_stream`, or `any`
- **severity_filter** — only match findings at this severity or above
- **template** — content template with `{placeholder}` variables filled from the finding

## Adapter Architecture

The feedback collector uses adapters to normalize validation results from three
different result models into a single `UnifiedFinding` format:

| Source | Result Model | Adapter Mapping |
|--------|-------------|-----------------|
| dx_app `validate_app.py` | Plain class with `name`, `severity` (string) | `name` → `check`, `severity` → `Severity` enum |
| dx_stream `validate_app.py` | `@dataclass` with `check`, `Severity` enum | Direct mapping (already structured) |
| Unified `validate_framework.py` | Plain class with `name`, `details`, `fixable` | `name` → `check`, infer severity from `fixable` |

The `UnifiedFinding` dataclass:

```python
@dataclass
class UnifiedFinding:
    check: str           # Normalized check name
    severity: Severity   # error, warning, info
    source_level: str    # dx_app, dx_stream, or unified
    details: dict        # Original finding data preserved
    fixable: bool        # Whether auto-fix is possible
```

This architecture means validation scripts do not need to change when new feedback
rules are added. Adapters handle all format differences transparently.

## Common Failures

| Failure | Cause | Fix |
|---------|-------|-----|
| feedback_collector.py import error | Missing pyyaml dependency | `pip install pyyaml` |
| Empty proposals list | No matching rules for findings | Add rules to `feedback_rules.yaml` |
| apply_feedback.py target not found | Incorrect relative path in rule | Fix `target` path in `feedback_rules.yaml` |
| "No validator found" | Running from wrong directory | Run from dx-runtime root |
| JSON decode error in report | Corrupted or partial report file | Re-run `feedback_collector.py` |
| Proposal applied but check still fails | Fix was incomplete or wrong template | Review the rule template and adjust |
| Permission denied on target file | File is read-only or owned by root | Check file permissions in `.deepx/` |
<!-- END_COMMON_FAILURES -->

## Related

- `dx_app/.deepx/skills/dx-validate.md` — dx_app validation levels and checks
- `dx_stream/.deepx/skills/dx-validate.md` — dx_stream pipeline validation
- `.deepx/knowledge/feedback_rules.yaml` — rule definitions
- `.deepx/scripts/feedback_collector.py` — collection script
- `.deepx/scripts/apply_feedback.py` — application script
