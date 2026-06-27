#!/usr/bin/env python3
"""SQ Enforcer — validates C4 name fidelity, ref blocks, activation pairs, and traceability.

Usage:
    python docs/SQ/common/sq_enforce.py                          # Full report
    python docs/SQ/common/sq_enforce.py --fix                    # Auto-fix what's safe
    python docs/SQ/common/sq_enforce.py --json                   # JSON report
    python docs/SQ/common/sq_enforce.py --group WRL              # Check single group
    python docs/SQ/common/sq_enforce.py --trace                  # Traceability report
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

REPO = Path(__file__).resolve().parents[3]
SQ_DIR = REPO / "docs" / "SQ"
C4_DIR = REPO / "docs" / "C4"
SM_README = REPO / "docs" / "SM" / "README.md"
ENTITIES = REPO / ".nasim" / "rules" / "ENTITIES.md"

# ---------------------------------------------------------------------------
# C4 Authoritative Component Names (extracted from C4 component diagrams)
# ---------------------------------------------------------------------------

C4_COMPONENTS: Dict[str, Dict[str, str]] = {
    # group_name -> {component_name: csr_layer}
    "CLI": {
        "ArgParser": "controller",
        "REPLSession": "controller",
        "Renderer": "controller",
        "SlashCommandHandler": "controller",
    },
    "API": {
        "ServerApp": "controller",
        "ServerRouter": "controller",
        "SSEHandler": "controller",
        "APISchema": "controller",
    },
    "Agent": {
        "AgentOrchestrator": "service",
        "ConversationHistory": "service",
        "ContextCompactor": "service",
        "SafetyCoordinator": "service",
        "PlanSession": "service",
        "AgentEvent": "service",
        "SubagentCoordinator": "service",
        "ErrorBoundary": "service",
        "PersonaManager": "service",
    },
    "Provider": {
        "Provider": "service",
        "LiteLLMProxy": "service",
        "ProviderCapabilities": "service",
        "ModelRouter": "service",
        "FallbackChain": "service",
        "ModelCatalog": "service",
    },
    "Tool": {
        "Tool": "repository",
        "ToolRegistry": "repository",
        "ToolResult": "repository",
        "ReadFileTool": "repository",
        "WriteFileTool": "repository",
        "EditFileTool": "repository",
        "GrepTool": "repository",
        "GlobTool": "repository",
        "FindFileTool": "repository",
        "ShellTool": "repository",
        "DirTool": "repository",
        "WebFetchTool": "repository",
        "WebSearchTool": "repository",
        "GitTool": "repository",
        "LspTool": "repository",
        "SubagentTool": "repository",
        "TodoTool": "repository",
        "MemoryTool": "repository",
        "PlanTool": "repository",
        "RepoMapTool": "repository",
        "SemanticSearchTool": "repository",
        "ReviewTool": "repository",
    },
    "Session": {
        "SessionStore": "repository",
        "SessionVersioning": "repository",
        "SessionSearch": "repository",
        "SessionFork": "repository",
    },
    "Memory": {
        "MemoryStore": "repository",
        "MemoryIndex": "repository",
        "MemoryScope": "repository",
        "EpisodicMemoryAdapter": "repository",
        "SemanticMemoryAdapter": "repository",
        "WorkingMemoryAdapter": "repository",
        "MemoryRetriever": "repository",
        "MemoryIndexer": "repository",
    },
    "Config": {
        "ConfigLoader": "repository",
        "Config": "repository",
    },
    "Git": {
        "GitIntegration": "repository",
        "GitStatus": "repository",
        "GitCommit": "repository",
    },
    "RepoIntelligence": {
        "RepoIntelligenceManager": "repository",
        "ASTIndexAdapter": "repository",
        "SymbolGraph": "repository",
        "RankingService": "repository",
        "EmbeddingAdapter": "repository",
        "SemanticSearchService": "repository",
        "RepoMapBuilder": "repository",
    },
    "MCP": {
        "MCPClientRuntime": "infrastructure",
        "MCPServerRuntime": "infrastructure",
        "MCPToolAdapter": "infrastructure",
        "MCPDiscovery": "infrastructure",
    },
    "Sandbox": {
        "SandboxExecutor": "infrastructure",
        "SandboxPolicy": "infrastructure",
        "SandboxMonitor": "infrastructure",
    },
    "Observability": {
        "StructuredLogger": "infrastructure",
        "MetricsCollector": "infrastructure",
        "TraceCorrelator": "infrastructure",
        "ContextPropagator": "infrastructure",
        "LogRedactor": "infrastructure",
        "DualOutputAdapter": "infrastructure",
        "OTelExporter": "infrastructure",
    },
    "WireLog": {
        "WireLog": "infrastructure",
        "WireAppender": "infrastructure",
        "WireReader": "infrastructure",
        "TurnIndex": "infrastructure",
        "SessionForkManager": "infrastructure",
    },
    "Hooks": {
        "HookManager": "infrastructure",
        "Hook": "infrastructure",
        "HookResult": "infrastructure",
    },
    "Plugins": {
        "PluginLoader": "infrastructure",
        "PluginManifest": "infrastructure",
    },
    "ContextGraph": {
        "ContextGraph": "service",
        "ContextNode": "service",
        "ContextEdge": "service",
        "ContextProcessor": "service",
        "ContextPrioritizer": "service",
        "TruncationProcessor": "service",
        "DistillationProcessor": "service",
        "InjectionProcessor": "service",
        "CompactionProcessor": "service",
        "PipelineOrchestrator": "service",
        "TokenBudgetTracker": "service",
    },
    "EditStrategy": {
        "EditStrategyManager": "service",
        "EditStrategy": "service",
        "SearchReplaceCoder": "service",
        "WholeFileCoder": "service",
        "UnifiedDiffCoder": "service",
        "FencedBlockCoder": "service",
        "FunctionLevelCoder": "service",
        "DiffSandboxCoder": "service",
        "ArchitectCoder": "service",
        "InlinePatchCoder": "service",
        "StrategySelector": "service",
    },
    "Evaluation": {
        "EvaluationEngine": "service",
        "TaskEvaluator": "service",
        "SuccessCheckRunner": "service",
        "LLMReviewer": "service",
        "TestRunner": "service",
        "RetryCoordinator": "service",
        "QualitySignal": "service",
        "RepetitionDetector": "service",
        "TurnBudgetInjector": "service",
    },
    "Router": {
        "ModelRouter": "service",
        "FallbackChain": "service",
    },
    "Safety": {
        "SafetyCoordinator": "service",
    },
}

# Flatten for quick lookup
ALL_C4_COMPONENTS: Dict[str, str] = {}
for group, components in C4_COMPONENTS.items():
    for name, layer in components.items():
        ALL_C4_COMPONENTS[name] = layer

# Known invented/non-existent components to reject
INVENTED_COMPONENTS: Set[str] = {
    "SessionManager",
    "WireLogManager",
    "WireLogStore",
    "ToolOrchestrator",
    "ApiManager",
    "AgentManager",
    "ProviderManager",
    "MemoryManager",
    "ConfigManager",
    "GitManager",
    "SafetyManager",
    "RouterManager",
    "ContextManager",
    "EditStrategyManager",  # exists but check layer
    "EvaluationManager",
}

# CSR layer colors
CSR_COLORS = {
    "controller": "#E3F2FD",
    "service": "#FFF3E0",
    "repository": "#E8F5E9",
    "infrastructure": "#F3E5F5",
}

# SM state hex colors
SM_STATE_COLORS: Dict[str, str] = {}


def load_sm_states() -> Dict[str, str]:
    """Load SM state hex colors from SM/README.md."""
    if not SM_README.exists():
        return {}
    text = SM_README.read_text()
    colors = {}
    for m in re.finditer(r'\|\s*(\w+)\s*\|.*?\|\s*(#[0-9A-Fa-f]{6})\s*\|', text):
        colors[m.group(1)] = m.group(2)
    return colors


# ---------------------------------------------------------------------------
# Validation checks
# ---------------------------------------------------------------------------

def check_c4_name_fidelity(files: list[Path]) -> List[dict]:
    """E-SQ-01: All lifeline names must be C4-authoritative component names."""
    findings = []
    for f in files:
        text = f.read_text()
        for line in text.split('\n'):
            stripped = line.strip()
            # Match participant/actor/database declarations
            m = re.match(
                r'(participant|actor|database)\s+"([^"]+)"\s+as\s+(\w+)',
                stripped
            )
            if not m:
                continue
            display_name = m.group(2)
            alias = m.group(3)

            # Skip known valid names
            if display_name in ("User", "CLI Process", "ServerRouter",
                                "ServerApp", "FileSystem"):
                continue
            if alias in ("user", "iface", "router"):
                continue

            # Check against C4
            if display_name not in ALL_C4_COMPONENTS:
                # Check if it's a known invented name
                if display_name in INVENTED_COMPONENTS:
                    findings.append({
                        "file": str(f),
                        "rule": "E-SQ-01",
                        "severity": "CRITICAL",
                        "detail": f"Invented component '{display_name}' — not in C4. Use C4-authoritative name.",
                    })
                elif not display_name.startswith(("WireLog", "Session", "Memory",
                                                  "Config", "Git", "Tool")):
                    # Allow storage-like names (database declarations)
                    if m.group(1) != "database":
                        findings.append({
                            "file": str(f),
                            "rule": "E-SQ-01",
                            "severity": "HIGH",
                            "detail": f"Component '{display_name}' not found in C4 registry.",
                        })
    return findings


def check_ref_blocks_for_state_writes(files: list[Path]) -> List[dict]:
    """E-SQ-02: State writes must use ref blocks, not self-calls."""
    findings = []
    for f in files:
        text = f.read_text()
        for i, line in enumerate(text.split('\n'), 1):
            stripped = line.strip()
            # Detect self-call state transitions
            if re.match(r'\w+\s*->\s*\w+\s*:\s*TRANSITION\s+State\(', stripped):
                # Check if it's a self-call (same alias on both sides)
                m = re.match(r'(\w+)\s*->\s*(\w+)\s*:', stripped)
                if m and m.group(1) == m.group(2):
                    findings.append({
                        "file": str(f),
                        "rule": "E-SQ-02",
                        "severity": "HIGH",
                        "detail": f"Line {i}: Self-call state write. Use ref block instead.",
                    })
    return findings


def check_activation_pairs(files: list[Path]) -> List[dict]:
    """E-SQ-03: Every activate must have a matching deactivate."""
    findings = []
    for f in files:
        text = f.read_text()
        activations = []
        deactivations = []

        for i, line in enumerate(text.split('\n'), 1):
            stripped = line.strip()
            if stripped.startswith('activate '):
                alias = stripped.split('activate ')[1].strip()
                activations.append((i, alias))
            elif stripped.startswith('deactivate '):
                alias = stripped.split('deactivate ')[1].strip()
                deactivations.append((i, alias))

        # Check for unmatched activations
        active_stack = []
        for line_num, alias in activations:
            active_stack.append((line_num, alias))

        for line_num, alias in deactivations:
            # Find matching activation
            found = False
            for j in range(len(active_stack) - 1, -1, -1):
                if active_stack[j][1] == alias:
                    active_stack.pop(j)
                    found = True
                    break
            if not found:
                findings.append({
                    "file": str(f),
                    "rule": "E-SQ-03",
                    "severity": "MEDIUM",
                    "detail": f"Line {line_num}: deactivate {alias} without matching activate.",
                })

        # Remaining activations without deactivation
        for line_num, alias in active_stack:
            findings.append({
                "file": str(f),
                "rule": "E-SQ-03",
                "severity": "MEDIUM",
                "detail": f"Line {line_num}: activate {alias} has no matching deactivate.",
            })

    return findings


def check_csr_box_colors(files: list[Path]) -> List[dict]:
    """E-SQ-04: CSR box colors must match the group's layer."""
    findings = []
    for f in files:
        text = f.read_text()
        for i, line in enumerate(text.split('\n'), 1):
            stripped = line.strip()
            # Match box declarations with colors
            m = re.match(r'box\s+"([^"]+)"\s+#([0-9A-Fa-f]{6})', stripped)
            if not m:
                continue
            box_name = m.group(1)
            color = "#" + m.group(2)

            # Determine expected color from box name
            expected_color = None
            if "Controller" in box_name or "API Group" in box_name or "Interface" in box_name:
                expected_color = "#E3F2FD"
            elif "Service" in box_name:
                expected_color = "#FFF3E0"
            elif "Repository" in box_name:
                expected_color = "#E8F5E9"
            elif "Infrastructure" in box_name:
                expected_color = "#F3E5F5"

            if expected_color and color != expected_color:
                findings.append({
                    "file": str(f),
                    "rule": "E-SQ-04",
                    "severity": "HIGH",
                    "detail": f"Line {i}: Box '{box_name}' has color {color}, expected {expected_color}.",
                })

    return findings


