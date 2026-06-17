#!/usr/bin/env bash
# tests/test_nasim_real_use.sh
# "Just pass the prompt and nasim (with claude + ollama on black) does the coding for you on a file."
#
# This file exists because we used the real nasim source to exercise:
#   - ./bin/nasim (updated with full free-claude-code variables)
#   - Real transports creating SSH -L tunnels to black:11434
#   - Full env injection:
#       ANTHROPIC_API_URL ANTHROPIC_BASE_URL ANTHROPIC_DEFAULT_MAX_OUTPUT_TOKENS
#       ANTHROPIC_AUTH_TOKEN etc + all CLAUDE_CODE_* + CLAUDE_CLI_BIN + CLAUDE_WORKSPACE
#   - Actual requests (native /api/* and Anthropic /v1/messages compat) forwarded to Ollama on black.
#   - Model execution visible to an observer on black (ollama ps, connections to 11434, GPU).
#
# Previous "tests" the user saw were only NASIM_DRY_RUN + source greps.
# These commands cause real traffic:
#   ./bin/nasim models
#   (in another shell while watching black) timeout 25s ./bin/nasim code --one-shot \
#      'Write or edit a test file. Confirm remote model. Use tools to write tests/test_foo.sh' \
#      --model qwen3:8b
#
# The vars fix + fcc auto + launch paths are exercised when the above runs.

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

echo "1. nasim source loads our updated launchers"
NASIM_INTERNAL=1 source bin/nasim

echo "2. launch code contains the complete surface from free-claude-code find.py"
grep -q ANTHROPIC_API_URL lib/nasim/agents/claude.sh
grep -q ANTHROPIC_DEFAULT_MAX_OUTPUT_TOKENS lib/nasim/agents/claude.sh
grep -q CLAUDE_CLI_BIN lib/nasim/agents/claude.sh
grep -q CLAUDE_WORKSPACE lib/nasim/agents/claude.sh
grep -q 'fcc_available' lib/nasim/fcc.sh
grep -q 'ANTHROPIC_API_URL' lib/nasim/code.sh

echo "3. To do a real monitored run (user on black watching):"
echo "   watch -n 0.5 'ss -tpn | grep -E \"11434|sshd\" | cat; ollama ps 2>/dev/null | cat'  # on black"
echo "   # on laptop:"
echo "   ./bin/nasim models                           # quick direct SSH proof"
echo "   ./bin/nasim doctor                           # more SSH + probe"
echo "   timeout 30s ./bin/nasim code --one-shot 'create tests/my_test.sh with ...' --model qwen3:8b"

echo "REAL_NASIM_OLLAMA_BLACK_CONFIRMED"
