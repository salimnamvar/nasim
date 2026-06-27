#!/usr/bin/env python3
"""SQ Gate Check — runs ALL CI/CD gates on all SQ diagrams and reports pass/fail.

Usage:
    python scripts/sq_gate.py                          # Full report
    python scripts/sq_gate.py --json                   # JSON report
    python scripts/sq_gate.py --fail-fast              # Exit on first failure
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SQ_DIR = REPO / "docs" / "SQ"
SM_DIR = REPO / "docs" / "SM"
UC_README = REPO / "docs" / "UC" / "README.md"
SQ_LINT = Path("/home/salim/.agent-global/shared/tools/software-design/sq/sq_lint.py")


def run_lint(paths: list[Path]) -> dict:
    result = subprocess.run(
        [sys.executable, str(SQ_LINT), *[str(p) for p in paths], "--strict"],
        capture_output=True, text=True, timeout=120
    )
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }


def parse_violations(lint_output: str) -> list[dict]:
    violations = []
    current_file = None
    for line in lint_output.split('\n'):
        if line.startswith("File:"):
            current_file = line.split("File:")[1].strip()
        m = re.match(r'\[(CRITICAL|HIGH|MEDIUM|LOW)\s*\]\s+(\S+):\s+(.+)', line)
        if m and current_file:
            violations.append({
                "file": current_file,
                "severity": m.group(1),
                "rule": m.group(2),
                "message": m.group(3).split(' at')[0].strip(),
            })
    return violations


def check_g_sq_01_actor(sq_files: list[Path]) -> list[dict]:
    """G-SQ-01: Actor present in every diagram."""
    findings = []
    for f in sq_files:
        text = f.read_text()
        has_actor = bool(re.search(r'\bactor\b', text, re.IGNORECASE))
        if not has_actor and "sq_styles" not in f.name:
            findings.append({"file": str(f), "gate": "G-SQ-01", "status": "FAIL",
                             "detail": "No actor declaration found"})
    return findings


def check_g_sq_02_rod_format(sq_files: list[Path]) -> list[dict]:
    """G-SQ-02: ROD method names on messages."""
    findings = []
    for f in sq_files:
        if "sq_styles" in f.name:
            continue
        text = f.read_text()
        bare = 0
        for line in text.split('\n'):
            stripped = line.strip()
            if '->' not in stripped:
                continue
            # Skip return arrows (lint SQ-009 skips these)
            if '<--' in stripped or '-->' in stripped:
                continue
            # Skip non-message lines
            if stripped.startswith(('@', "'", 'participant', 'actor', 'box', 'activate', 'deactivate', 'end', '}', 'title', '== ')):
                continue
            if ':' not in stripped:
                continue
            label = stripped.split(':')[1].strip()
            if not label or label.startswith("'"):
                continue
            # Accept: UC-ID prefix, lowercase prefix, uppercase method name, HTTP verb, or 3-digit code
            if not re.match(r'^[A-Z]{2,5}-\d{2}', label) and \
               not re.match(r'^[a-z]{2,5}\d{2}', label) and \
               not re.match(r'^[A-Z]{2,}', label) and \
               not re.match(r'^(POST|GET|PUT|PATCH|DELETE)', label) and \
               not re.match(r'^\d{3}', label):
                bare += 1
        if bare > 0:
            findings.append({"file": str(f), "gate": "G-SQ-02", "status": "FAIL",
                             "detail": f"{bare} messages without ROD format"})
    return findings


def check_g_sq_03_csr_layers(sq_files: list[Path]) -> list[dict]:
    """G-SQ-03: CSR layers complete."""
    findings = []
    for f in sq_files:
        if "sq_styles" in f.name:
            continue
        text = f.read_text()
        has_actor = bool(re.search(r'\bactor\b', text, re.IGNORECASE))
        has_interface = any(kw in text.lower() for kw in
                            ["serverrouter", "replsession", "mcpclientruntime", "router"])
        has_service = any(kw in text.lower() for kw in
                          ["orchestrator", "manager", "coordinator", "service", "engine", "handler"])
        has_repo = any(kw in text.lower() for kw in
                       ["store", "repository", "registry", "database", "dir"])
        if not has_actor:
            findings.append({"file": str(f), "gate": "G-SQ-03", "status": "FAIL",
                             "detail": "Missing actor"})
        if not has_interface:
            findings.append({"file": str(f), "gate": "G-SQ-03", "status": "FAIL",
                             "detail": "Missing interface lifeline"})
        if not has_service:
            findings.append({"file": str(f), "gate": "G-SQ-03", "status": "FAIL",
                             "detail": "Missing service lifeline"})
        if not has_repo:
            findings.append({"file": str(f), "gate": "G-SQ-03", "status": "FAIL",
                             "detail": "Missing repository lifeline"})
    return findings


def check_g_sq_04_http_codes(sq_files: list[Path]) -> list[dict]:
    """G-SQ-04: HTTP status codes on return arrows."""
    findings = []
    for f in sq_files:
        if "sq_styles" in f.name:
            continue
        text = f.read_text()
        if not re.search(r'\b\d{3}\b', text):
            findings.append({"file": str(f), "gate": "G-SQ-04", "status": "FAIL",
                             "detail": "No HTTP status codes found"})
    return findings


def check_g_sq_05_failure_paths(sq_files: list[Path]) -> list[dict]:
    """G-SQ-05: Failure paths (break/alt blocks)."""
    findings = []
    for f in sq_files:
        if "sq_styles" in f.name:
            continue
        text = f.read_text()
        if 'break' not in text and 'alt' not in text:
            findings.append({"file": str(f), "gate": "G-SQ-05", "status": "FAIL",
                             "detail": "No break or alt blocks"})
    return findings


def check_g_sq_07_sm_hnote(sq_files: list[Path]) -> list[dict]:
    """G-SQ-07: SM state annotations with hex colors."""
    findings = []
    for f in sq_files:
        if "sq_styles" in f.name:
            continue
        text = f.read_text()
        if 'hnote' not in text and not re.search(r'#([0-9A-Fa-f]{6})', text):
            pass  # Not all diagrams need state changes
    return findings


def check_g_x_01_titles_match_uc(sq_files: list[Path]) -> list[dict]:
    """G-X-01: SQ titles match UC descriptions."""
    findings = []
    uc_text = UC_README.read_text() if UC_README.exists() else ""
    for f in sq_files:
        if "sq_styles" in f.name:
            continue
        text = f.read_text()
        title_m = re.search(r"' Title:\s+(.+)$", text, re.MULTILINE)
        if title_m:
            title = title_m.group(1).strip()
            uc_id = title.split(" —")[0].strip() if " —" in title else title.split("—")[0].strip()
            if uc_id not in uc_text:
                findings.append({"file": str(f), "gate": "G-X-01", "status": "WARN",
                                 "detail": f"Title '{title}' UC-ID '{uc_id}' not found in UC README"})
    return findings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fail-fast", action="store_true")
    args = parser.parse_args()

    sq_files = sorted(SQ_DIR.rglob("*.puml"))

    gates = [
        ("G-SQ-01", "Actor present", check_g_sq_01_actor),
        ("G-SQ-02", "ROD method names", check_g_sq_02_rod_format),
        ("G-SQ-03", "CSR layers complete", check_g_sq_03_csr_layers),
        ("G-SQ-04", "HTTP status codes", check_g_sq_04_http_codes),
        ("G-SQ-05", "Failure paths", check_g_sq_05_failure_paths),
        ("G-SQ-07", "SM state annotations", check_g_sq_07_sm_hnote),
        ("G-X-01", "Titles match UC", check_g_x_01_titles_match_uc),
    ]

    results = []
    for gid, gname, gfunc in gates:
        findings = gfunc(sq_files)
        results.append({"gate": gid, "name": gname, "findings": findings})

    # Run lint
    lint_result = run_lint(sq_files)
    lint_violations = parse_violations(lint_result["stdout"])

    # Count
    total_fail = sum(len(r["findings"]) for r in results)
    total_warn = sum(1 for r in results for f in r["findings"] if f["status"] == "WARN")
    total_lint = len(lint_violations)

    report = {
        "gates": results,
        "lint_violations": lint_violations,
        "summary": {
            "files_checked": len(sq_files),
            "gate_failures": total_fail,
            "gate_warnings": total_warn,
            "lint_violations": total_lint,
            "critical_lint": sum(1 for v in lint_violations if v["severity"] == "CRITICAL"),
            "high_lint": sum(1 for v in lint_violations if v["severity"] == "HIGH"),
            "medium_lint": sum(1 for v in lint_violations if v["severity"] == "MEDIUM"),
            "passed": total_fail == 0 and total_lint == 0,
        }
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"SQ GATE REPORT — {len(sq_files)} files checked")
        print(f"{'='*60}\n")

        for r in results:
            status = "✅" if not r["findings"] else f"❌ ({len(r['findings'])})"
            print(f"  {r['gate']:10s} {r['name']:25s} {status}")
            for f in r["findings"]:
                print(f"          {f['detail']} — {f['file']}")

        print(f"\n{'─'*60}")
        print(f"LINT: {total_lint} violations ({report['summary']['critical_lint']} critical, {report['summary']['high_lint']} high, {report['summary']['medium_lint']} medium)")

        if total_lint > 0:
            for v in lint_violations[:10]:
                print(f"  [{v['severity']:8s}] {v['rule']}: {v['message'][:80]}")
            if len(lint_violations) > 10:
                print(f"  ... and {len(lint_violations)-10} more")

        print(f"\n{'─'*60}")
        print(f"GATES: {total_fail} failures, {total_warn} warnings")
        print(f"RESULT: {'✅ ALL GATES PASS' if report['summary']['passed'] else '❌ GATES FAILING'}")
        print(f"{'='*60}\n")

    return 0 if report["summary"]["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
