#!/usr/bin/env python3
"""DEEPX Unified Framework Integrity Validator

Validates ALL THREE .deepx/ directories (dx-runtime, dx_app, dx_stream).
Checks cross-references between levels and verifies the integration layer
is consistent with both sub-project knowledge bases.

Usage:
    python validate_framework.py                     # Validate all 3 levels
    python validate_framework.py --level runtime     # Validate integration layer only
    python validate_framework.py --strict            # Warnings become errors
"""

import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEEPX_DIR_NAME = ".deepx"
MEMORY_DOMAIN_TAGS = {"[UNIVERSAL]", "[DX_APP]", "[DX_STREAM]", "[PPU]", "[INTEGRATION]"}

MD_FILE_REF_PATTERN = re.compile(r"`([^`]*\.(?:md|py|json|yaml|yml))`")
MD_LINK_PATTERN = re.compile(r"\[.*?\]\(([^)]+)\)")

# Expected sub-project directories relative to dx-runtime root
SUB_PROJECTS = {
    "dx_app": Path("dx_app"),
    "dx_stream": Path("dx_stream"),
}


# ---------------------------------------------------------------------------
# Result Container
# ---------------------------------------------------------------------------


class CheckResult:
    """Result of a single validation check."""

    def __init__(
        self,
        name: str,
        passed: bool,
        message: str,
        level: str = "runtime",
        details: Optional[List[str]] = None,
        fixable: bool = False,
    ):
        self.name = name
        self.passed = passed
        self.message = message
        self.level = level
        self.details = details or []
        self.fixable = fixable

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "message": self.message,
            "level": self.level,
            "details": self.details,
            "fixable": self.fixable,
        }

    def __str__(self) -> str:
        status = "[PASS]" if self.passed else "[FAIL]"
        line = f"{status} [{self.level}] {self.message}"
        if self.details:
            for d in self.details:
                line += f"\n       {d}"
        return line


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _find_repo_root(start: Optional[Path] = None) -> Path:
    """Locate the dx-runtime root by looking for .deepx/ directory."""
    search = start or Path.cwd()
    for ancestor in [search] + list(search.parents):
        candidate = ancestor / DEEPX_DIR_NAME
        if candidate.is_dir():
            return ancestor
    return search


def _read_text_safe(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as exc:
        logger.debug("Cannot read %s: %s", path, exc)
        return None


def _collect_actual_files(deepx_dir: Path) -> Set[str]:
    """Collect all files under a .deepx/ directory as relative paths."""
    result: Set[str] = set()
    if not deepx_dir.is_dir():
        return result
    for root, dirs, files in os.walk(deepx_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), deepx_dir)
            result.add(rel)
    return result


# ---------------------------------------------------------------------------
# Integration Layer Checks
# ---------------------------------------------------------------------------


def check_routing_table_paths(deepx_dir: Path, repo_root: Path) -> CheckResult:
    """Check 1: All file paths in README.md routing table exist."""
    readme = deepx_dir / "README.md"
    if not readme.exists():
        return CheckResult("routing_paths", False, "Routing table path resolution", "runtime", ["README.md not found"])

    content = _read_text_safe(readme)
    if content is None:
        return CheckResult("routing_paths", False, "Routing table path resolution", "runtime", ["Cannot read README.md"])

    missing: List[str] = []
    for match in MD_FILE_REF_PATTERN.finditer(content):
        ref_path = match.group(1)
        # Check paths that reference .deepx/ directories
        if ".deepx/" in ref_path:
            full_path = repo_root / ref_path
            if not full_path.exists():
                missing.append(f"Referenced path does not exist: {ref_path}")

    if missing:
        return CheckResult("routing_paths", False, "Routing table path resolution", "runtime", missing)
    return CheckResult("routing_paths", True, "Routing table path resolution", "runtime")


def check_agent_handoff_targets(deepx_dir: Path, repo_root: Path) -> CheckResult:
    """Check 2: Agent handoff targets all exist."""
    agents_dir = deepx_dir / "agents"
    if not agents_dir.is_dir():
        return CheckResult("agent_handoffs", True, "Agent handoff targets (no agents/)", "runtime")

    issues: List[str] = []
    for agent_file in sorted(agents_dir.glob("*.md")):
        content = _read_text_safe(agent_file)
        if content is None:
            continue

        for match in MD_FILE_REF_PATTERN.finditer(content):
            ref = match.group(1)
            if ".deepx/" in ref:
                full = repo_root / ref
                if not full.exists():
                    issues.append(f"{agent_file.name}: handoff target missing: {ref}")

    if issues:
        return CheckResult("agent_handoffs", False, "Agent handoff target verification", "runtime", issues)
    return CheckResult("agent_handoffs", True, "Agent handoff target verification", "runtime")


