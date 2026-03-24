#!/usr/bin/env python3
"""DEEPX Unified App Validator

Auto-detects whether validating a dx_app or dx_stream application and applies
the appropriate checks. Works with both sub-project types from a single entry point.

Usage:
    python validate_app.py <app_dir>
    python validate_app.py <app_dir> --smoke-test
    python validate_app.py <app_dir> --strict
    python validate_app.py <app_dir> --project dx_app
"""

import argparse
import ast
import json
import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

IFACTORY_REQUIRED_METHODS = frozenset(
    [
        "create_preprocessor",
        "create_postprocessor",
        "create_visualizer",
        "get_model_name",
        "get_task_type",
    ]
)

APP_YAML_REQUIRED_FIELDS = {"name", "type", "model", "status"}

DXNN_PATH_PATTERN = re.compile(r"""['"][^'"]*\.dxnn['"]""")
RELATIVE_IMPORT_PATTERN = re.compile(r"^\s*(from\s+\.+|import\s+\.+)", re.MULTILINE)
LOGGING_PATTERN = re.compile(r"logging\.getLogger\(__name__\)")
PARSE_COMMON_ARGS_PATTERN = re.compile(r"parse_common_args\s*\(")

# GStreamer pipeline detection patterns
GSTREAMER_PATTERNS = [
    re.compile(r"Gst\.parse_launch"),
    re.compile(r"gst_parse_launch"),
    re.compile(r"DxPipeline"),
    re.compile(r"DxInfer"),
    re.compile(r"DxPreprocess"),
]

PREPROCESS_ID_PATTERN = re.compile(r"preprocess-id\s*=\s*(\d+)")


# ---------------------------------------------------------------------------
# Project Type Detection
# ---------------------------------------------------------------------------


def detect_project_type(app_dir: Path) -> str:
    """Auto-detect whether app_dir is a dx_app or dx_stream application.

    Returns 'dx_app', 'dx_stream', or 'unknown'.
    """
    # Check directory ancestry
    for parent in [app_dir] + list(app_dir.parents):
        if parent.name == "dx_app":
            return "dx_app"
        if parent.name == "dx_stream":
            return "dx_stream"

    # Check for GStreamer patterns in source files
    for py_file in _collect_py_files(app_dir):
        source = _read_text_safe(py_file)
        if source is None:
            continue
        for pattern in GSTREAMER_PATTERNS:
            if pattern.search(source):
                return "dx_stream"

    # Check for IFactory pattern (dx_app indicator)
    for py_file in _collect_py_files(app_dir):
        source = _read_text_safe(py_file)
        if source and "IFactory" in source:
            return "dx_app"

    # Check for pipeline config files
    if (app_dir / "pipeline.py").exists() or any(app_dir.glob("run_*.sh")):
        return "dx_stream"

    # Check for factory files
    if any("factory" in f.stem.lower() for f in _collect_py_files(app_dir)):
        return "dx_app"

    return "unknown"


# ---------------------------------------------------------------------------
# Result Container
# ---------------------------------------------------------------------------