def check_entry_chain(files: list[Path]) -> List[dict]:
    """E-SQ-05: Full entry chain present (User -> Interface -> API -> ...)."""
    findings = []
    for f in files:
        text = f.read_text()
        has_actor = bool(re.search(r'\bactor\b', text, re.IGNORECASE))
        has_interface = "CLI Process" in text or "WebApp" in text
        has_router = "ServerRouter" in text

        if not has_actor:
            findings.append({
                "file": str(f), "rule": "E-SQ-05", "severity": "CRITICAL",
                "detail": "No actor declaration.",
            })
        if not has_interface:
            findings.append({
                "file": str(f), "rule": "E-SQ-05", "severity": "HIGH",
                "detail": "No Interface lifeline (CLI Process / WebApp).",
            })
        if not has_router:
            findings.append({
                "file": str(f), "rule": "E-SQ-05", "severity": "HIGH",
                "detail": "No ServerRouter lifeline.",
            })
    return findings


def check_header_fields(files: list[Path]) -> List[dict]:
    """E-SQ-06: Required header fields present."""
    findings = []
    required = ["Title:", "Boundary:", "Purpose:", "Version:", "Source:"]
    for f in files:
        text = f.read_text()
        for field in required:
            if field not in text:
                findings.append({
                    "file": str(f), "rule": "E-SQ-06", "severity": "MEDIUM",
                    "detail": f"Missing header field '{field}'.",
                })
    return findings