def check_memory_domain_tags(deepx_dir: Path) -> CheckResult:
    """Check 3: All entries in common_pitfalls.md have domain tags."""
    pitfalls_path = deepx_dir / "memory" / "common_pitfalls.md"
    if not pitfalls_path.exists():
        return CheckResult("memory_tags", True, "Memory domain tags (common_pitfalls.md not found)", "runtime")

    content = _read_text_safe(pitfalls_path)
    if content is None:
        return CheckResult("memory_tags", False, "Memory domain tags", "runtime", ["Cannot read common_pitfalls.md"])

    issues: List[str] = []
    entry_pattern = re.compile(r"^## ", re.MULTILINE)
    entries = entry_pattern.split(content)

    for i, entry in enumerate(entries[1:], 1):
        first_line = entry.split("\n")[0].strip()
        has_tag = any(tag in first_line for tag in MEMORY_DOMAIN_TAGS)
        if not has_tag:
            issues.append(f"Entry '{first_line[:60]}' (#{i}) missing domain tag in heading")

    if issues:
        return CheckResult("memory_tags", False, "Memory domain tags", "runtime", issues, fixable=True)
    return CheckResult("memory_tags", True, "Memory domain tags", "runtime")


def check_integration_has_integration_entries(deepx_dir: Path) -> CheckResult:
    """Check 4: Integration layer common_pitfalls.md has [INTEGRATION] entries."""
    pitfalls_path = deepx_dir / "memory" / "common_pitfalls.md"
    if not pitfalls_path.exists():
        return CheckResult("integration_entries", True, "Integration entries present (no file)", "runtime")

    content = _read_text_safe(pitfalls_path)
    if content is None:
        return CheckResult("integration_entries", False, "Integration entries present", "runtime")

    if "[INTEGRATION]" not in content:
        return CheckResult(
            "integration_entries",
            False,
            "Integration entries present",
            "runtime",
            ["No [INTEGRATION] domain tag found in common_pitfalls.md"],
        )
    return CheckResult("integration_entries", True, "Integration entries present", "runtime")


def check_slim_structure(deepx_dir: Path) -> CheckResult:
    """Check 5: Integration layer has slim structure (no duplicated sub-project content)."""
    issues: List[str] = []
    disallowed_dirs = ["toolsets", "prompts", "contextual-rules"]
    for dirname in disallowed_dirs:
        check_dir = deepx_dir / dirname
        if check_dir.is_dir() and any(check_dir.iterdir()):
            issues.append(f"Directory '{dirname}/' should not exist in integration layer (content moved to sub-projects)")

    if issues:
        return CheckResult("slim_structure", False, "Slim integration structure", "runtime", issues)
    return CheckResult("slim_structure", True, "Slim integration structure", "runtime")


# ---------------------------------------------------------------------------
# Sub-Project Checks
# ---------------------------------------------------------------------------


def check_sub_project_deepx_exists(repo_root: Path, sub_project: str) -> CheckResult:
    """Check: Sub-project has its own .deepx/ directory."""
    sub_deepx = repo_root / SUB_PROJECTS[sub_project] / DEEPX_DIR_NAME
    if not sub_deepx.is_dir():
        return CheckResult(
            f"{sub_project}_deepx_exists",
            False,
            f"{sub_project} .deepx/ directory exists",
            sub_project,
            [f"Expected: {sub_deepx}"],
        )
    return CheckResult(f"{sub_project}_deepx_exists", True, f"{sub_project} .deepx/ directory exists", sub_project)


def check_sub_project_claude_md(repo_root: Path, sub_project: str) -> CheckResult:
    """Check: Sub-project has a CLAUDE.md entry point."""
    claude_path = repo_root / SUB_PROJECTS[sub_project] / "CLAUDE.md"
    if not claude_path.exists():
        return CheckResult(
            f"{sub_project}_claude_md",
            False,
            f"{sub_project} CLAUDE.md exists",
            sub_project,
            [f"Expected: {claude_path}"],
        )
    return CheckResult(f"{sub_project}_claude_md", True, f"{sub_project} CLAUDE.md exists", sub_project)


# ---------------------------------------------------------------------------
# Cross-Reference Checks
# ---------------------------------------------------------------------------