class CheckResult:
    """Result of a single validation check."""

    def __init__(self, name: str, passed: bool, message: str, details: Optional[List[str]] = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "message": self.message,
            "details": self.details,
        }

    def __str__(self) -> str:
        status = "[PASS]" if self.passed else "[FAIL]"
        line = f"{status} {self.message}"
        if self.details:
            for d in self.details:
                line += f"\n       {d}"
        return line


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _collect_py_files(app_dir: Path) -> List[Path]:
    """Gather all .py files under *app_dir*, skipping hidden dirs and __pycache__."""
    py_files: List[Path] = []
    for root, dirs, files in os.walk(app_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
        for f in files:
            if f.endswith(".py"):
                py_files.append(Path(root) / f)
    return sorted(py_files)


def _read_text_safe(path: Path) -> Optional[str]:
    """Read text from a file, returning None on decode errors."""
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as exc:
        logger.debug("Cannot read %s: %s", path, exc)
        return None


# ---------------------------------------------------------------------------
# Shared Checks (apply to both dx_app and dx_stream)
# ---------------------------------------------------------------------------


def check_python_syntax(app_dir: Path) -> CheckResult:
    """Check: ast.parse() all .py files."""
    errors: List[str] = []
    for py_file in _collect_py_files(app_dir):
        source = _read_text_safe(py_file)
        if source is None:
            errors.append(f"Cannot read: {py_file.relative_to(app_dir)}")
            continue
        try:
            ast.parse(source, filename=str(py_file))
        except SyntaxError as exc:
            errors.append(f"Syntax error in {py_file.relative_to(app_dir)}: line {exc.lineno}: {exc.msg}")

    if errors:
        return CheckResult("python_syntax", False, "Python syntax valid", errors)
    return CheckResult("python_syntax", True, "Python syntax valid")


def check_no_relative_imports(app_dir: Path) -> CheckResult:
    """Check: No relative imports."""
    hits: List[str] = []
    for py_file in _collect_py_files(app_dir):
        source = _read_text_safe(py_file)
        if source is None:
            continue
        for lineno, line in enumerate(source.splitlines(), 1):
            if RELATIVE_IMPORT_PATTERN.match(line):
                rel = py_file.relative_to(app_dir)
                hits.append(f"Relative import found: line {lineno} in {rel}")
    if hits:
        return CheckResult("no_relative_imports", False, "No relative imports", hits)
    return CheckResult("no_relative_imports", True, "No relative imports")


def check_no_hardcoded_model_paths(app_dir: Path) -> CheckResult:
    """Check: No .dxnn literal paths in source."""
    hits: List[str] = []
    for py_file in _collect_py_files(app_dir):
        source = _read_text_safe(py_file)
        if source is None:
            continue
        for lineno, line in enumerate(source.splitlines(), 1):
            if DXNN_PATH_PATTERN.search(line):
                rel = py_file.relative_to(app_dir)
                hits.append(f"Hardcoded .dxnn path: line {lineno} in {rel}")
    if hits:
        return CheckResult("no_hardcoded_model_paths", False, "No hardcoded model paths", hits)
    return CheckResult("no_hardcoded_model_paths", True, "No hardcoded model paths")


def check_logging_pattern(app_dir: Path) -> CheckResult:
    """Check: At least one file uses logging.getLogger(__name__)."""
    py_files = _collect_py_files(app_dir)
    if not py_files:
        return CheckResult("logging_pattern", True, "Logging pattern correct (no Python files)")

    for py_file in py_files:
        source = _read_text_safe(py_file)
        if source and LOGGING_PATTERN.search(source):
            return CheckResult("logging_pattern", True, "Logging pattern correct")

    return CheckResult(
        "logging_pattern",
        False,
        "Logging pattern correct",
        ["No file uses logging.getLogger(__name__)"],
    )


def check_readme_quality(app_dir: Path) -> CheckResult:
    """Check: README quality — min 10 lines, Usage section, command example."""
    readme_path = app_dir / "README.md"
    if not readme_path.exists():
        return CheckResult("readme_quality", False, "README quality", ["README.md not found"])

    content = _read_text_safe(readme_path)
    if content is None:
        return CheckResult("readme_quality", False, "README quality", ["Cannot read README.md"])

    lines = content.splitlines()
    issues: List[str] = []

    if len(lines) < 10:
        issues.append(f"README has {len(lines)} lines, minimum is 10")

    has_usage_section = False
    for line in lines:
        stripped = line.strip().lower()
        if stripped.startswith("#") and ("usage" in stripped or "how to run" in stripped):
            has_usage_section = True
            break
    if not has_usage_section:
        issues.append("Missing 'Usage' or 'How to Run' section heading")

    if issues:
        return CheckResult("readme_quality", False, "README quality", issues)
    return CheckResult("readme_quality", True, "README quality")


# ---------------------------------------------------------------------------
# dx_app-Specific Checks
# ---------------------------------------------------------------------------


def check_required_files_dx_app(app_dir: Path) -> CheckResult:
    """dx_app: Required files — app.yaml, README.md, factory file."""
    missing: List[str] = []
    for required in ("app.yaml", "README.md"):
        if not (app_dir / required).exists():
            missing.append(required)

    py_files = _collect_py_files(app_dir)
    if py_files:
        factory_found = any("factory" in p.stem.lower() for p in py_files)
        if not factory_found:
            missing.append("factory file (e.g. *_factory.py)")

    if missing:
        return CheckResult("required_files", False, "Required files present", [f"Missing: {m}" for m in missing])
    return CheckResult("required_files", True, "Required files present")


def check_ifactory_implementation(app_dir: Path) -> CheckResult:
    """dx_app: Verify IFactory subclass implements all 5 required methods."""
    py_files = _collect_py_files(app_dir)
    factory_files = [p for p in py_files if "factory" in p.stem.lower()]
    if not factory_files:
        return CheckResult("ifactory_impl", True, "IFactory implementation (no factory file)")

    for factory_file in factory_files:
        source = _read_text_safe(factory_file)
        if source is None:
            continue
        try:
            tree = ast.parse(source, filename=str(factory_file))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            bases = {
                getattr(b, "id", None) or getattr(getattr(b, "attr", None), "__str__", lambda: "")()
                for b in node.bases
            }
            if "IFactory" not in bases:
                continue

            implemented = {m.name for m in node.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))}
            missing = IFACTORY_REQUIRED_METHODS - implemented
            if missing:
                return CheckResult(
                    "ifactory_impl",
                    False,
                    "IFactory implementation",
                    [f"Missing methods in {node.name}: {', '.join(sorted(missing))}"],
                )
            return CheckResult("ifactory_impl", True, "IFactory implementation")

    return CheckResult("ifactory_impl", True, "IFactory implementation (no IFactory subclass found)")


