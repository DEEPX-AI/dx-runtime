#!/usr/bin/env python3
"""Feedback Collector — Run validators, unify results, propose feedback.

Calls the 6 validation scripts (validate_app.py, validate_framework.py) across
all 3 .deepx/ levels, normalizes their heterogeneous JSON output into a unified
UnifiedFinding model, and maps failures to knowledge-base update proposals using
feedback_rules.yaml.

Usage:
    # Full validation (all levels, app + framework)
    python .deepx/scripts/feedback_collector.py --all

    # Validate specific app directories
    python .deepx/scripts/feedback_collector.py \
        --app-dirs dx_app/src/python_example/object_detection/yolov8n/

    # Framework-only check
    python .deepx/scripts/feedback_collector.py --framework-only

    # Output JSON report
    python .deepx/scripts/feedback_collector.py --all --output report.json
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import yaml


# ---------------------------------------------------------------------------
# Unified Result Model
# ---------------------------------------------------------------------------

@dataclass
class UnifiedFinding:
    """Normalized finding from any of the 6 validation scripts."""
    source: str            # e.g. "dx_app/validate_app"
    level: str             # "dx_app", "dx_stream", "runtime", "integration"
    check_name: str        # normalized check name
    passed: bool
    severity: str          # "error", "warning", "info"
    message: str
    category: str          # "app_code" or "framework_integrity"
    fixable: bool          # merged from auto_fixable / fixable
    details: list[str] = field(default_factory=list)
    line: Optional[int] = None
    source_file: Optional[str] = None


@dataclass
class FeedbackProposal:
    """Proposed knowledge-base update based on a finding."""
    id: str                        # "FB-001"
    finding: UnifiedFinding
    target_file: str               # relative path from .deepx/ root
    target_level: str              # which .deepx/ to modify
    action: str                    # action name from rules
    preview: str                   # human-readable preview of the change
    status: str = "pending_approval"


@dataclass
class FeedbackReport:
    """Complete output of the feedback collector."""
    timestamp: str
    repo_root: str
    validation_summary: dict
    findings: list[UnifiedFinding]
    proposed_feedback: list[FeedbackProposal]

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "repo_root": self.repo_root,
            "validation_summary": self.validation_summary,
            "findings": [asdict(f) for f in self.findings],
            "proposed_feedback": [
                {**asdict(p), "finding": asdict(p.finding)}
                for p in self.proposed_feedback
            ],
        }


# ---------------------------------------------------------------------------
# Adapters — normalize each script's JSON output
# ---------------------------------------------------------------------------

def _norm_severity(raw: str) -> str:
    """Normalize severity to lowercase 'error'|'warning'|'info'."""
    return raw.lower().strip() if raw else "error"


def adapt_dx_app_validate_app(data: dict) -> list[UnifiedFinding]:
    """Adapter for dx_app/.deepx/scripts/validate_app.py --json output."""
    findings = []
    for r in data.get("results", []):
        findings.append(UnifiedFinding(
            source="dx_app/validate_app",
            level="dx_app",
            check_name=r["name"],
            passed=r["passed"],
            severity=_norm_severity(r.get("severity", "error")),
            message=r.get("message", ""),
            category="app_code",
            fixable=False,
            source_file=data.get("target_dir"),
        ))
    return findings


def adapt_dx_app_validate_framework(data: dict) -> list[UnifiedFinding]:
    """Adapter for dx_app/.deepx/scripts/validate_framework.py --json."""
    findings = []
    for r in data.get("results", []):
        findings.append(UnifiedFinding(
            source="dx_app/validate_framework",
            level="dx_app",
            check_name=r["name"],
            passed=r["passed"],
            severity=_norm_severity(r.get("severity", "error")),
            message=r.get("message", ""),
            category="framework_integrity",
            fixable=False,
        ))
    return findings


def adapt_dx_stream_validate_app(data: dict) -> list[UnifiedFinding]:
    """Adapter for dx_stream/.deepx/scripts/validate_app.py --json."""
    findings = []
    for f in data.get("findings", []):
        findings.append(UnifiedFinding(
            source="dx_stream/validate_app",
            level="dx_stream",
            check_name=f["check"],
            passed=f["severity"] != "ERROR",
            severity=_norm_severity(f["severity"]),
            message=f.get("message", ""),
            category="app_code",
            fixable=False,
            line=f.get("line"),
            source_file=data.get("script"),
        ))
    return findings


def adapt_dx_stream_validate_framework(data: dict) -> list[UnifiedFinding]:
    """Adapter for dx_stream/.deepx/scripts/validate_framework.py --json."""
    findings = []
    for r in data.get("results", []):
        findings.append(UnifiedFinding(
            source="dx_stream/validate_framework",
            level="dx_stream",
            check_name=r["check"],
            passed=r["passed"],
            severity="error" if not r["passed"] else "info",
            message=r.get("message", ""),
            category="framework_integrity",
            fixable=r.get("auto_fixable", False),
        ))
    return findings


def adapt_unified_validate_app(data: dict) -> list[UnifiedFinding]:
    """Adapter for .deepx/scripts/validate_app.py --json (unified)."""
    findings = []
    for r in data.get("checks", []):
        findings.append(UnifiedFinding(
            source="runtime/validate_app",
            level=data.get("project_type", "runtime"),
            check_name=r["name"],
            passed=r["passed"],
            severity="error" if not r["passed"] else "info",
            message=r.get("message", ""),
            category="app_code",
            fixable=False,
            details=r.get("details", []),
            source_file=data.get("app_dir"),
        ))
    return findings


def adapt_unified_validate_framework(data: dict) -> list[UnifiedFinding]:
    """Adapter for .deepx/scripts/validate_framework.py --json (unified)."""
    findings = []
    for r in data.get("checks", []):
        findings.append(UnifiedFinding(
            source="runtime/validate_framework",
            level=r.get("level", "runtime"),
            check_name=r["name"],
            passed=r["passed"],
            severity="error" if not r["passed"] else "info",
            message=r.get("message", ""),
            category="framework_integrity",
            fixable=r.get("fixable", False),
            details=r.get("details", []),
        ))
    return findings


# Adapter registry: (level, script_type) → adapter function
ADAPTERS = {
    ("dx_app", "validate_app"): adapt_dx_app_validate_app,
    ("dx_app", "validate_framework"): adapt_dx_app_validate_framework,
    ("dx_stream", "validate_app"): adapt_dx_stream_validate_app,
    ("dx_stream", "validate_framework"): adapt_dx_stream_validate_framework,
    ("runtime", "validate_app"): adapt_unified_validate_app,
    ("runtime", "validate_framework"): adapt_unified_validate_framework,
}


# ---------------------------------------------------------------------------
# Script runner
# ---------------------------------------------------------------------------

def run_validator(script_path: Path, args: list[str]) -> Optional[dict]:
    """Run a validation script with --json and return parsed output."""
    cmd = [sys.executable, str(script_path), "--json"] + args
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60,
        )
        # Scripts exit 0 on pass, 1 on fail — both produce valid JSON
        output = result.stdout.strip()
        if output:
            return json.loads(output)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"  [WARN] Failed to run {script_path.name}: {e}", file=sys.stderr)
    return None


def collect_all_findings(
    repo_root: Path,
    app_dirs: list[str],
    framework_only: bool = False,
    app_only: bool = False,
) -> list[UnifiedFinding]:
    """Run all applicable validators and collect unified findings."""
    all_findings: list[UnifiedFinding] = []

    levels = {
        "dx_app": repo_root / "dx_app" / ".deepx" / "scripts",
        "dx_stream": repo_root / "dx_stream" / ".deepx" / "scripts",
        "runtime": repo_root / ".deepx" / "scripts",
    }

    for level_name, scripts_dir in levels.items():
        if not scripts_dir.exists():
            continue

        # Framework validation
        if not app_only:
            fw_script = scripts_dir / "validate_framework.py"
            if fw_script.exists():
                print(f"  Running {level_name}/validate_framework.py ...")
                data = run_validator(fw_script, [])
                if data:
                    adapter = ADAPTERS.get((level_name, "validate_framework"))
                    if adapter:
                        all_findings.extend(adapter(data))

        # App validation
        if not framework_only:
            app_script = scripts_dir / "validate_app.py"
            if app_script.exists() and app_dirs:
                for app_dir in app_dirs:
                    print(f"  Running {level_name}/validate_app.py on {app_dir} ...")
                    data = run_validator(app_script, [app_dir])
                    if data:
                        adapter = ADAPTERS.get((level_name, "validate_app"))
                        if adapter:
                            all_findings.extend(adapter(data))

    return all_findings


# ---------------------------------------------------------------------------
# Feedback proposal generation
# ---------------------------------------------------------------------------

def load_rules(repo_root: Path) -> dict:
    """Load feedback_rules.yaml."""
    rules_path = repo_root / ".deepx" / "knowledge" / "feedback_rules.yaml"
    if not rules_path.exists():
        print(f"  [WARN] Rules file not found: {rules_path}", file=sys.stderr)
        return {"rules": [], "actions": {}}
    with open(rules_path) as f:
        return yaml.safe_load(f)


def match_rule(finding: UnifiedFinding, rules: list[dict]) -> Optional[dict]:
    """Find the first matching rule for a finding."""
    for rule in rules:
        pattern = rule.get("check_pattern", "")
        if not re.search(pattern, finding.check_name):
            continue
        # Check source filter
        source_filter = rule.get("source", "")
        if source_filter and source_filter not in finding.source:
            continue
        # Check level filter
        level_filter = rule.get("level", "any")
        if level_filter != "any" and level_filter != finding.level:
            continue
        # Check severity filter
        sev_filter = rule.get("severity_filter", "info")
        sev_order = {"error": 0, "warning": 1, "info": 2}
        if sev_order.get(finding.severity, 2) > sev_order.get(sev_filter, 2):
            continue
        return rule
    return None


def generate_preview(finding: UnifiedFinding, rule: dict, actions: dict) -> str:
    """Generate human-readable preview of the proposed change."""
    action_name = rule.get("action", "")
    action_def = actions.get(action_name, {})
    template = rule.get("template", {})

    if action_name == "append_pitfall":
        domain = template.get("domain", finding.level.upper()).replace(
            "{detected_level}", finding.level.upper()
        )
        title = template.get("title", finding.check_name)
        symptom = template.get("symptom", finding.message)
        cause = template.get("cause", "See validation details")
        fix = template.get("fix", "See validation details")
        return (
            f"## N. [{domain}] {title}\n\n"
            f"**Symptom:** {symptom}\n"
            f"**Cause:** {cause}\n"
            f"**Fix:** {fix}"
        )
    elif action_name == "fix_reference":
        return f"Fix broken reference: {finding.message}"
    elif action_name == "append_rule":
        return f"Add rule for: {finding.check_name} — {finding.message}"
    elif action_name == "add_domain_tag":
        return f"Add domain tag to entry: {finding.message}"
    else:
        return f"[{action_name}] {finding.message}"


def generate_proposals(
    findings: list[UnifiedFinding],
    rules_config: dict,
) -> list[FeedbackProposal]:
    """Generate feedback proposals for failed findings."""
    rules = rules_config.get("rules", [])
    actions = rules_config.get("actions", {})
    proposals: list[FeedbackProposal] = []
    counter = 0

    for finding in findings:
        if finding.passed:
            continue
        rule = match_rule(finding, rules)
        if rule is None:
            continue
        counter += 1
        target = rule.get("target", "memory/common_pitfalls.md")
        # Determine which level's .deepx/ to modify
        target_level = finding.level if rule.get("level") == "any" else rule["level"]

        proposals.append(FeedbackProposal(
            id=f"FB-{counter:03d}",
            finding=finding,
            target_file=target,
            target_level=target_level,
            action=rule.get("action", "append_pitfall"),
            preview=generate_preview(finding, rule, actions),
        ))

    return proposals


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def build_report(
    repo_root: Path,
    findings: list[UnifiedFinding],
    proposals: list[FeedbackProposal],
) -> FeedbackReport:
    """Build the complete feedback report."""
    failed = [f for f in findings if not f.passed]
    by_level: dict[str, int] = {}
    for f in failed:
        by_level[f.level] = by_level.get(f.level, 0) + 1

    return FeedbackReport(
        timestamp=datetime.now().isoformat(),
        repo_root=str(repo_root),
        validation_summary={
            "total_checks": len(findings),
            "passed": sum(1 for f in findings if f.passed),
            "failed": len(failed),
            "by_level": by_level,
            "by_category": {
                "app_code": sum(1 for f in failed if f.category == "app_code"),
                "framework_integrity": sum(
                    1 for f in failed if f.category == "framework_integrity"
                ),
            },
        },
        findings=findings,
        proposed_feedback=proposals,
    )


def print_report_text(report: FeedbackReport) -> None:
    """Print human-readable report to stdout."""
    s = report.validation_summary
    print(f"\n{'=' * 60}")
    print(f"  DEEPX Validation + Feedback Report")
    print(f"  {report.timestamp}")
    print(f"{'=' * 60}\n")
    print(f"  Total checks: {s['total_checks']}")
    print(f"  Passed:       {s['passed']}")
    print(f"  Failed:       {s['failed']}")
    if s["by_level"]:
        print(f"  By level:     {s['by_level']}")
    print()

    # Failed findings
    failed = [f for f in report.findings if not f.passed]
    if failed:
        print("--- Failed Checks ---\n")
        for f in failed:
            icon = {"error": "[ERR]", "warning": "[WRN]", "info": "[INF]"}.get(
                f.severity, "[???]"
            )
            print(f"  {icon} [{f.level}] {f.check_name}: {f.message}")
        print()

    # Proposals
    if report.proposed_feedback:
        print("--- Proposed Feedback ---\n")
        for p in report.proposed_feedback:
            print(f"  {p.id}: {p.action} → {p.target_level}/.deepx/{p.target_file}")
            print(f"         {p.preview.split(chr(10))[0]}")
            print()

    if not failed:
        print("  All checks passed. No feedback proposals generated.\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Collect validation results and propose knowledge-base feedback.",
    )
    parser.add_argument(
        "--app-dirs", nargs="*", default=[],
        help="App directories to validate (relative to repo root)",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Run all validators (framework + discover app dirs)",
    )
    parser.add_argument(
        "--framework-only", action="store_true",
        help="Only run framework validators",
    )
    parser.add_argument(
        "--app-only", action="store_true",
        help="Only run app validators",
    )
    parser.add_argument(
        "--output", "-o", type=str, default=None,
        help="Write JSON report to file",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output JSON to stdout",
    )
    args = parser.parse_args()

    # Determine repo root (dx-runtime/)
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent  # .deepx/scripts/ → .deepx/ → dx-runtime/

    print(f"Repo root: {repo_root}")
    print(f"Collecting validation results...\n")

    # Collect findings
    findings = collect_all_findings(
        repo_root, args.app_dirs,
        framework_only=args.framework_only,
        app_only=args.app_only,
    )

    # Load rules and generate proposals
    rules_config = load_rules(repo_root)
    proposals = generate_proposals(findings, rules_config)

    # Build report
    report = build_report(repo_root, findings, proposals)

    # Output
    if args.json:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
    elif args.output:
        with open(args.output, "w") as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"Report written to {args.output}")
        print_report_text(report)
    else:
        print_report_text(report)

    # Exit code: 0 if no errors, 1 if any errors
    has_errors = any(
        not f.passed and f.severity == "error" for f in findings
    )
    return 1 if has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
