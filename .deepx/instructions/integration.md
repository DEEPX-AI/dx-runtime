# Cross-Project Integration Patterns

> Integration-only instructions for tasks that span dx_app and dx_stream.
> For sub-project-specific coding standards and workflows, see the respective
> `.deepx/instructions/` directories in dx_app and dx_stream.

---

## When dx_app Models Are Used in dx_stream Pipelines

dx_app and dx_stream both consume `.dxnn` model files, but they resolve paths differently:

- **dx_app**: Looks up models via `config/model_registry.json` using `resolve_model_path()`.
  The registry maps a logical model name (e.g., `"yolov8n"`) to a `.dxnn` file path
  relative to the dx_app models directory.

- **dx_stream**: Uses `model_list.json` at the repository root. GStreamer `DxInfer` elements
  require an **absolute path** to the `.dxnn` file via the `model-path` property.

### Synchronization Rule

When adding a new model:
1. Add the entry to `dx_app/config/model_registry.json` with all metadata (input dims,
   class labels, architecture support).
2. Add the corresponding entry to `dx_stream/model_list.json` with the download URL
   and expected filesystem path.
3. Verify both entries reference the same `.dxnn` filename and architecture variant.

---

## Shared .dxnn Models Across Both Projects

Both projects download models to a shared location (typically `~/dx_models/` or a
project-local `models/` directory). The path resolution differs:

| Project | Resolution Method | Path Style |
|---|---|---|
| dx_app | `resolve_model_path(name)` via model_registry.json | Relative, resolved at runtime |
| dx_stream | `model-path` property on DxInfer element | Absolute, set at pipeline construction |

### Best Practice

Use environment variable `DX_MODEL_DIR` to point both projects at the same model directory.
This avoids duplicate downloads and ensures version consistency.

---

## Build Order

The correct build and install order is strictly sequential:

```
0. sanity    — bash scripts/sanity_check.sh --dx_rt   (verify dx-runtime is installed)
               If FAIL: bash install.sh --all --exclude-app --exclude-stream --skip-uninstall --venv-reuse
1. dx_rt     — ./install.sh           (runtime C library + GStreamer plugins)
2. dx_app    — ./install.sh && ./build.sh   (Python SDK + C++ examples + pybind11 postprocessors)
3. dx_stream — ./install.sh           (GStreamer plugin bindings + Python pipeline tools)
```

### Why Order Matters

- `dx_app` links against `libdx_engine.so` from dx_rt. If dx_rt is not installed,
  the dx_app build will fail with `cannot find -ldx_engine`.
- `dx_stream` GStreamer plugins depend on dx_rt plugin libraries. Missing dx_rt
  causes `gst-inspect-1.0 dxinfer` to report "No such element or plugin."
- dx_app and dx_stream do NOT depend on each other. They can be built in either
  order after dx_rt is installed.

---

## Unified Testing Strategy

### Unit Tests

```bash
# dx_app unit tests
cd dx_app && pytest tests/

# dx_stream unit tests
cd dx_stream && pytest test/
```

### Cross-Project Smoke Test

After building both projects, run the unified validation:

```bash
python .deepx/scripts/validate_framework.py
```

This checks cross-references between all three `.deepx/` directories and verifies
model name consistency between `model_registry.json` and `model_list.json`.

---

## Python Imports — No Cross-Project Imports

dx_app and dx_stream are **not** importable as `dx_app.*` / `dx_stream.*` packages —
there is no installed package root (no `__init__.py` chain, not pip-installed). Each
sub-project's Python code resolves only its own in-tree imports; e.g. dx_app apps use
`from common.runner import ...` with `src/python_example/` on `sys.path` (see dx_app
`coding-standards.md`).

### Common Mistake

Do NOT import one sub-project's Python modules from the other — there is no package to
import, so copied import lines fail with `ModuleNotFoundError`. Each sub-project is
self-contained. Cross-project coupling happens through **shared `.dxnn` models** kept
name-consistent across `dx_app/config/model_registry.json` and
`dx_stream/model_list.json`, and through the shared **dx_rt** runtime — never Python imports.