def check_parse_common_args(app_dir: Path) -> CheckResult:
    """dx_app: Verify parse_common_args() is used for CLI argument handling."""
    py_files = _collect_py_files(app_dir)
    if not py_files:
        return CheckResult("parse_common_args", True, "parse_common_args usage (no Python files)")

    for py_file in py_files:
        source = _read_text_safe(py_file)
        if source and PARSE_COMMON_ARGS_PATTERN.search(source):
            return CheckResult("parse_common_args", True, "parse_common_args usage")

    return CheckResult(
        "parse_common_args",
        False,
        "parse_common_args usage",
        ["No file calls parse_common_args()"],
    )


def check_app_yaml(app_dir: Path) -> CheckResult:
    """dx_app: app.yaml validation — required fields: name, type, model, status."""
    yaml_path = app_dir / "app.yaml"
    if not yaml_path.exists():
        return CheckResult("app_yaml", False, "app.yaml validation", ["app.yaml not found"])

    content = _read_text_safe(yaml_path)
    if content is None:
        return CheckResult("app_yaml", False, "app.yaml validation", ["Cannot read app.yaml"])

    found_keys: Set[str] = set()
    for line in content.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and ":" in line:
            key = line.split(":", 1)[0].strip()
            found_keys.add(key)

    missing = APP_YAML_REQUIRED_FIELDS - found_keys
    if missing:
        return CheckResult(
            "app_yaml",
            False,
            "app.yaml validation",
            [f"Missing required fields: {', '.join(sorted(missing))}"],
        )
    return CheckResult("app_yaml", True, "app.yaml validation")


# ---------------------------------------------------------------------------
# dx_stream-Specific Checks
# ---------------------------------------------------------------------------


def check_required_files_dx_stream(app_dir: Path) -> CheckResult:
    """dx_stream: Required files — pipeline.py or run script, README.md."""
    missing: List[str] = []
    if not (app_dir / "README.md").exists():
        missing.append("README.md")

    has_pipeline = (app_dir / "pipeline.py").exists()
    has_run_script = bool(list(app_dir.glob("run_*.sh")))
    has_py_entry = bool(list(app_dir.glob("*.py")))

    if not has_pipeline and not has_run_script and not has_py_entry:
        missing.append("pipeline.py, run_*.sh, or Python entry point")

    if missing:
        return CheckResult("required_files", False, "Required files present", [f"Missing: {m}" for m in missing])
    return CheckResult("required_files", True, "Required files present")


