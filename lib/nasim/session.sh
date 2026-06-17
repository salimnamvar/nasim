#!/usr/bin/env bash
# lib/nasim/session.sh — Session history + resume (Option A/C)
#
# session_start(agent, model, url):
#   Record a new session start with timestamp, agent, model, project.
#
# session_end(session_id):
#   Mark session as ended, record duration.
#
# session_list():
#   Show recent sessions with metadata.
#
# session_resume(session_id):
#   Reconnect to a previous session (reuse tunnel + agent + model).

NASIM_SESSION_DIR="${HOME}/.local/share/nasim/sessions"
NASIM_CURRENT_SESSION_FILE="${HOME}/.local/share/nasim/current-session"

# _session_ensure_dir():
#   Ensure session directory exists.
_session_ensure_dir() {
    mkdir -p "$NASIM_SESSION_DIR"
}

# session_start(agent, model, url):
#   Record session start. Returns session_id.
session_start() {
    local agent="$1" model="$2" url="$3"
    _session_ensure_dir

    local session_id
    session_id="$(date +%Y%m%d-%H%M%S)-$$"
    local project
    project="$(git remote get-url origin 2>/dev/null || basename "$(pwd)")"
    local branch
    branch="$(git branch --show-current 2>/dev/null || echo 'none')"

    local session_file="$NASIM_SESSION_DIR/$session_id.json"
    cat > "$session_file" <<EOF
{"id": "$session_id", "start": "$(date -Iseconds)", "agent": "$agent", "model": "$model", "url": "$url", "project": "$project", "branch": "$branch", "cwd": "$(pwd)", "end": null, "duration_sec": null}
EOF

    echo "$session_id" > "$NASIM_CURRENT_SESSION_FILE"
    echo "$session_id"
}

# session_end([session_id]):
#   Mark session as ended. Defaults to current session.
session_end() {
    local session_id="${1:-$(cat "$NASIM_CURRENT_SESSION_FILE" 2>/dev/null || true)}"
    [[ -z "$session_id" ]] && return 0

    local session_file="$NASIM_SESSION_DIR/$session_id.json"
    [[ ! -f "$session_file" ]] && return 0

    # Calculate duration
    local start_ts end_ts duration
    start_ts=$(jq -r '.start' "$session_file" 2>/dev/null || echo "")
    if [[ -n "$start_ts" ]]; then
        end_ts=$(date -Iseconds)
        duration=$(python3 -c "
import sys, datetime
start = datetime.datetime.fromisoformat(sys.argv[1].replace('Z', '+00:00'))
end = datetime.datetime.fromisoformat(sys.argv[2].replace('Z', '+00:00'))
print(int((end - start).total_seconds()))
" "$start_ts" "$end_ts" 2>/dev/null || echo "0")
    else
        duration="0"
    fi

    # Update JSON
    jq ".end = \"$end_ts\" | .duration_sec = $duration" "$session_file" > "$session_file.tmp" && mv "$session_file.tmp" "$session_file" 2>/dev/null || true

    rm -f "$NASIM_CURRENT_SESSION_FILE"
}

# session_list([limit]):
#   Show recent sessions.
session_list() {
    local limit="${1:-10}"
    _session_ensure_dir

    if [[ ! -d "$NASIM_SESSION_DIR" ]] || [[ -z "$(ls -A "$NASIM_SESSION_DIR" 2>/dev/null)" ]]; then
        echo "No sessions recorded yet."
        return 0
    fi

    echo "Recent nasim sessions (last $limit):"
    echo ""
    printf "%-20s %-10s %-20s %-15s %-8s %s\n" "ID" "Agent" "Model" "Project" "Duration" "Status"
    printf "%s\n" "$(printf '=%.0s' {1..80})"

    # Sort by start time descending, take limit
    local files=()
    while IFS= read -r f; do
        files+=("$f")
    done < <(ls -t "$NASIM_SESSION_DIR"/*.json 2>/dev/null | head -n "$limit")

    for f in "${files[@]}"; do
        local id agent model project duration status
        id=$(basename "$f" .json)
        agent=$(jq -r '.agent // "?"' "$f" 2>/dev/null || echo "?")
        model=$(jq -r '.model // "?"' "$f" 2>/dev/null || echo "?")
        model="${model:0:20}"  # truncate
        project=$(jq -r '.project // "?"' "$f" 2>/dev/null || echo "?")
        project="${project:0:15}"  # truncate
        duration=$(jq -r '.duration_sec // "?"' "$f" 2>/dev/null || echo "?")
        if [[ "$duration" == "null" || "$duration" == "?" ]]; then
            status="running"
            duration="-"
        else
            status="ended"
            duration="${duration}s"
        fi
        printf "%-20s %-10s %-20s %-15s %-8s %s\n" "$id" "$agent" "$model" "$project" "$duration" "$status"
    done
}

# session_resume(session_id):
#   Reconnect to a previous session.
#   Restarts tunnel if needed, re-launches same agent + model.
session_resume() {
    local session_id="$1"
    local session_file="$NASIM_SESSION_DIR/$session_id.json"

    if [[ ! -f "$session_file" ]]; then
        log "session '$session_id' not found"
        return 1
    fi

    local agent model url project cwd
    agent=$(jq -r '.agent' "$session_file" 2>/dev/null || echo "terminal")
    model=$(jq -r '.model' "$session_file" 2>/dev/null || echo "$DEFAULT_MODEL")
    url=$(jq -r '.url' "$session_file" 2>/dev/null || echo "")
    project=$(jq -r '.project' "$session_file" 2>/dev/null || echo "")
    cwd=$(jq -r '.cwd' "$session_file" 2>/dev/null || echo "")

    log "resuming session $session_id"
    log "  agent: $agent, model: $model, project: $project"

    # Change to original directory if possible
    if [[ -n "$cwd" && -d "$cwd" ]]; then
        cd "$cwd" || log "warning: original directory $cwd not accessible"
    fi

    # Ensure tunnel is running
    if ! daemon_is_running; then
        log "restarting tunnel..."
        daemon_start
    fi

    # Get fresh URL (may have changed)
    url=$(daemon_url)

    # Re-launch agent
    log "re-launching $agent..."
    launch_agent "$agent" "$url" "$model"
}

# session_current():
#   Show current active session info.
session_current() {
    if [[ ! -f "$NASIM_CURRENT_SESSION_FILE" ]]; then
        echo "No active session."
        return 0
    fi

    local session_id
    session_id=$(cat "$NASIM_CURRENT_SESSION_FILE")
    local session_file="$NASIM_SESSION_DIR/$session_id.json"

    if [[ -f "$session_file" ]]; then
        echo "Active session: $session_id"
        jq . "$session_file" 2>/dev/null || cat "$session_file"
    else
        echo "Session $session_id not found (stale current-session marker)"
    fi
}
