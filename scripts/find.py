#!/usr/bin/env python3

import re
from pathlib import Path

# Adjust as needed
ROOT_DIR = "/home/salim/prj/salim/nasim/code/free-claude-code/"

# Matches:
# ANTHROPIC_API_KEY
# CLAUDE_MODEL
# CLAUDE_SOMETHING_ELSE
pattern = re.compile(r"\b(?:ANTHROPIC|CLAUDE)_[A-Z0-9_]+\b")

matches = set()

for file_path in Path(ROOT_DIR).rglob("*"):
    if not file_path.is_file():
        continue

    try:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        matches.update(pattern.findall(text))
    except Exception:
        pass

for item in sorted(matches):
    print(item)

print(f"\nFound {len(matches)} unique matches.")
