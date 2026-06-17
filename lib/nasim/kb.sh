#!/usr/bin/env bash
# lib/nasim/kb.sh — Knowledge Base indexing + RAG query (Option B)
#
# kb_index(path, [name]):
#   Index documents at path into a local vector store using ollama embeddings.
#   Uses the black server for embedding generation (no local GPU needed on laptop).
#   Stores index in ~/.local/share/nasim/kb/<name>/
#
# kb_query(name, query):
#   Search the KB and return top-k relevant chunks.
#   Can be injected into agent prompts via context.
#
# kb_list():
#   Show all indexed KBs.
#
# kb_rm(name):
#   Delete a KB index.

NASIM_KB_DIR="${HOME}/.local/share/nasim/kb"
NASIM_KB_EMBED_MODEL="${NASIM_KB_EMBED_MODEL:-nomic-embed-text:latest}"
NASIM_KB_CHUNK_SIZE="${NASIM_KB_CHUNK_SIZE:-512}"
NASIM_KB_TOP_K="${NASIM_KB_TOP_K:-5}"

# _kb_ensure_dir():
#   Ensure KB directory exists.
_kb_ensure_dir() {
    mkdir -p "$NASIM_KB_DIR"
}

# kb_index(path, [name]):
#   Index all text files under path into a named KB.
#   Files: .md, .txt, .rst, .py, .rs, .js, .ts, .go, .java, .c, .cpp, .h, .sh
#   Skips: node_modules, .git, target, dist, build, venv, __pycache__
kb_index() {
    local path="${1:-.}"
    local name="${2:-$(basename "$(cd "$path" && pwd)")}"
    local idx_dir="$NASIM_KB_DIR/$name"

    _kb_ensure_dir
    mkdir -p "$idx_dir"

    log "indexing KB '$name' from $path ..."
    log "using embed model: $NASIM_KB_EMBED_MODEL (on black)"

    # Get the tunnel URL (daemon must be running or we start one)
    local url
    if daemon_is_running; then
        url=$(daemon_url)
    else
        log "starting temporary tunnel for indexing..."
        url=$(setup_ssh_tunnel)
    fi

    # Check if embedding model exists on black
    if ! model_exists_on_black "$NASIM_KB_EMBED_MODEL" 2>/dev/null; then
        log "WARNING: embed model '$NASIM_KB_EMBED_MODEL' not found on black"
        log "Run on black: ollama pull $NASIM_KB_EMBED_MODEL"
        return 1
    fi

    # Find all text files
    local files_tmp="/tmp/nasim-kb-files-$$.txt"
    find "$path" -type f \
        \( -name "*.md" -o -name "*.txt" -o -name "*.rst" \
           -o -name "*.py" -o -name "*.rs" -o -name "*.js" -o -name "*.ts" \
           -o -name "*.go" -o -name "*.java" -o -name "*.c" -o -name "*.cpp" -o -name "*.h" \
           -o -name "*.sh" -o -name "*.yaml" -o -name "*.yml" -o -name "*.json" \
           -o -name "*.toml" -o -name "*.ini" -o -name "*.cfg" \) \
        ! -path "*/node_modules/*" ! -path "*/.git/*" ! -path "*/target/*" \
        ! -path "*/dist/*" ! -path "*/build/*" ! -path "*/venv/*" \
        ! -path "*/__pycache__/*" ! -path "*/.pytest_cache/*" \
        ! -path "*/.mypy_cache/*" > "$files_tmp"

    local total
    total=$(wc -l < "$files_tmp" | tr -d ' ')
    log "found $total files to index"

    # Process each file: chunk, embed, store
    local chunks_file="$idx_dir/chunks.jsonl"
    > "$chunks_file"

    local count=0
    while IFS= read -r f; do
        count=$((count + 1))
        [[ $((count % 50)) -eq 0 ]] && log "  indexed $count/$total files..."

        # Extract text (skip binary)
        if file "$f" | grep -q "text" || [[ "$f" == *.md || "$f" == *.txt || "$f" == *.rst ]]; then
            : # good
        else
            continue
        fi

        # Chunk the file
        python3 -c "
import sys, json, re
path = sys.argv[1]
chunk_size = int(sys.argv[2])
try:
    with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
        text = fh.read()
except: sys.exit(0)

# Simple chunking by paragraphs then sliding window
paras = [p.strip() for p in re.split(r'\n\s*\n', text) if len(p.strip()) > 20]
chunks = []
current = ''
for p in paras:
    if len(current) + len(p) < chunk_size:
        current += '\n' + p if current else p
    else:
        if current: chunks.append(current)
        current = p
if current: chunks.append(current)

# Sliding window for long chunks
for i, chunk in enumerate(chunks):
    rec = {'file': path, 'chunk_id': i, 'text': chunk[:chunk_size*2]}
    print(json.dumps(rec, ensure_ascii=False))
" "$f" "$NASIM_KB_CHUNK_SIZE" >> "$chunks_file" 2>/dev/null || true
    done < "$files_tmp"

    rm -f "$files_tmp"

    # Now generate embeddings for all chunks via black
    log "generating embeddings via $url ..."
    local embeds_file="$idx_dir/embeddings.jsonl"
    > "$embeds_file"

    local batch_num=0
    local batch_file="/tmp/nasim-kb-batch-$$.jsonl"
    > "$batch_file"

    while IFS= read -r line; do
        echo "$line" >> "$batch_file"
        local batch_size
        batch_size=$(wc -l < "$batch_file" | tr -d ' ')

        if [[ "$batch_size" -ge 10 ]]; then
            _kb_embed_batch "$batch_file" "$embeds_file" "$url"
            > "$batch_file"
            batch_num=$((batch_num + 1))
            [[ $((batch_num % 10)) -eq 0 ]] && log "  embedded batch $batch_num..."
        fi
    done < "$chunks_file"

    # Final batch
    if [[ -s "$batch_file" ]]; then
        _kb_embed_batch "$batch_file" "$embeds_file" "$url"
    fi
    rm -f "$batch_file"

    # Write metadata
    cat > "$idx_dir/meta.json" <<EOF
{"name": "$name", "path": "$path", "created": "$(date -Iseconds)", "embed_model": "$NASIM_KB_EMBED_MODEL", "chunk_size": $NASIM_KB_CHUNK_SIZE}
EOF

    log "KB '$name' indexed — $(wc -l < "$embeds_file" | tr -d ' ') chunks with embeddings"
    echo "Usage: nasim kb query $name 'your question'"
    echo "       nasim code --kb $name  (injects KB into agent context)"

    # Cleanup temp tunnel if we started one
    if ! daemon_is_running 2>/dev/null; then
        cleanup_tunnel "/tmp/nasim-ssh-tunnel-$$.pid" 2>/dev/null || true
    fi
}