def check_no_notes(files: list[Path]) -> List[dict]:
    """E-SQ-07: ZERO note/hnote blocks (AD-02)."""
    findings = []
    for f in files:
        text = f.read_text()
        for i, line in enumerate(text.split('\n'), 1):
            stripped = line.strip()
            if re.match(r'(note|hnote)\s+(over|left|right)', stripped):
                findings.append({
                    "file": str(f), "rule": "E-SQ-07", "severity": "CRITICAL",
                    "detail": f"Line {i}: note/hnote block found (AD-02 violation).",
                })
    return findings


def check_rod_format(files: list[Path]) -> List[dict]:
    """E-SQ-08: ROD method names on messages."""
    findings = []
    for f in files:
        text = f.read_text()
        for i, line in enumerate(text.split('\n'), 1):
            stripped = line.strip()
            if '->' not in stripped or ':' not in stripped:
                continue
            if '<--' in stripped or '-->' in stripped:
                continue
            if stripped.startswith(('@', "'", 'participant', 'actor', 'box',
                                   'activate', 'deactivate', 'end', '}',
                                   'title', '== ', 'ref')):
                continue
            label = stripped.split(':', 1)[1].strip()
            if not label or label.startswith("'"):
                continue
            # Accept ROD format
            if not re.match(r'^[A-Z]{2,5}-\d{2}', label) and \
               not re.match(r'^[a-z]{2,5}\d{2}', label) and \
               not re.match(r'^[A-Z]{2,}', label) and \
               not re.match(r'^(POST|GET|PUT|PATCH|DELETE)', label) and \
               not re.match(r'^\d{3}', label) and \
               label != "TRANSITION State(...)":
                findings.append({
                    "file": str(f), "rule": "E-SQ-08", "severity": "HIGH",
                    "detail": f"Line {i}: Non-ROD message '{label[:50]}'.",
                })
    return findings


