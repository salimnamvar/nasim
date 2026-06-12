#!/usr/bin/env python3
"""Patch the Claude Code native binary into the Naseem identity.

Claude Code ships as a bun-compiled ELF binary with its JavaScript bundle
embedded as plain UTF-8 text. Binary patching requires byte-for-byte
same-length replacements so every ELF section offset survives.

"naseem" (the standard alternate romanization of nasim, Persian for breeze)
is exactly 6 bytes — the same length as "claude" — which makes a complete,
offset-safe identity rename possible:

    claude -> naseem    Claude -> Naseem    CLAUDE -> NASEEM

Derived renames that fall out automatically, all length-preserving:
    CLAUDE.md            -> NASEEM.md
    .claude/  ~/.claude  -> .naseem/  ~/.naseem
    .claude.json         -> .naseem.json
    CLAUDE_CONFIG_DIR    -> NASEEM_CONFIG_DIR
    CLAUDE_CODE_*        -> NASEEM_CODE_*
    "Claude Code"        -> "Naseem Code"

Side effects that are intentional and safe in the Nasim deployment:
    - Model IDs become naseem-* — the Bridge maps any non-Ollama name anyway.
    - Update/marketing URLs become dead — auto-update must be off regardless,
      or it would overwrite this patch.
    - anthropic-beta header values are renamed — the Bridge ignores them.

Usage:
    patch-binary.py <input-binary> <output-binary>
"""

import stat
import sys
from pathlib import Path
from typing import List, Tuple

REPLACEMENTS: List[Tuple[bytes, bytes]] = [
    (b"claude", b"naseem"),
    (b"Claude", b"Naseem"),
    (b"CLAUDE", b"NASEEM"),
]


def patch(a_src: Path, a_dst: Path) -> Tuple[bool, List[Tuple[str, int]]]:
    """Apply same-length identity replacements to a binary.

    Args:
        a_src (Path): Input binary path.
        a_dst (Path): Output binary path (made executable).

    Returns:
        Tuple[bool, List[Tuple[str, int]]]: (success, per-pattern counts).
    """
    counts: List[Tuple[str, int]] = []
    success = False

    data = a_src.read_bytes()
    for old, new in REPLACEMENTS:
        if len(old) != len(new):
            raise ValueError(f"length mismatch: {old!r} -> {new!r}")
        counts.append((old.decode(), data.count(old)))
        data = data.replace(old, new)

    leftovers = sum(data.count(old) for old, _ in REPLACEMENTS)
    if leftovers == 0:
        a_dst.write_bytes(data)
        a_dst.chmod(a_dst.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        success = True

    return (success, counts)


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    ok, counts = patch(src, dst)
    for pattern, n in counts:
        print(f"  {pattern}: {n} occurrences replaced")
    print(f"{'OK' if ok else 'FAIL'}: {dst} ({dst.stat().st_size if ok else 0} bytes)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