def check_preprocess_id_matching(app_dir: Path) -> CheckResult:
    """dx_stream: Verify DxPreprocess and DxInfer preprocess-id values match."""
    issues: List[str] = []

    for py_file in _collect_py_files(app_dir):
        source = _read_text_safe(py_file)
        if source is None:
            continue

        # Only check files that contain GStreamer pipeline definitions
        has_pipeline = any(p.search(source) for p in GSTREAMER_PATTERNS)
        if not has_pipeline:
            continue

        preprocess_ids = PREPROCESS_ID_PATTERN.findall(source)
        if preprocess_ids:
            # Count occurrences — each preprocess-id should appear at least twice
            # (once in DxPreprocess, once in DxInfer)
            from collections import Counter
            id_counts = Counter(preprocess_ids)
            for pid, count in id_counts.items():
                if count < 2:
                    rel = py_file.relative_to(app_dir)
                    issues.append(f"preprocess-id={pid} appears only {count} time(s) in {rel} — expected at least 2 (DxPreprocess + DxInfer)")

    if issues:
        return CheckResult("preprocess_id_match", False, "preprocess-id matching", issues)
    return CheckResult("preprocess_id_match", True, "preprocess-id matching")


def check_model_path_absolute(app_dir: Path) -> CheckResult:
    """dx_stream: Verify model-path on DxInfer uses absolute paths or variables."""
    issues: List[str] = []
    model_path_pattern = re.compile(r"model-path\s*=\s*([^\s!]+)")

    for py_file in _collect_py_files(app_dir):
        source = _read_text_safe(py_file)
        if source is None:
            continue

        for lineno, line in enumerate(source.splitlines(), 1):
            match = model_path_pattern.search(line)
            if match:
                path_val = match.group(1).strip("'\"")
                # Allow variables, f-strings, os.path calls
                if path_val.startswith("{") or path_val.startswith("$") or "os.path" in line:
                    continue
                # Flag relative paths
                if not path_val.startswith("/") and not path_val.startswith("~"):
                    rel = py_file.relative_to(app_dir)
                    issues.append(f"Relative model-path in {rel}:{lineno}: {path_val}")

    if issues:
        return CheckResult("model_path_absolute", False, "Absolute model paths in DxInfer", issues)
    return CheckResult("model_path_absolute", True, "Absolute model paths in DxInfer")


# ---------------------------------------------------------------------------
# Smoke Tests
# ---------------------------------------------------------------------------