# ---------------------------------------------------------------------------
# Traceability report
# ---------------------------------------------------------------------------

def generate_traceability(files: list[Path]) -> dict:
    """Generate lifeline → C4 component mapping."""
    report = {}
    for f in files:
        group = f.parent.name
        text = f.read_text()
        lifelines = []
        for line in text.split('\n'):
            m = re.match(
                r'\s*(participant|actor|database)\s+"([^"]+)"\s+as\s+(\w+)',
                line.strip()
            )
            if m:
                lifelines.append({
                    "display": m.group(2),
                    "alias": m.group(3),
                    "type": m.group(1),
                    "c4_match": m.group(2) in ALL_C4_COMPONENTS,
                    "c4_layer": ALL_C4_COMPONENTS.get(m.group(2), "unknown"),
                })
        report[str(f)] = {
            "group": group,
            "lifelines": lifelines,
        }
    return report


# ---------------------------------------------------------------------------
# Auto-fix: box color correction
# ---------------------------------------------------------------------------

def fix_box_colors(content: str) -> Tuple[str, List[str]]:
    """Fix CSR box colors to match layer labels."""
    changes = []
    lines = content.split('\n')
    result = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        m = re.match(r'(box\s+"[^"]+"\s+)#([0-9A-Fa-f]{6})', stripped)
        if m:
            prefix = m.group(1)
            current_color = "#" + m.group(2)
            box_name = re.match(r'box\s+"([^"]+)"', stripped).group(1)

            expected = None
            if "Controller" in box_name or "API Group" in box_name or "Interface" in box_name:
                expected = "#E3F2FD"
            elif "Service" in box_name:
                expected = "#FFF3E0"
            elif "Repository" in box_name:
                expected = "#E8F5E9"
            elif "Infrastructure" in box_name:
                expected = "#F3E5F5"

            if expected and current_color != expected:
                line = line.replace(current_color, expected)
                changes.append(f"Line {i+1}: Fixed box color {current_color} → {expected}")

        result.append(line)

    return '\n'.join(result), changes


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="SQ Enforcer")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fix", action="store_true", help="Auto-fix safe violations")
    parser.add_argument("--group", type=str, help="Check single group (e.g., WRL)")
    parser.add_argument("--trace", action="store_true", help="Generate traceability report")
    args = parser.parse_args()

    # Load SM states
    global SM_STATE_COLORS
    SM_STATE_COLORS = load_sm_states()

    # Find SQ files
    if args.group:
        sq_dir = SQ_DIR / args.group
        files = sorted(sq_dir.rglob("*.puml")) if sq_dir.exists() else []
    else:
        files = sorted(SQ_DIR.rglob("*.puml"))
    files = [f for f in files if "common" not in str(f) and "sq_template" not in f.name]

    if not files:
        print("No SQ files found.")
        return 1

    # Run all checks
    all_findings = []
    checks = [
        ("E-SQ-01", "C4 Name Fidelity", check_c4_name_fidelity),
        ("E-SQ-02", "Ref Blocks for State Writes", check_ref_blocks_for_state_writes),
        ("E-SQ-03", "Activation Pairs", check_activation_pairs),
        ("E-SQ-04", "CSR Box Colors", check_csr_box_colors),
        ("E-SQ-05", "Entry Chain", check_entry_chain),
        ("E-SQ-06", "Header Fields", check_header_fields),
        ("E-SQ-07", "No Notes", check_no_notes),
        ("E-SQ-08", "ROD Format", check_rod_format),
    ]

    results = []
    for rule_id, name, check_fn in checks:
        findings = check_fn(files)
        results.append({"rule": rule_id, "name": name, "findings": findings})
        all_findings.extend(findings)

    # Auto-fix
    if args.fix:
        fixed_count = 0
        for f in files:
            content = f.read_text()
            new_content, changes = fix_box_colors(content)
            if new_content != content:
                f.write_text(new_content)
                fixed_count += 1
                print(f"Fixed: {f}")
                for c in changes:
                    print(f"  {c}")
        print(f"\nAuto-fixed {fixed_count} files.")

    # Traceability
    if args.trace:
        trace = generate_traceability(files)
        print("\n=== TRACEABILITY REPORT ===\n")
        for filepath, data in trace.items():
            print(f"{filepath} ({data['group']})")
            for ll in data["lifelines"]:
                status = "OK" if ll["c4_match"] else "MISSING"
                print(f"  [{status}] {ll['display']} ({ll['alias']}) → C4: {ll['c4_layer']}")
            print()

    # Report
    if args.json:
        report = {
            "files_checked": len(files),
            "total_violations": len(all_findings),
            "critical": sum(1 for f in all_findings if f.get("severity") == "CRITICAL"),
            "high": sum(1 for f in all_findings if f.get("severity") == "HIGH"),
            "medium": sum(1 for f in all_findings if f.get("severity") == "MEDIUM"),
            "results": results,
        }
        print(json.dumps(report, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"SQ ENFORCER — {len(files)} files checked")
        print(f"{'='*60}\n")

        for r in results:
            status = "PASS" if not r["findings"] else f"FAIL ({len(r['findings'])})"
            print(f"  {r['rule']:12s} {r['name']:30s} {status}")
            for f in r["findings"][:5]:
                sev = f.get("severity", "HIGH")
                print(f"              [{sev:8s}] {f['detail'][:80]}")
            if len(r["findings"]) > 5:
                print(f"              ... and {len(r['findings'])-5} more")

        critical = sum(1 for f in all_findings if f.get("severity") == "CRITICAL")
        high = sum(1 for f in all_findings if f.get("severity") == "HIGH")
        medium = sum(1 for f in all_findings if f.get("severity") == "MEDIUM")

        print(f"\n{'─'*60}")
        print(f"TOTAL: {len(all_findings)} violations ({critical} critical, {high} high, {medium} medium)")
        passed = critical == 0 and high == 0
        print(f"RESULT: {'ALL CHECKS PASS' if passed else 'VIOLATIONS FOUND'}")
        print(f"{'='*60}\n")

    return 0 if not any(f.get("severity") == "CRITICAL" for f in all_findings) else 1


if __name__ == "__main__":
    sys.exit(main())
