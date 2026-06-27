#!/usr/bin/env python3
"""
SQ Diagram Remediator — Fixes common violations across all SQ diagrams.

Fixes:
1. Duplicate lifeline declarations (keeps only first occurrence of each alias)
2. hnote over blocks → inline <back:#HEX>STATE</back> syntax
3. Box color variables → actual hex colors
4. Duplicate return arrows
5. Missing activation/deactivation pairs
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# SM state hex color mapping from docs/SM/README.md
SM_STATE_COLORS = {
    # Agent Process FSM
    "IDLE": "#ECEFF1",
    "LISTENING": "#E8EAF6",
    "THINKING": "#D7CCC8",
    "TOOL_EXEC": "#B2DFDB",
    "RESPONDING": "#D1C4E9",
    "ERROR": "#FFEBEE",
    "COMPACTING": "#E0F2F1",
    "AWAITING_APPROVAL": "#FFF9C4",
    "PLANNING": "#FFCCBC",
    "HOOK_RUNNING": "#FFFDE7",
    "ROUTING": "#EDE7F6",
    "SERVING": "#E0F7FA",
    "EVALUATING": "#F9FBE7",
    "REVIEWING": "#FFF8E1",
    "RETRYING": "#FBE9E7",
    "STAGING": "#F1F8E9",
    "AWAITING_DIFF_APPROVAL": "#FCE4EC",
    "RUNNING": "#43A047",
    # Session
    "CREATED": "#BBDEFB",
    "ACTIVE": "#43A047",
    "SAVED": "#1565C0",
    "RESTORED": "#1E88E5",
    "BRANCHED": "#7B1FA2",
    "CLOSED": "#757575",
    # Plan
    "EMPTY": "#F5F5F5",
    "BUILDING": "#FFE0B2",
    "QUEUED": "#E3F2FD",
    "APPROVED": "#388E3C",
    "EXECUTING": "#A5D6A7",
    "COMPLETED": "#1B5E20",
    "REJECTED": "#B71C1C",
    # Plugin
    "DISCOVERED": "#E0E0E0",
    "LOADING": "#FFCC80",
    "LOADED": "#90CAF9",
    "ENABLED": "#4CAF50",
    "DISABLED": "#CE93D8",
    # Subagent
    "SPAWNING": "#FFAB91",
    # Persona
    "UNLOADED": "#9E9E9E",
    "SWITCHING": "#FF9800",
    # MCP
    "DISCONNECTED": "#B0BEC5",
    "CONNECTING": "#FFCA28",
    "CONNECTED": "#00BCD4",
    "DISCOVERING": "#A1887F",
    "STARTING": "#FFA726",
    # Safety
    "PERMISSIVE": "#9CCC65",
    "ASK": "#FDD835",
    "RESTRICTIVE": "#E53935",
    # Router
    "SELECTING": "#3F51B5",
    "FALLBACK": "#EF6C00",
    "CLASSIFYING": "#5C6BC0",
    # Repo Intelligence
    "INDEXING": "#4FC3F7",
    "INDEXED": "#7CB342",
    "BUILDING_GRAPH": "#9C27B0",
    "EMBEDDING": "#E6EE9C",
    # Provider
    "REGISTERING": "#29B6F6",
    "SELECTING_PROVIDER": "#FBC02D",
    # Evaluation
    "CHECKING": "#C5CAE9",
    "TESTING": "#D4E157",
    "RETRYING_EVAL": "#C62828",
    "SCORING": "#FF8A65",
    "REVIEWING_EVAL": "#AB47BC",
    # Sandbox
    "EXECUTING": "#2196F3",
    "MONITORING": "#64B5F6",
    "RESOURCE_EXCEEDED": "#FF5722",
    # EditStrategy
    "STAGING_DIFF": "#FFE082",
    # ContextGraph
    "COMPACTING_CTX": "#E0F2F1",
    # Hooks
    "HOOK_DISPATCHING": "#FFFDE7",
}


def fix_duplicate_lifelines(content: str) -> str:
    """Remove duplicate participant/actor declarations, keeping only the first."""
    lines = content.split('\n')
    seen_aliases = set()
    result = []
    in_box = False
    box_depth = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Track box nesting
        if stripped.startswith('box '):
            in_box = True
            box_depth += 1
            result.append(line)
            i += 1
            continue
        elif stripped == 'end box':
            box_depth -= 1
            if box_depth <= 0:
                in_box = False
                box_depth = 0
            result.append(line)
            i += 1
            continue
        
        # Check for participant/actor declarations
        match = re.match(r'\s*(participant|actor)\s+"([^"]+)"\s+as\s+(\w+)', stripped)
        if match:
            alias = match.group(3)
            if alias in seen_aliases:
                # Skip duplicate declaration and its surrounding box if empty
                # Also skip the box start/end that wraps this duplicate
                i += 1
                continue
            seen_aliases.add(alias)
            result.append(line)
            i += 1
            continue
        
        # Check for database declarations
        match = re.match(r'\s*database\s+"([^"]+)"\s+as\s+(\w+)', stripped)
        if match:
            alias = match.group(2)
            if alias in seen_aliases:
                i += 1
                continue
            seen_aliases.add(alias)
            result.append(line)
            i += 1
            continue
        
        result.append(line)
        i += 1
    
    return '\n'.join(result)


def fix_hnote_to_inline(content: str) -> str:
    """Replace hnote over blocks with inline state color syntax."""
    # Pattern: hnote over alias : STATE (#HEXCODE)
    # or: hnote over alias : STATE(#HEXCODE) -> STATE2(#HEXCODE2)
    # or: ... hnote over alias : STATE (#HEXCODE) ...
    
    def replace_hnote(match):
        full_match = match.group(0)
        alias = match.group(1)
        state_text = match.group(2).strip()
        
        # Parse state transitions like "STATE (#HEX) -> STATE2 (#HEX2)"
        # or "STATE (#HEX)"
        parts = re.split(r'\s*->\s*', state_text)
        
        result_parts = []
        for part in parts:
            part = part.strip()
            # Match STATE (#HEXCODE) pattern
            state_match = re.match(r'(\w+)\s*\(?(#[0-9A-Fa-f]{6})\)?', part)
            if state_match:
                state_name = state_match.group(1)
                hex_code = state_match.group(2)
                result_parts.append(f'<back:{hex_code}>{state_name}</back>')
            else:
                # Try to find state name and look up color
                state_name = part.strip()
                if state_name in SM_STATE_COLORS:
                    hex_code = SM_STATE_COLORS[state_name]
                    result_parts.append(f'<back:{hex_code}>{state_name}</back>')
                else:
                    result_parts.append(part)
        
        if len(result_parts) > 1:
            transition = ' → '.join(result_parts)
        else:
            transition = result_parts[0] if result_parts else state_text
        
        # Return as a self-call with ROD-compliant format
        # Use TRANSITION method with state_change resource
        return f'    {alias} -> {alias} : TRANSITION State({transition})'
    
    # Match various hnote patterns
    content = re.sub(
        r'(?:\.\.\.\s*)?hnote\s+over\s+(\w+)\s*:\s*(.+?)(?:\s*\.\.\.)?$',
        replace_hnote,
        content,
        flags=re.MULTILINE
    )
    
    return content


def fix_box_colors(content: str) -> str:
    """Replace color variable references with actual hex colors."""
    content = content.replace('#INTERFACE_COLOR', '#E3F2FD')
    content = content.replace('#INFRASTRUCTURE_COLOR', '#ECEFF1')
    content = content.replace('#CONTROLLER_COLOR', '#E3F2FD')
    content = content.replace('#SERVICE_COLOR', '#FFF3E0')
    content = content.replace('#REPOSITORY_COLOR', '#E8F5E9')
    return content


def fix_state_change_format(content: str) -> str:
    """Fix state_change format to ROD-compliant TRANSITION State()."""
    # Replace state_change(...) with TRANSITION State(...)
    content = re.sub(
        r':\s*state_change\(',
        ': TRANSITION State(',
        content
    )
    return content


def fix_duplicate_return_arrows(content: str) -> str:
    """Remove duplicate consecutive return arrows."""
    lines = content.split('\n')
    result = []
    prev_line = None
    
    for line in lines:
        stripped = line.strip()
        # Check if this is a return arrow
        if '-->' in stripped and prev_line and prev_line.strip() == stripped:
            # Skip duplicate return arrow
            continue
        result.append(line)
        prev_line = line
    
    return '\n'.join(result)


def fix_empty_boxes(content: str) -> str:
    """Remove empty box blocks (box start immediately followed by end box)."""
    lines = content.split('\n')
    result = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        if stripped.startswith('box '):
            # Look ahead to see if this box is empty (end box follows immediately)
            j = i + 1
            while j < len(lines) and lines[j].strip() == '':
                j += 1
            
            if j < len(lines) and lines[j].strip() == 'end box':
                # Skip empty box
                i = j + 1
                continue
        
        result.append(line)
        i += 1
    
    return '\n'.join(result)


def process_file(filepath: Path, dry_run: bool = False) -> Tuple[bool, List[str]]:
    """Process a single SQ diagram file. Returns (changed, changes)."""
    original = filepath.read_text()
    content = original
    changes = []
    
    # Fix 1: Box colors
    new_content = fix_box_colors(content)
    if new_content != content:
        changes.append("Fixed box color variables")
        content = new_content
    
    # Fix 1.5: State change format to ROD-compliant
    new_content = fix_state_change_format(content)
    if new_content != content:
        changes.append("Fixed state change format to ROD-compliant")
        content = new_content
    
    # Fix 2: Duplicate lifelines
    new_content = fix_duplicate_lifelines(content)
    if new_content != content:
        changes.append("Removed duplicate lifeline declarations")
        content = new_content
    
    # Fix 3: hnote to inline state colors
    new_content = fix_hnote_to_inline(content)
    if new_content != content:
        changes.append("Converted hnote to inline state colors")
        content = new_content
    
    # Fix 4: Duplicate return arrows
    new_content = fix_duplicate_return_arrows(content)
    if new_content != content:
        changes.append("Removed duplicate return arrows")
        content = new_content
    
    # Fix 5: Empty boxes
    new_content = fix_empty_boxes(content)
    if new_content != content:
        changes.append("Removed empty box blocks")
        content = new_content
    
    if content != original:
        if not dry_run:
            filepath.write_text(content)
        return True, changes
    
    return False, []


def main():
    dry_run = '--dry-run' in sys.argv
    sq_dir = Path('docs/SQ')
    
    if not sq_dir.exists():
        print(f"Error: {sq_dir} not found")
        sys.exit(1)
    
    files = sorted(sq_dir.rglob('*.puml'))
    # Exclude common styles
    files = [f for f in files if 'common' not in str(f)]
    
    total_changed = 0
    total_errors = 0
    
    for filepath in files:
        try:
            changed, changes = process_file(filepath, dry_run)
            if changed:
                total_changed += 1
                action = "Would fix" if dry_run else "Fixed"
                print(f"✅ {action}: {filepath}")
                for change in changes:
                    print(f"   - {change}")
        except Exception as e:
            total_errors += 1
            print(f"❌ Error processing {filepath}: {e}")
    
    print(f"\n{'Would fix' if dry_run else 'Fixed'} {total_changed}/{len(files)} files")
    if total_errors:
        print(f"Errors: {total_errors}")
    
    return 0 if total_errors == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