def check_model_registry_consistency(repo_root: Path) -> CheckResult:
    """Check: Model names are consistent between dx_app and dx_stream registries."""
    dx_app_registry = repo_root / "dx_app" / "config" / "model_registry.json"
    dx_stream_model_list = repo_root / "dx_stream" / "model_list.json"

    if not dx_app_registry.exists() and not dx_stream_model_list.exists():
        return CheckResult(
            "model_consistency",
            True,
            "Model registry consistency (no registry files found)",
            "integration",
        )

    issues: List[str] = []

    app_models: Set[str] = set()
    stream_models: Set[str] = set()

    if dx_app_registry.exists():
        try:
            data = json.loads(dx_app_registry.read_text(encoding="utf-8"))
            if isinstance(data, list):
                app_models = {e.get("model_name", "") for e in data if isinstance(e, dict)}
                app_models.discard("")
            elif isinstance(data, dict):
                app_models = set(data.keys())
        except (json.JSONDecodeError, OSError) as exc:
            issues.append(f"Cannot parse dx_app registry: {exc}")

    if dx_stream_model_list.exists():
        try:
            data = json.loads(dx_stream_model_list.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                models_list = data.get("models", [])
                if isinstance(models_list, list):
                    # Strip .dxnn extension for comparison
                    stream_models = {m.replace(".dxnn", "") if isinstance(m, str) else "" for m in models_list}
                    stream_models.discard("")
                else:
                    stream_models = set(data.keys()) - {"version"}
            elif isinstance(data, list):
                stream_models = {e.get("model_name", "") for e in data if isinstance(e, dict)}
                stream_models.discard("")
        except (json.JSONDecodeError, OSError) as exc:
            issues.append(f"Cannot parse dx_stream model list: {exc}")

    if app_models and stream_models:
        # dx_stream models should be a subset of dx_app registry (dx_app is
        # the single source of truth).  Models that exist only in dx_app are
        # expected — dx_app has the full catalogue while dx_stream only
        # references models it actually uses in pipelines.
        # Use case-insensitive comparison because the two registries may use
        # different casing for the same model (e.g. "YoloV5S" vs "yolov5s").
        app_models_lower = {m.lower() for m in app_models}
        in_stream_not_app = {m for m in stream_models if m.lower() not in app_models_lower}
        if in_stream_not_app:
            for m in sorted(in_stream_not_app)[:5]:
                issues.append(f"In dx_stream model_list but not dx_app: {m}")

    if issues:
        return CheckResult("model_consistency", False, "Model registry consistency", "integration", issues)
    return CheckResult("model_consistency", True, "Model registry consistency", "integration")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def run_validation(
    repo_root: Path,
    level: str = "all",
    strict: bool = False,
) -> Tuple[List[CheckResult], bool]:
    """Execute all framework checks across levels."""
    results: List[CheckResult] = []
    deepx_dir = repo_root / DEEPX_DIR_NAME

    # Integration layer checks
    if level in ("all", "runtime"):
        results.append(check_routing_table_paths(deepx_dir, repo_root))
        results.append(check_agent_handoff_targets(deepx_dir, repo_root))
        results.append(check_memory_domain_tags(deepx_dir))
        results.append(check_integration_has_integration_entries(deepx_dir))
        results.append(check_slim_structure(deepx_dir))

    # Sub-project existence checks
    if level in ("all", "sub_projects"):
        for sub in SUB_PROJECTS:
            results.append(check_sub_project_deepx_exists(repo_root, sub))
            results.append(check_sub_project_claude_md(repo_root, sub))

    # Cross-reference checks
    if level in ("all", "integration"):
        results.append(check_model_registry_consistency(repo_root))

    failures = [r for r in results if not r.passed]
    return results, len(failures) == 0


def print_results(results: List[CheckResult], repo_root: Path) -> None:
    """Print formatted validation report."""
    print(f"\n=== DEEPX Unified Framework Integrity: {repo_root} ===")
    for r in results:
        print(r)

    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)
    summary = f"=== RESULT: {passed}/{len(results)} checks passed"
    if failed:
        summary += f", {failed} FAIL"
    summary += " ==="
    print(summary)

    # Group by level
    levels = {}
    for r in results:
        levels.setdefault(r.level, []).append(r)
    print("\nBy level:")
    for level_name, level_results in sorted(levels.items()):
        lp = sum(1 for r in level_results if r.passed)
        lf = sum(1 for r in level_results if not r.passed)
        status = "OK" if lf == 0 else f"{lf} FAIL"
        print(f"  {level_name}: {lp}/{len(level_results)} ({status})")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="DEEPX Unified Framework Integrity Validator — checks all 3 .deepx/ levels.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_framework.py
  python validate_framework.py --level runtime
  python validate_framework.py --strict --json
""",
    )
    parser.add_argument(
        "repo_root",
        type=Path,
        nargs="?",
        default=None,
        help="Path to dx-runtime repository root (auto-detected if omitted)",
    )
    parser.add_argument(
        "--level",
        choices=["all", "runtime", "sub_projects", "integration"],
        default="all",
        help="Which level(s) to validate (default: all)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Treat warnings as errors",
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
        help="Output results as JSON",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    if args.repo_root:
        repo_root = args.repo_root.resolve()
    else:
        repo_root = _find_repo_root()

    if not (repo_root / DEEPX_DIR_NAME).is_dir():
        logger.error("Cannot find .deepx/ in %s", repo_root)
        return 1

    results, overall_pass = run_validation(
        repo_root,
        level=args.level,
        strict=args.strict,
    )

    if args.json_output:
        output = {
            "repo_root": str(repo_root),
            "checks": [r.to_dict() for r in results],
            "passed": overall_pass,
        }
        print(json.dumps(output, indent=2))
    else:
        print_results(results, repo_root)

    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
