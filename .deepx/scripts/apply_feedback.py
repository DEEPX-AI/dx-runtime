#!/usr/bin/env python3
"""Apply Feedback — Apply approved feedback proposals to knowledge base files.

Reads a feedback report JSON (from feedback_collector.py), filters by approved
IDs, and applies the corresponding modifications to the target .deepx/ files.

Usage:
    # Approve specific items
    python .deepx/scripts/apply_feedback.py \
        --report feedback_report.json \
        --approve FB-001,FB-002

    # Approve all proposals
    python .deepx/scripts/apply_feedback.py \
        --report feedback_report.json \
        --approve-all

    # Dry run (show what would change without modifying files)
    python .deepx/scripts/apply_feedback.py \
        --report feedback_report.json \
        --approve-all \
        --dry-run

    # Reject specific items (apply all others)
    python .deepx/scripts/apply_feedback.py \
        --report feedback_report.json \
        --approve-all \
        --reject FB-003
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# File modification actions
# ---------------------------------------------------------------------------

def resolve_target_path(repo_root: Path, target_level: str, target_file: str) -> Path:
    """Resolve the absolute path for a feedback target."""
    if target_level == "runtime":
        return repo_root / ".deepx" / target_file
    elif target_level == "dx_app":
        return repo_root / "dx_app" / ".deepx" / target_file
    elif target_level == "dx_stream":
        return repo_root / "dx_stream" / ".deepx" / target_file
    else:
        return repo_root / ".deepx" / target_file


def count_existing_entries(content: str, pattern: str = r"^## \d+\.") -> int:
    """Count numbered entries in a markdown file."""
    return len(re.findall(pattern, content, re.MULTILINE))


def action_append_pitfall(
    file_path: Path, preview: str, dry_run: bool = False,
) -> tuple[bool, str]:
    """Append a new pitfall entry to a common_pitfalls.md file."""
    if not file_path.exists():
        return False, f"Target file does not exist: {file_path}"

    content = file_path.read_text()
    next_num = count_existing_entries(content) + 1

    # Replace the placeholder "N." with the actual number
    entry = preview.replace("## N.", f"## {next_num}.")
    new_content = content.rstrip() + "\n\n---\n\n" + entry + "\n"

    if dry_run:
        return True, f"[DRY RUN] Would append entry #{next_num} to {file_path.name}"

    file_path.write_text(new_content)
    return True, f"Appended entry #{next_num} to {file_path.name}"


def action_append_rule(
    file_path: Path, preview: str, dry_run: bool = False,
) -> tuple[bool, str]:
    """Append a new rule section to a contextual-rules file."""
    if not file_path.exists():
        return False, f"Target file does not exist: {file_path}"

    content = file_path.read_text()
    new_content = content.rstrip() + "\n\n" + preview + "\n"

    if dry_run:
        return True, f"[DRY RUN] Would append rule to {file_path.name}"

    file_path.write_text(new_content)
    return True, f"Appended rule to {file_path.name}"


def action_fix_reference(
    file_path: Path, preview: str, dry_run: bool = False,
) -> tuple[bool, str]:
    """Fix a broken file path reference. Requires manual parsing of the preview."""
    if not file_path.exists():
        return False, f"Target file does not exist: {file_path}"

    # Preview format: "Fix broken reference: ..." or "Replace X → Y"
    # For automated fixes, we need the old and new paths
    match = re.search(r"Replace [`']?(.+?)[`']?\s*→\s*[`']?(.+?)[`']?\s*$", preview)
    if not match:
        return False, f"Cannot auto-fix: manual review needed for {file_path.name}"

    old_ref, new_ref = match.group(1).strip(), match.group(2).strip()
    content = file_path.read_text()
    if old_ref not in content:
        return False, f"Old reference '{old_ref}' not found in {file_path.name}"

    new_content = content.replace(old_ref, new_ref)

    if dry_run:
        return True, f"[DRY RUN] Would replace '{old_ref}' → '{new_ref}' in {file_path.name}"

    file_path.write_text(new_content)
    return True, f"Replaced '{old_ref}' → '{new_ref}' in {file_path.name}"


def action_add_domain_tag(
    file_path: Path, preview: str, dry_run: bool = False,
) -> tuple[bool, str]:
    """Add missing domain tag to a memory entry."""
    # This is a complex operation that depends on context
    # For now, flag it for manual review
    return False, f"Domain tag addition requires manual review: {file_path.name}"


def action_update_skill(
    file_path: Path, preview: str, dry_run: bool = False,
) -> tuple[bool, str]:
    """Add entry to Common Failures table in a skill doc."""
    if not file_path.exists():
        return False, f"Target file does not exist: {file_path}"

    content = file_path.read_text()
    marker = "<!-- END_COMMON_FAILURES -->"

    if marker not in content:
        # Append to end if marker not found
        new_content = content.rstrip() + "\n\n" + preview + "\n"
    else:
        new_content = content.replace(marker, preview + "\n" + marker)

    if dry_run:
        return True, f"[DRY RUN] Would update skill {file_path.name}"

    file_path.write_text(new_content)
    return True, f"Updated skill {file_path.name}"


def action_update_knowledge(
    file_path: Path, preview: str, dry_run: bool = False,
) -> tuple[bool, str]:
    """Add new insight to knowledge_base.yaml."""
    return False, f"Knowledge YAML update requires manual review: {file_path.name}"


# Action registry
ACTIONS = {
    "append_pitfall": action_append_pitfall,
    "append_rule": action_append_rule,
    "fix_reference": action_fix_reference,
    "add_domain_tag": action_add_domain_tag,
    "update_skill": action_update_skill,
    "update_knowledge": action_update_knowledge,
}


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def apply_proposals(
    repo_root: Path,
    report: dict,
    approved_ids: set[str],
    dry_run: bool = False,
) -> list[dict]:
    """Apply approved feedback proposals and return results."""
    results = []

    for proposal in report.get("proposed_feedback", []):
        pid = proposal["id"]
        if pid not in approved_ids:
            results.append({
                "id": pid, "applied": False, "reason": "not approved",
            })
            continue

        action_name = proposal["action"]
        action_fn = ACTIONS.get(action_name)
        if not action_fn:
            results.append({
                "id": pid, "applied": False,
                "reason": f"unknown action: {action_name}",
            })
            continue

        target_path = resolve_target_path(
            repo_root, proposal["target_level"], proposal["target_file"],
        )

        success, message = action_fn(target_path, proposal["preview"], dry_run)
        results.append({
            "id": pid, "applied": success, "reason": message,
            "target": str(target_path),
        })

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Apply approved feedback proposals to knowledge base files.",
    )
    parser.add_argument(
        "--report", required=True,
        help="Path to feedback_report.json from feedback_collector.py",
    )
    parser.add_argument(
        "--approve", type=str, default="",
        help="Comma-separated list of proposal IDs to approve (e.g., FB-001,FB-002)",
    )
    parser.add_argument(
        "--approve-all", action="store_true",
        help="Approve all proposals",
    )
    parser.add_argument(
        "--reject", type=str, default="",
        help="Comma-separated list of proposal IDs to reject (used with --approve-all)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would change without modifying files",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output results as JSON",
    )
    args = parser.parse_args()

    # Load report
    report_path = Path(args.report)
    if not report_path.exists():
        print(f"Error: Report file not found: {report_path}", file=sys.stderr)
        return 2

    with open(report_path) as f:
        report = json.load(f)

    # Determine approved IDs
    rejected = set(args.reject.split(",")) if args.reject else set()
    if args.approve_all:
        approved = {
            p["id"] for p in report.get("proposed_feedback", [])
        } - rejected
    elif args.approve:
        approved = set(args.approve.split(",")) - rejected
    else:
        print("Error: Must specify --approve or --approve-all", file=sys.stderr)
        return 2

    # Determine repo root
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent

    print(f"Applying feedback ({len(approved)} approved, {len(rejected)} rejected)")
    if args.dry_run:
        print("[DRY RUN MODE]\n")

    # Apply
    results = apply_proposals(repo_root, report, approved, args.dry_run)

    # Output
    applied = [r for r in results if r["applied"]]
    skipped = [r for r in results if not r["applied"]]

    if args.json:
        print(json.dumps({"applied": applied, "skipped": skipped}, indent=2))
    else:
        if applied:
            print(f"\n--- Applied ({len(applied)}) ---")
            for r in applied:
                print(f"  [OK] {r['id']}: {r['reason']}")
        if skipped:
            print(f"\n--- Skipped ({len(skipped)}) ---")
            for r in skipped:
                print(f"  [--] {r['id']}: {r['reason']}")
        print(f"\nDone. {len(applied)} applied, {len(skipped)} skipped.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
