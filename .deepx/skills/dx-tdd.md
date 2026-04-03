# Skill: Test-Driven Development for DEEPX

> **RIGID skill** — follow this process exactly. No shortcuts, no exceptions.

## Overview

Write validation checks first, then implement. Verify each file immediately
after creation. Never batch validation to the end.

## The Iron Law

```
NO APPLICATION CODE WITHOUT A VALIDATION CHECK FIRST
```

In the DEEPX context, "validation check" means:
- Syntax check (`py_compile`) for every Python file
- JSON validation for every config.json
- Factory interface compliance check (5 methods)
- Import resolution test

## Red-Green Cycle for DEEPX Apps

### RED — Define What Should Pass

Before creating any file, define what validation must pass:

```bash
# Example: Before creating yolo26n_factory.py
# These checks MUST pass after the file is created:
python -c "import py_compile; py_compile.compile('factory/yolo26n_factory.py', doraise=True)"
PYTHONPATH=../../ python -c "from factory import Yolo26nFactory; f = Yolo26nFactory(); print(f.get_model_name())"
```

### GREEN — Create Minimal Code to Pass

Create the file with just enough content to pass all defined checks.

### VERIFY — Run Checks Immediately

After creating EACH file (not after all files):

```bash
# 1. Syntax
python -c "import py_compile; py_compile.compile('<file>', doraise=True)" && echo "OK: <file>"

# 2. JSON (for config.json)
python -c "import json; json.load(open('config.json')); print('OK: config.json')"

# 3. Factory import (after factory is created)
PYTHONPATH=<v3_dir> python -c "from factory import <Model>Factory; f = <Model>Factory(); assert f.get_model_name() == '<model>'; print('OK: factory')"
```

### REPEAT — Next File

Move to the next file only after the current file passes all checks.

## Validation Order

Create and validate files in this order:

| Order | File | Validation |
|---|---|---|
| 1 | `factory/<model>_factory.py` | py_compile + interface check |
| 2 | `factory/__init__.py` | py_compile + import test |
| 3 | `config.json` | JSON parse |
| 4 | `<model>_sync.py` | py_compile |
| 5 | `<model>_async.py` | py_compile |
| 6 | `<model>_sync_cpp_postprocess.py` | py_compile (if applicable) |
| 7 | `<model>_async_cpp_postprocess.py` | py_compile (if applicable) |
| 8 | `session.json` | JSON parse |
| 9 | `README.md` | exists |

## For GStreamer Pipelines

| Order | File | Validation |
|---|---|---|
| 1 | `pipeline.py` | py_compile + argparse check |
| 2 | `run_<app>.sh` | bash -n syntax check |
| 3 | `config/*.json` | JSON parse |
| 4 | `session.json` | JSON parse |
| 5 | `README.md` | exists |

## Framework-Level Validation

After all files are created, run the framework validator:

```bash
python .deepx/scripts/validate_app.py <session_dir>/
```

This validates the complete application structure.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "I'll validate at the end" | Errors compound. Fix file-by-file. |
| "py_compile is obvious" | Syntax errors happen. 1 second to check. |
| "The factory pattern is simple" | Missing methods cause runtime crashes. |
| "I know this works" | Confidence ≠ evidence. Run the check. |

## Key Principle

**Validate incrementally.** Each file is a checkpoint. Never move to the
next file until the current one passes. This catches errors when they are
cheapest to fix.