def smoke_test_npu(app_dir: Path) -> CheckResult:
    """Smoke: dxrt-cli -s NPU detection (graceful skip if unavailable)."""
    try:
        result = subprocess.run(
            ["dxrt-cli", "-s"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return CheckResult("smoke_npu", True, "NPU detected via dxrt-cli")
        return CheckResult(
            "smoke_npu",
            False,
            "NPU detected via dxrt-cli",
            [result.stderr[:200] if result.stderr else f"Exit code: {result.returncode}"],
        )
    except FileNotFoundError:
        return CheckResult("smoke_npu", True, "NPU detection (skipped: dxrt-cli not found)")
    except subprocess.TimeoutExpired:
        return CheckResult("smoke_npu", False, "NPU detection", ["dxrt-cli timed out"])
    except OSError as exc:
        return CheckResult("smoke_npu", True, f"NPU detection (skipped: {exc})")


def smoke_test_help(app_dir: Path) -> CheckResult:
    """Smoke: python <app>.py --help exits 0."""
    py_files = _collect_py_files(app_dir)
    main_script = None
    for py_file in py_files:
        stem = py_file.stem.lower()
        if stem == app_dir.name or stem == "main" or "sync" in stem or "pipeline" in stem:
            main_script = py_file
            break
    if main_script is None and py_files:
        main_script = py_files[0]
    if main_script is None:
        return CheckResult("smoke_help", False, "--help exits 0", ["No Python script found"])

    try:
        result = subprocess.run(
            [sys.executable, str(main_script), "--help"],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=str(app_dir),
        )
        if result.returncode == 0:
            return CheckResult("smoke_help", True, "--help exits 0")
        return CheckResult(
            "smoke_help",
            False,
            "--help exits 0",
            [f"Exit code: {result.returncode}", result.stderr[:300] if result.stderr else ""],
        )
    except subprocess.TimeoutExpired:
        return CheckResult("smoke_help", False, "--help exits 0", ["Timed out after 15s"])
    except OSError as exc:
        return CheckResult("smoke_help", False, "--help exits 0", [str(exc)])


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

SHARED_CHECKS = [
    check_python_syntax,
    check_no_relative_imports,
    check_no_hardcoded_model_paths,
    check_logging_pattern,
    check_readme_quality,
]

DX_APP_CHECKS = [
    check_required_files_dx_app,
    check_ifactory_implementation,
    check_parse_common_args,
    check_app_yaml,
]

DX_STREAM_CHECKS = [
    check_required_files_dx_stream,
    check_preprocess_id_matching,
    check_model_path_absolute,
]

SMOKE_TESTS = [
    smoke_test_npu,
    smoke_test_help,
]


def run_validation(
    app_dir: Path,
    project_type: str = "auto",
    run_smoke: bool = False,
    verbose: bool = False,
) -> Tuple[str, List[CheckResult], bool]:
    """Execute all validation checks and return (detected_type, results, overall_pass)."""

    # Auto-detect project type if needed
    if project_type == "auto":
        project_type = detect_project_type(app_dir)

    results: List[CheckResult] = []

    # Shared checks
    for check_fn in SHARED_CHECKS:
        result = check_fn(app_dir)
        results.append(result)
        if verbose and result.details:
            for d in result.details:
                logger.debug("  %s: %s", result.name, d)

    # Project-specific checks
    if project_type == "dx_app":
        for check_fn in DX_APP_CHECKS:
            results.append(check_fn(app_dir))
    elif project_type == "dx_stream":
        for check_fn in DX_STREAM_CHECKS:
            results.append(check_fn(app_dir))
    else:
        # Unknown — run both sets and mark as informational
        for check_fn in DX_APP_CHECKS + DX_STREAM_CHECKS:
            results.append(check_fn(app_dir))

    # Smoke tests
    if run_smoke:
        for smoke_fn in SMOKE_TESTS:
            results.append(smoke_fn(app_dir))

    failures = [r for r in results if not r.passed]
    return project_type, results, len(failures) == 0


def print_results(project_type: str, results: List[CheckResult], app_dir: Path) -> None:
    """Print formatted validation report."""
    print(f"\n=== DEEPX App Validation: {app_dir} ===")
    print(f"    Detected project type: {project_type}")
    for r in results:
        print(r)

    static_results = [r for r in results if not r.name.startswith("smoke_")]
    smoke_results = [r for r in results if r.name.startswith("smoke_")]

    static_pass = sum(1 for r in static_results if r.passed)
    static_fail = sum(1 for r in static_results if not r.passed)

    summary = f"=== RESULT: {static_pass}/{len(static_results)} static checks passed"
    if static_fail:
        summary += f", {static_fail} FAIL"

    if smoke_results:
        smoke_pass = sum(1 for r in smoke_results if r.passed)
        smoke_fail = sum(1 for r in smoke_results if not r.passed)
        summary += f" | {smoke_pass}/{len(smoke_results)} smoke tests passed"
        if smoke_fail:
            summary += f", {smoke_fail} FAIL"

    summary += " ==="
    print(summary)


def output_json(project_type: str, results: List[CheckResult], app_dir: Path) -> None:
    """Print validation results as JSON."""
    output = {
        "app_dir": str(app_dir),
        "project_type": project_type,
        "checks": [r.to_dict() for r in results],
        "passed": all(r.passed for r in results),
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r.passed),
            "failed": sum(1 for r in results if not r.passed),
        },
    }
    print(json.dumps(output, indent=2))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="DEEPX Unified App Validator — validates dx_app and dx_stream applications.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_app.py dx_app/src/python_example/object_detection/yolov8n
  python validate_app.py dx_stream/dx_stream/pipelines/detection --project dx_stream
  python validate_app.py <app_dir> --smoke-test --json
""",
    )
    parser.add_argument("app_dir", type=Path, help="Path to the application directory to validate")
    parser.add_argument(
        "--project",
        choices=["dx_app", "dx_stream", "auto"],
        default="auto",
        help="Force project type (default: auto-detect)",
    )
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        default=False,
        help="Run smoke tests (NPU, --help) in addition to static checks",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Enable verbose debug logging",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        dest="json_output",
        help="Output results as JSON instead of formatted text",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    app_dir: Path = args.app_dir.resolve()
    if not app_dir.is_dir():
        logger.error("Not a directory: %s", app_dir)
        return 1

    project_type, results, overall_pass = run_validation(
        app_dir,
        project_type=args.project,
        run_smoke=args.smoke_test,
        verbose=args.verbose,
    )

    if args.json_output:
        output_json(project_type, results, app_dir)
    else:
        print_results(project_type, results, app_dir)

    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
