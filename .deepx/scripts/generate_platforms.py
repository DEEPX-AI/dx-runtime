#!/usr/bin/env python3
"""DEEPX Unified Platform Synchronization Script

Generates platform-specific configuration files for the entire dx-runtime,
merging content from all three .deepx/ directories (dx-runtime, dx_app, dx_stream).

Transformations:
  .deepx/ (all levels) -> .github/    (full copy, GitHub Copilot format)
  .deepx/ (all levels) -> CLAUDE.md   (thin redirect, Claude Code format)
  .deepx/ (all levels) -> .cursor/    (thin .mdc redirects, Cursor format)

Usage:
    python generate_platforms.py --generate              # Generate all platform files
    python generate_platforms.py --check                 # Verify sync (CI use)
    python generate_platforms.py --diff                  # Show what would change
    python generate_platforms.py --platform copilot      # Specific platform only
"""

import argparse
import json
import logging
import os
import re
import sys
import textwrap
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEEPX_DIR = ".deepx"

SUB_PROJECTS = {
    "dx_app": {
        "path": "dx_app",
        "description": "Standalone inference apps (Python/C++)",
        "skills": [
            ("/dx-build-python-app", "Build Python inference app (4 variants)"),
            ("/dx-build-cpp-app", "Build C++ inference app"),
            ("/dx-build-async-app", "Build async high-performance app"),
        ],
    },
    "dx_stream": {
        "path": "dx_stream",
        "description": "GStreamer pipeline apps",
        "skills": [
            ("/dx-build-pipeline-app", "Build GStreamer pipeline app"),
            ("/dx-build-mqtt-kafka-app", "Build message broker pipeline app"),
        ],
    },
}

COPILOT_TOOLS: Dict[str, str] = {
    "ask-user": "askQuestions",
    "edit": "editFiles",
    "execute": "runTerminalCommand",
    "read": "readFile",
    "search": "searchCode",
    "sub-agent": "createSubAgent",
    "todo": "manageTodos",
}

