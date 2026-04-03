# Skill: Verify Before Completion

> **RIGID skill** — follow this process exactly. No shortcuts, no exceptions.

## Overview

Never claim an application is complete without running verification commands
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

## Verification Checklist for dx_app Python Apps

Run ALL of these before claiming completion:

```bash
# 1. Syntax check all Python files
for f in factory/*_factory.py *_sync.py *_async.py *_sync_cpp_postprocess.py *_async_cpp_postprocess.py; do
    [ -f "$f" ] && python -c "import py_compile; py_compile.compile('$f', doraise=True)" && echo "OK: $f"
done

# 2. JSON validation
python -c "import json; json.load(open('config.json')); print('OK: config.json')"
python -c "import json; json.load(open('session.json')); print('OK: session.json')"

# 3. Factory compliance
PYTHONPATH=<v3_dir> python -c "
from factory import <Model>Factory
f = <Model>Factory()
assert hasattr(f, 'create_preprocessor'), 'Missing create_preprocessor'
assert hasattr(f, 'create_postprocessor'), 'Missing create_postprocessor'
assert hasattr(f, 'create_visualizer'), 'Missing create_visualizer'
assert hasattr(f, 'get_model_name'), 'Missing get_model_name'
assert hasattr(f, 'get_task_type'), 'Missing get_task_type'
print(f'OK: {f.get_model_name()} / {f.get_task_type()}')
"

# 4. Framework validator (if available)
python .deepx/scripts/validate_app.py <session_dir>/
```

## Verification Checklist for dx_stream Pipelines

```bash
# 1. Python syntax
python -c "import py_compile; py_compile.compile('pipeline.py', doraise=True)" && echo "OK: pipeline.py"

# 2. Shell script syntax
bash -n run_*.sh && echo "OK: shell scripts"

# 3. JSON configs
for f in config/*.json session.json; do
    [ -f "$f" ] && python -c "import json; json.load(open('$f')); print('OK: $f')"
done

# 4. Pipeline parse test (requires GStreamer)
python pipeline.py --help 2>/dev/null && echo "OK: argparse"
```

## Verification Checklist for C++ Apps

```bash
# 1. CMakeLists.txt syntax (basic check)
grep -q "cmake_minimum_required" CMakeLists.txt && echo "OK: CMakeLists.txt has minimum version"
grep -q "target_link_libraries" CMakeLists.txt && echo "OK: CMakeLists.txt has link libs"

# 2. JSON config
python -c "import json; json.load(open('config.json')); print('OK: config.json')"

# 3. Compile test (if build environment available)
mkdir -p build && cd build && cmake .. && make -j$(nproc)
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
Build Complete ✓
================
Session:  dx-agentic-dev/20250403-143022_yolo26n_object_detection/
Model:    yolo26n
Task:     object_detection
Variants: sync, async (2 files)

Verification:
  ✓ py_compile: 4/4 files pass
  ✓ JSON: 2/2 files valid
  ✓ Factory: 5/5 methods present
  ✓ validate_app.py: PASS

Run:
  cd dx-agentic-dev/20250403-143022_yolo26n_object_detection/
  python yolo26n_sync.py --model /path/to/yolo26n.dxnn --image test.jpg
```

## Key Principle

**Evidence before claims.** Run the command. Read the output. THEN report
the result. Claiming completion without verification is dishonesty, not
efficiency.