# _kb_embed_batch(batch_file, output_file, url):
#   Send a batch of texts to ollama embeddings endpoint.
_kb_embed_batch() {
    local batch_file="$1" output_file="$2" url="$3"

    python3 -c "
import sys, json, urllib.request
batch_file = sys.argv[1]
output_file = sys.argv[2]
url = sys.argv[3]
model = sys.argv[4]

with open(batch_file) as f:
    lines = [json.loads(l) for l in f if l.strip()]

for rec in lines:
    text = rec['text']
    payload = json.dumps({'model': model, 'prompt': text}).encode()
    req = urllib.request.Request(f'{url}/api/embeddings', data=payload, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            rec['embedding'] = data.get('embedding', [])
            with open(output_file, 'a') as out:
                out.write(json.dumps(rec, ensure_ascii=False) + '\n')
    except Exception as e:
        print(f'embed error: {e}', file=sys.stderr)
" "$batch_file" "$output_file" "$url" "$NASIM_KB_EMBED_MODEL" 2>/dev/null || true
}

# kb_query(name, query):
#   Search the KB for chunks relevant to query.
#   Returns top-k results with similarity scores.
kb_query() {
    local name="$1" query="$2"
    local idx_dir="$NASIM_KB_DIR/$name"

    if [[ ! -d "$idx_dir" ]]; then
        log "KB '$name' not found. Run: nasim kb index <path> $name"
        return 1
    fi

    local url
    if daemon_is_running; then
        url=$(daemon_url)
    else
        log "starting temporary tunnel for query..."
        url=$(setup_ssh_tunnel)
    fi

    # Embed the query
    local query_embed_file="/tmp/nasim-kb-query-$$.json"
    python3 -c "
import sys, json, urllib.request
url = sys.argv[1]
model = sys.argv[2]
query = sys.argv[3]
payload = json.dumps({'model': model, 'prompt': query}).encode()
req = urllib.request.Request(f'{url}/api/embeddings', data=payload, headers={'Content-Type': 'application/json'}, method='POST')
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
        with open(sys.argv[4], 'w') as f:
            json.dump(data.get('embedding', []), f)
except Exception as e:
    print(f'query embed error: {e}', file=sys.stderr)
    sys.exit(1)
" "$url" "$NASIM_KB_EMBED_MODEL" "$query" "$query_embed_file" || {
        log "failed to embed query"
        return 1
    }

    # Search against stored embeddings
    local results
    results=$(python3 -c "
import sys, json, math

# Load query embedding
with open(sys.argv[1]) as f:
    q_embed = json.load(f)
if not q_embed:
    print('no query embedding')
    sys.exit(1)

# Load all chunk embeddings
chunks = []
with open(sys.argv[2]) as f:
    for line in f:
        if line.strip():
            chunks.append(json.loads(line))

def cosine(a, b):
    dot = sum(x*y for x,y in zip(a,b))
    norm_a = math.sqrt(sum(x*x for x in a))
    norm_b = math.sqrt(sum(x*x for x in b))
    if norm_a == 0 or norm_b == 0: return 0
    return dot / (norm_a * norm_b)

# Score all
scored = []
for c in chunks:
    emb = c.get('embedding', [])
    if emb and len(emb) == len(q_embed):
        score = cosine(q_embed, emb)
        scored.append((score, c))

scored.sort(reverse=True)
top_k = int(sys.argv[3])
for score, c in scored[:top_k]:
    text = c['text'][:300].replace(chr(10), ' ')
    print(f'{score:.3f} | {c[\"file\"]} | {text}')
" "$query_embed_file" "$idx_dir/embeddings.jsonl" "$NASIM_KB_TOP_K")

    rm -f "$query_embed_file"

    # Cleanup temp tunnel
    if ! daemon_is_running 2>/dev/null; then
        cleanup_tunnel "/tmp/nasim-ssh-tunnel-$$.pid" 2>/dev/null || true
    fi

    echo "$results"
}

# kb_list():
#   Show all indexed KBs with metadata.
kb_list() {
    _kb_ensure_dir
    if [[ ! -d "$NASIM_KB_DIR" ]] || [[ -z "$(ls -A "$NASIM_KB_DIR" 2>/dev/null)" ]]; then
        echo "No knowledge bases indexed."
        echo "Run: nasim kb index <path> [name]"
        return 0
    fi

    echo "Knowledge Bases:"
    for d in "$NASIM_KB_DIR"/*/; do
        local name
        name=$(basename "$d")
        local meta="$d/meta.json"
        if [[ -f "$meta" ]]; then
            local created embed_model chunks
            created=$(jq -r '.created // "unknown"' "$meta" 2>/dev/null || echo "unknown")
            embed_model=$(jq -r '.embed_model // "unknown"' "$meta" 2>/dev/null || echo "unknown")
            chunks=$(wc -l < "$d/embeddings.jsonl" 2>/dev/null | tr -d ' ')
            echo "  $name — $chunks chunks, model: $embed_model, created: $created"
        else
            echo "  $name (no metadata)"
        fi
    done
}

# kb_rm(name):
#   Delete a KB index.
kb_rm() {
    local name="$1"
    local idx_dir="$NASIM_KB_DIR/$name"
    if [[ -d "$idx_dir" ]]; then
        rm -rf "$idx_dir"
        log "KB '$name' removed"
    else
        log "KB '$name' not found"
        return 1
    fi
}

# kb_is_indexed():
#   True if at least one KB exists.
kb_is_indexed() {
    _kb_ensure_dir
    [[ -d "$NASIM_KB_DIR" ]] && [[ -n "$(ls -A "$NASIM_KB_DIR" 2>/dev/null)" ]]
}

# kb_index_path():
#   Return path to first KB (for status display).
kb_index_path() {
    if kb_is_indexed; then
        echo "$NASIM_KB_DIR"
    fi
}