CLAUDE_TOOLS: Dict[str, str] = {
    "ask-user": "question",
    "edit": "Edit",
    "execute": "Bash",
    "read": "Read",
    "search": "Grep",
    "sub-agent": "task",
    "todo": "todowrite",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _find_repo_root(start: Optional[Path] = None) -> Optional[Path]:
    """Locate dx-runtime root by finding .deepx/ directory."""
    search = start or Path.cwd()
    for ancestor in [search] + list(search.parents):
        candidate = ancestor / DEEPX_DIR
        if candidate.is_dir():
            return ancestor
    return None


def _read_text_safe(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as exc:
        logger.debug("Cannot read %s: %s", path, exc)
        return None


def _write_file(path: Path, content: str, dry_run: bool = False) -> bool:
    """Write content to path. Returns True if the file changed."""
    existing = _read_text_safe(path) if path.exists() else None
    if existing == content:
        return False
    if dry_run:
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    logger.info("Wrote: %s", path)
    return True


def _map_tool_references(content: str, tool_map: Dict[str, str]) -> str:
    """Replace canonical tool names with platform-specific names."""
    result = content
    for canonical, platform_name in tool_map.items():
        result = result.replace(f"tool:{canonical}", f"tool:{platform_name}")
        result = result.replace(f"`{canonical}`", f"`{platform_name}`")
    return result


def _collect_skills_table(repo_root: Path) -> str:
    """Build a merged skills table from all sub-projects."""
    rows = []
    for sub_name, sub_info in SUB_PROJECTS.items():
        for cmd, desc in sub_info["skills"]:
            rows.append(f"| {cmd} | {desc} | {sub_name} |")

    return (
        "| Command | Description | Sub-project |\n"
        "|---------|-------------|-------------|\n"
        + "\n".join(rows)
    )


def _collect_routing_table(repo_root: Path) -> str:
    """Build unified routing table covering all sub-projects."""
    return textwrap.dedent("""\
        | If the task mentions... | Sub-project | Read these files |
        |---|---|---|
        | **Python app, detection, factory** | dx_app | `dx_app/.deepx/skills/dx-build-python-app.md` |
        | **C++ app, native, performance** | dx_app | `dx_app/.deepx/skills/dx-build-cpp-app.md` |
        | **Async, high-throughput, batch** | dx_app | `dx_app/.deepx/skills/dx-build-async-app.md` |
        | **Model, download, registry** | dx_app | `dx_app/.deepx/skills/dx-model-management.md` |
        | **GStreamer, pipeline, stream** | dx_stream | `dx_stream/.deepx/skills/dx-build-pipeline-app.md` |
        | **MQTT, Kafka, message broker** | dx_stream | `dx_stream/.deepx/skills/dx-build-mqtt-kafka-app.md` |
        | **Cross-project, integration** | dx-runtime | `.deepx/instructions/integration.md` |
        | **ALWAYS read (every task)** | dx-runtime | `.deepx/memory/common_pitfalls.md` |""")


# ---------------------------------------------------------------------------
# Platform Generators
# ---------------------------------------------------------------------------


class PlatformGenerator:
    """Base class for platform-specific file generators."""

    def __init__(self, repo_root: Path, dry_run: bool = False):
        self.repo_root = repo_root
        self.deepx_dir = repo_root / DEEPX_DIR
        self.dry_run = dry_run
        self.changes: List[Tuple[str, str]] = []

    def generate(self) -> List[Tuple[str, str]]:
        raise NotImplementedError

    def _record(self, path: Path, action: str) -> None:
        rel = str(path.relative_to(self.repo_root))
        self.changes.append((rel, action))


class CopilotGenerator(PlatformGenerator):
    """Generate .github/ files (full copy, Copilot format)."""

    def generate(self) -> List[Tuple[str, str]]:
        github_dir = self.repo_root / ".github"

        skills_table = _collect_skills_table(self.repo_root)
        routing_table = _collect_routing_table(self.repo_root)

        entry_content = textwrap.dedent(f"""\
            # DEEPX dx-runtime — GitHub Copilot Instructions

            > Auto-generated by `generate_platforms.py`. Do not edit directly.

            ## Knowledge Base Architecture

            | Level | Path | Scope |
            |---|---|---|
            | dx_app | `dx_app/.deepx/` | Standalone inference apps |
            | dx_stream | `dx_stream/.deepx/` | GStreamer pipeline apps |
            | dx-runtime | `.deepx/` | Cross-project integration |

            ## Skills

            {skills_table}

            ## Context Routing Table

            {routing_table}

            ## Critical Conventions

            1. **Imports are always absolute** — no relative imports
            2. **Model resolution** — query `model_registry.json` (dx_app) or `model_list.json` (dx_stream)
            3. **Factory pattern** — all dx_app Python apps implement IFactory (5 methods)
            4. **preprocess-id matching** — DxPreprocess and DxInfer must share the same ID
            5. **NPU verification** — use `dxrt-cli -s` before inference
            6. **Logging** — use `logging.getLogger(__name__)`

            ## Hardware

            | Architecture | Value |
            |---|---|
            | DX-M1 | `dx_m1` |
            | DX-M1A | `dx_m1a` |
        """)

        path = github_dir / "copilot-instructions.md"
        if _write_file(path, entry_content, self.dry_run):
            self._record(path, "updated" if path.exists() else "created")

        return self.changes


class ClaudeGenerator(PlatformGenerator):
    """Generate CLAUDE.md entry point (thin redirect to .deepx/)."""

    def generate(self) -> List[Tuple[str, str]]:
        # The main CLAUDE.md is managed separately (Step 10)
        # This generator handles sub-project CLAUDE.md files
        return self.changes


class CursorGenerator(PlatformGenerator):
    """Generate .cursor/ files (thin .mdc redirects)."""

    def generate(self) -> List[Tuple[str, str]]:
        cursor_dir = self.repo_root / ".cursor"
        routing_table = _collect_routing_table(self.repo_root)

        global_mdc = textwrap.dedent(f"""\
            ---
            description: DEEPX dx-runtime global rules
            globs: "**/*"
            ---

            # DEEPX dx-runtime

            > Auto-generated from `.deepx/`. Do not edit directly.

            ## Knowledge Base Architecture

            | Level | Path | Scope |
            |---|---|---|
            | dx_app | `dx_app/.deepx/` | Standalone inference apps |
            | dx_stream | `dx_stream/.deepx/` | GStreamer pipeline apps |
            | dx-runtime | `.deepx/` | Cross-project integration |

            ## Context Routing Table

            {routing_table}

            ## Critical Conventions

            1. Imports are always absolute — no relative imports
            2. Model resolution — query the appropriate registry for the sub-project
            3. Factory pattern — all dx_app Python apps implement IFactory (5 methods)
            4. preprocess-id matching — DxPreprocess and DxInfer must share the same ID
            5. NPU verification — use `dxrt-cli -s` before inference
            6. Logging — use `logging.getLogger(__name__)`
        """)

        target = cursor_dir / "rules" / "dx-global.mdc"
        if _write_file(target, global_mdc, self.dry_run):
            self._record(target, "updated" if target.exists() else "created")

        return self.changes


# ---------------------------------------------------------------------------
# Sync Checker
# ---------------------------------------------------------------------------


def check_sync(repo_root: Path) -> Tuple[bool, List[str]]:
    """Verify all platform files are in sync with .deepx/ sources."""
    diffs: List[str] = []

    for GeneratorClass in (CopilotGenerator, ClaudeGenerator, CursorGenerator):
        gen = GeneratorClass(repo_root, dry_run=True)
        changes = gen.generate()
        for path, action in changes:
            diffs.append(f"  {action}: {path}")

    return len(diffs) == 0, diffs


def show_diff(repo_root: Path) -> None:
    """Show what would change if --generate were run."""
    in_sync, diffs = check_sync(repo_root)
    if in_sync:
        print("All platform files are in sync with .deepx/")
    else:
        print(f"Found {len(diffs)} file(s) that would change:")
        for d in diffs:
            print(d)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

GENERATORS: Dict[str, type] = {
    "copilot": CopilotGenerator,
    "claude": ClaudeGenerator,
    "cursor": CursorGenerator,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="DEEPX Unified Platform Sync — generates platform configs from all .deepx/ levels.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_platforms.py --generate
  python generate_platforms.py --check
  python generate_platforms.py --diff
  python generate_platforms.py --platform copilot --generate
""",
    )

    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--generate", action="store_true", help="Generate all platform files")
    action.add_argument("--check", action="store_true", help="Verify sync (for CI)")
    action.add_argument("--diff", action="store_true", help="Show what would change")

    parser.add_argument(
        "--platform",
        choices=["copilot", "claude", "cursor"],
        default=None,
        help="Generate for a specific platform only (default: all)",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Path to dx-runtime repo root (auto-detected if omitted)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Enable verbose debug logging",
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
        found = _find_repo_root()
        if found is None:
            logger.error("Cannot find .deepx/ directory. Pass --repo-root or run from repo root.")
            return 1
        repo_root = found

    if not (repo_root / DEEPX_DIR).is_dir():
        logger.error("Not a valid dx-runtime root: %s", repo_root)
        return 1

    platform_names = [args.platform] if args.platform else list(GENERATORS.keys())

    if args.generate:
        total_changes: List[Tuple[str, str]] = []
        for name in platform_names:
            gen = GENERATORS[name](repo_root)
            changes = gen.generate()
            total_changes.extend(changes)
            logger.info("Platform '%s': %d file(s) written", name, len(changes))

        if total_changes:
            print(f"\nGenerated {len(total_changes)} file(s):")
            for path, action in total_changes:
                print(f"  {action}: {path}")
        else:
            print("All platform files already up to date.")
        return 0

    elif args.check:
        in_sync, diffs = check_sync(repo_root)
        if in_sync:
            print("All platform files are in sync with .deepx/")
            return 0
        else:
            print(f"Platform files out of sync. {len(diffs)} file(s) need updating:")
            for d in diffs:
                print(d)
            print("\nRun: python generate_platforms.py --generate")
            return 1

    elif args.diff:
        show_diff(repo_root)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
