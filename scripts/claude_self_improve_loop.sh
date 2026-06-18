#!/usr/bin/env bash
set -euo pipefail

# Claude-driven self-improvement loop:
# - Runs nasim claude one-shot against a targeted file
# - Continues until Claude stops producing diffs
# - Prints diffs after each iteration so you can observe what changed

TARGET_FILE="${TARGET_FILE:-src/nasim/cli.py}"
MAX_ITERS="${MAX_ITERS:-10}"

# Keep these aligned with the earlier validated working CLI path.
MODEL_TAG="${MODEL_TAG:-deepseek-r1:14b}"
AGENT_NAME="${AGENT_NAME:-claude}"

# Ensure we're in repo root (this script lives in ./scripts).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

if ! command -v git >/dev/null 2>&1; then
  echo "ERROR: git not found in PATH" >&2
  exit 1
fi

if [[ ! -f "$TARGET_FILE" ]]; then
  echo "ERROR: target file not found: $TARGET_FILE" >&2
  exit 1
fi

echo "== Claude self-improve loop =="
echo "repo:        $REPO_ROOT"
echo "target:      $TARGET_FILE"
echo "model:       $MODEL_TAG"
echo "agent:       $AGENT_NAME"
echo "max iters:   $MAX_ITERS"
echo "tunnel/url:  use existing daemon tunnel (run: ./bin/nasim start ssh-tunnel if needed)"
echo

# Baseline diff marker.
PREV_DIFF="$(git diff -- "$TARGET_FILE" || true)"
# If the tree is dirty already, we still continue but diffs will be relative to current state.
# That’s OK for iterative development, but the loop stops only when Claude makes no further changes.

for ((i=1; i<=MAX_ITERS; i++)); do
  echo "------------------------------------------------------------"
  echo "Iteration $i/$MAX_ITERS"
  echo "Running Claude one-shot to improve instruction usage/prompt formatting for: $TARGET_FILE"
  echo

  # Prompt is intentionally strict:
  # - edit only the target file
  # - produce a single coherent improvement
  # - keep changes minimal and compile-safe
  PROMPT=$(
    cat <<EOF
You are editing $TARGET_FILE for instruction/prompt robustness.

Goal:
Improve how nasim's Claude Code launch ("nasim code" / --one-shot flow) uses instructions and formats prompts so Claude reliably follows the requested coding task.

Constraints:
- ONLY modify $TARGET_FILE. Do not edit other files.
- Make small, safe, testable changes.
- Keep code style consistent with the existing file.
- If the file already satisfies the requirements, make no changes.

Deliverable:
Return a patch by directly editing the file.

What to focus on:
- How prompts/instructions are constructed/passed
- Reduce ambiguity: ensure one-shot prompts are forwarded verbatim and not mangled
- If there are existing helpers, refactor them minimally for clarity
- Add/adjust help text or comments only if necessary.

Now do the improvement. After editing, stop.
EOF
  )

  # One-shot prompt: ask Claude to edit code. We do not pass --no-context so Claude can see repo context,
  # but the prompt itself constrains edits to TARGET_FILE.
  # If your environment requires tunnel, ensure daemon is running before starting this script.
  ./bin/nasim code \
    --agent "$AGENT_NAME" \
    --model "$MODEL_TAG" \
    --one-shot "$PROMPT" \
    --context ".nasim/context.md" >/dev/null || true

  # Capture diffs after the run.
  CUR_DIFF="$(git diff -- "$TARGET_FILE" || true)"

  # Show what changed (if anything).
  if [[ "$CUR_DIFF" != "$PREV_DIFF" && -n "$CUR_DIFF" ]]; then
    echo "Changes detected in $TARGET_FILE:"
    git diff --stat -- "$TARGET_FILE" || true
    echo
    # Show a small excerpt of the diff for observation.
    git diff -- "$TARGET_FILE" | sed -n '1,200p'
    echo
  else
    echo "No new diffs detected in $TARGET_FILE. Stopping loop."
    break
  fi

  PREV_DIFF="$CUR_DIFF"
done

echo "== Loop complete =="
