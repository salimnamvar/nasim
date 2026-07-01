"""
Restructure all SQ diagrams to 7-layer CSR chain.

Removes GroupAPI/GroupController lifeline, inserts Interface (CLI Process)
and Infrastructure layers. Reroutes messages through correct lifelines.
"""

from pathlib import Path
import re

SQ_DIR = Path("/home/salim/prj/salim/nasim/code/nasim/docs/SQ")

INFRA_LABEL = {
    "session": "FileSystem",
    "tool": "FileSystem",
    "agent": "FileSystem",
    "api": "FileSystem",
    "cli": "FileSystem",
    "editstrategy": "FileSystem",
    "evaluation": "TestSuite",
    "config": "FileSystem",
    "contextgraph": "TokenBudget",
    "git": "Git Repository",
    "hooks": "HookRuntime",
    "mcp": "MCPServer",
    "memory": "FileSystem",
    "observability": "MetricsBackend",
    "plugins": "PluginRuntime",
    "provider": "LLMBackend",
    "repointelligence": "FileSystem",
    "repointer": "FileSystem",
    "router": "ModelBackend",
    "safety": "PolicyEngine",
    "sandbox": "HostShell",
    "wirelog": "FileSystem",
}


def read_box(lines, start):
    """Read a box block starting at `start`. Return (content_lines, end_index)."""
    content = [lines[start]]
    i = start + 1
    depth = 1
    while i < len(lines) and depth > 0:
        s = lines[i].strip()
        content.append(lines[i])
        if s.startswith("box "):
            depth += 1
        elif s in ("end box", "endbox"):
            depth -= 1
        i += 1
    return content, i


def fix_file(path: Path) -> bool:
    dname = path.parent.name.lower()
    raw = path.read_text()
    orig = raw

    # Idempotency: skip if already restructured
    if '"CLI Process" as iface' in raw:
        return False

    cap = dname.capitalize()
    if dname in ("repointer", "repointelligence"):
        cap = "RepoIntelligence"
    infra_name = INFRA_LABEL.get(dname, "ExternalSystem")
    chain = f"User -> CLI Process -> ServerRouter -> {cap}Manager -> {cap}Store -> {cap}Directory -> {infra_name}"
    raw = re.sub(r"' CSR Chain:.*$", f"' CSR Chain: {chain}", raw, count=1, flags=re.MULTILINE)

    lines = raw.split("\n")
    out = []
    i = 0
    n = len(lines)
    added_iface = False
    added_infra = False
    in_msgs = False
    first_arrow = False

    while i < n:
        line = lines[i]
        s = line.strip()

        if s.startswith("== ") and " ==" in s:
            in_msgs = True

        # === Handle box blocks ===
        if s.startswith("box "):
            block, end = read_box(lines, i)
            block_text = "\n".join(line for line in block)
            # Check if this box contains a GroupAPI or GroupController participant
            has_api = re.search(r'participant\s+"[^"]*API"\s+as\s+api', block_text)
            has_ctrl = re.search(r'participant\s+"[^"]*Controller"\s+as\s+ctrl', block_text)
            if has_api or has_ctrl:
                i = end
                continue
            # Otherwise output the box as-is
            out.extend(block)
            i = end
            continue

        # Remove standalone participant lines for api/ctrl
        if re.match(r'participant\s+"[^"]*API"\s+as\s+api\s*$', s) or re.match(
            r'participant\s+"[^"]*Controller"\s+as\s+ctrl\s*$', s
        ):
            i += 1
            continue

        # Insert Interface box after actor
        if re.match(r'actor\s+"', s) and not added_iface:
            out.append(line)
            out.append("")
            out.append('box "Interface Layer" #INTERFACE_COLOR')
            out.append('  participant "CLI Process" as iface')
            out.append("end box")
            added_iface = True
            i += 1
            continue

        # Insert Infrastructure box after last database/entity
        if (s.startswith("database ") or s.startswith("entity ") or s.startswith("collections ")) and not added_infra:
            out.append(line)
            # Check what comes next
            k = i + 1
            while k < n and lines[k].strip() == "":
                k += 1
            if k < n and (lines[k].strip().startswith("== ") or lines[k].strip().startswith("box ")):
                ivar = infra_name.replace(" ", "")
                out.append("")
                out.append(f'box "Infrastructure Layer" #INFRASTRUCTURE_COLOR')
                out.append(f'  participant "{infra_name}" as {ivar}')
                out.append("end box")
                added_infra = True
            i += 1
            continue

        # === MESSAGE SECTION ===
        if in_msgs:
            # Remove activate/deactivate api/ctrl
            if re.match(r"(de)?activate\s+(api|ctrl)\s*$", s):
                i += 1
                continue

            # Transform lifeline references
            line = re.sub(r"\brouter\s*->\s*api\b", "router -> mgr", line)
            line = re.sub(r"\bctrl\s*(->|-->)\s*", r"router \1 ", line)
            line = re.sub(r"(->|-->)\s*ctrl\b", r"\1 router", line)
            line = re.sub(r"\bapi\s*(-->|<--)\s*router\b", r"router \1 iface", line)
            line = re.sub(r"\bmgr\s*(-->|<--)\s*api\b", r"mgr \1 router", line)
            line = re.sub(r"\bstore\s*(-->|<--)\s*api\b", r"store \1 router", line)
            line = re.sub(r"\bapi\s*(-->|<--)\s*mgr\b", r"router \1 mgr", line)
            # Skip original api->mgr forward lines (now redundant)
            if re.match(r"^\s*api\s*->\s*mgr\b", line):
                i += 1
                continue
            # Catch-all: remaining 'api' or 'ctrl' → 'router'
            line = re.sub(r"\bapi\b", "router", line)
            line = re.sub(r"\bctrl\b", "router", line)

            # Route router → user through iface
            m = re.match(r"^(\s*)router\s*(-->|<--)\s*user\s*:\s*(.+)$", line)
            if m:
                indent = m.group(1)
                arrow = m.group(2)
                msg = m.group(3)
                out.append(f"{indent}router {arrow} iface : {msg}")
                out.append(f"{indent}iface {arrow} user : {msg}")
                i += 1
                continue

            # First user → router → user → iface → router
            if not first_arrow:
                m = re.match(r"^(\s*)user\s*->\s*router\s*:\s*(.+)$", line)
                if m:
                    indent = m.group(1)
                    msg = m.group(2)
                    out.append(f"{indent}user -> iface : {msg}")
                    out.append(f"{indent}activate iface")
                    out.append(f"{indent}iface -> router : {msg}")
                    first_arrow = True
                    i += 1
                    continue

            # Add deactivate iface after deactivate router
            if re.match(r"^\s*deactivate\s+router\s*$", s):
                out.append(line)
                peek = lines[i + 1].strip() if i + 1 < n else ""
                if not re.match(r"^\s*deactivate\s+iface\s*$", peek):
                    indent = line[: len(line) - len(s.lstrip())]
                    out.append(f"{indent}deactivate iface")
                i += 1
                continue

        out.append(line)
        i += 1

    result = "\n".join(out)
    if result != orig:
        path.write_text(result)
        return True
    return False


def main():
    total = changed = errors = 0
    for p in sorted(SQ_DIR.rglob("*.puml")):
        if "sq_styles" in p.name or "common" in str(p.parent):
            continue
        total += 1
        try:
            if fix_file(p):
                changed += 1
        except Exception as e:
            print(f"  ✗ {p.relative_to(SQ_DIR)}: {e}")
            errors += 1
    print(f"\nTotal: {total}, Changed: {changed}, Errors: {errors}")


if __name__ == "__main__":
    main()
