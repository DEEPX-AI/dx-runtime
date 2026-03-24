# Skill: Brainstorm and Plan (Cross-Project Integration)

> **RIGID skill** — follow this process exactly. No shortcuts, no exceptions.

> **Scope:** This is the cross-project integration version. For single-project work, use:
> - `dx_app/.deepx/skills/dx-brainstorm-and-plan.md` (standalone inference)
> - `dx_stream/.deepx/skills/dx-brainstorm-and-plan.md` (GStreamer pipelines)

## Overview

Collaborative design session before any cross-project integration work. Explores
user intent, gathers requirements, proposes approaches, and produces an approved
build plan for work that spans dx_app and dx_stream.

<HARD-GATE>
Do NOT generate any application code, create any files, or take any implementation
action until you have presented a build plan and the user has approved it.
This applies to EVERY request regardless of perceived simplicity.
</HARD-GATE>

## When to Use

**Always** — before any cross-project integration work:
- Cross-project build coordination (dx_app + dx_stream)
- Shared model configuration
- Integration testing across sub-projects
- Modifying cross-project conventions

## Anti-Pattern: "This Is Too Simple"

Every build goes through this process. A single-model detection app, a config
change, a variant addition — all of them. "Simple" projects are where unexamined
assumptions cause the most wasted work.

## Process

### Step 1: Context Check

Before asking any questions:
1. Check both sub-projects' model registries for consistency
2. Check both `dx_app/` and `dx_stream/` directories
3. If the model/app already exists, inform the user and ask their intent:
   - Modify the existing app?
   - Create a specialized variant (e.g., person-only detection)?
   - Start fresh in `dx-agentic-dev/`?

### Step 2: Ask Key Decisions (one at a time)

Gather these decisions through focused questions:

1. **What are you building?** (app type, task, model)
2. **What variant?** (Python sync/async, C++, pipeline category)
3. **What input source?** (image, video, USB camera, RTSP)
4. **Any special requirements?** (custom thresholds, specific classes, tracking, broker)

Rules:
- One question at a time
- Provide concrete options (not open-ended)
- Default to the simplest working configuration

### Step 3: Present Build Plan

Present a concise plan:

```
Build Plan:
  Output:  dx-agentic-dev/20250403-143022_yolo26n_object_detection/
  Task:    object_detection
  Model:   yolo26n
  Variant: Python sync + async (2 files)
  Files:
    factory/yolo26n_factory.py
    factory/__init__.py
    yolo26n_sync.py
    yolo26n_async.py
    config.json
    session.json
    README.md
  Config:  score_threshold=0.25, nms_threshold=0.45
```

### Step 4: Get User Approval

Wait for explicit user approval before proceeding:
- "Looks good" / "Go ahead" / "Build it" → proceed to implementation
- Any modification request → update plan and re-present
- "Cancel" → stop

### Step 5: Route to Implementation

After approval, route to the appropriate level:
- For dx_app tasks → delegate to `dx_app/.deepx/skills/dx-brainstorm-and-plan.md`
- For dx_stream tasks → delegate to `dx_stream/.deepx/skills/dx-brainstorm-and-plan.md`
- For integration tasks → proceed with cross-project plan

## 5-Condition Pre-Flight Check

Before presenting the build plan, verify ALL of these:

| # | Check | Action if Failed |
|---|---|---|
| 1 | Model exists in registry | List available models, ask user to choose |
| 2 | Target directory doesn't exist | Ask user: modify existing, specialize, or fresh build? |
| 3 | Task type is supported | List supported tasks, suggest closest match |
| 4 | Required components exist | Check preprocessor/postprocessor availability |
| 5 | Output path is dx-agentic-dev/ | Confirm isolation (never default to src/) |

## Red Flags — STOP

- Generating code without user approval
- Skipping the model registry check
- Creating files in src/ without explicit user request
- Assuming the user wants the same thing as an existing app
- Proceeding without confirming variant and input source

## Key Principle

**Ask first, build second.** Every minute spent clarifying saves ten minutes
of rework. The user's intent is never obvious — even "build a yolo26n app"
has multiple valid interpretations.
