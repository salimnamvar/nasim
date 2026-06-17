#!/usr/bin/env bash
# lib/nasim/vram.sh — Model-VRAM fit calculator (Option A/B)
#
# vram_estimate(model_tag):
#   Estimate GPU VRAM needed for a given model tag.
#   Uses heuristics based on parameter count + quantization.
#
# vram_fit([available_vram_gb]):
#   List models from black that fit in available VRAM.
#   Defaults to 11GB for GTX 1080Ti.
#
# vram_recommend():
#   Suggest best model for your GPU based on workload.

# vram_estimate(model_tag):
#   Return estimated VRAM in GB (as integer, rounded up).
#   Parses tags like: deepseek-r1:14b, qwen3:8b, llama3.1:70b, etc.
vram_estimate() {
    local tag="$1"
    local params=""
    local quant=""

    # Extract parameter count from tag
    if [[ "$tag" =~ :([0-9]+(\.[0-9]+)?)b$ ]]; then
        params="${BASH_REMATCH[1]}"
    elif [[ "$tag" =~ -([0-9]+(\.[0-9]+)?)b ]]; then
        params="${BASH_REMATCH[1]}"
    elif [[ "$tag" =~ ([0-9]+(\.[0-9]+)?)b ]]; then
        params="${BASH_REMATCH[1]}"
    fi

    # Extract quantization hints
    if [[ "$tag" == *q4_0* || "$tag" == *q4-0* ]]; then
        quant=0.5
    elif [[ "$tag" == *q4_k* || "$tag" == *q4-k* ]]; then
        quant=0.55
    elif [[ "$tag" == *q5_k* || "$tag" == *q5-k* ]]; then
        quant=0.65
    elif [[ "$tag" == *q6_k* || "$tag" == *q6-k* ]]; then
        quant=0.75
    elif [[ "$tag" == *q8_0* || "$tag" == *q8-0* || "$tag" == *q8* ]]; then
        quant=1.0
    elif [[ "$tag" == *fp16* || "$tag" == *f16* ]]; then
        quant=2.0
    elif [[ "$tag" == *fp32* || "$tag" == *f32* ]]; then
        quant=4.0
    else
        # Default to Q4_K_M (common default for Ollama)
        quant=0.55
    fi

    if [[ -z "$params" ]]; then
        echo "unknown"
        return 1
    fi

    # Calculate: params * quant * 1.2 overhead
    local vram
    vram=$(python3 -c "import math; print(math.ceil($params * $quant * 1.2))" 2>/dev/null || echo "unknown")
    echo "$vram"
}

# vram_fit([available_gb]):
#   Query black for models, filter by VRAM fit.
#   Default available: 11GB (GTX 1080Ti).
vram_fit() {
    local available="${1:-11}"
    log "checking models that fit in ${available}GB VRAM..."

    # Get model list from black
    local models_json
    models_json=$(ssh -o ConnectTimeout=5 "$BLACK_HOST" 'curl -s --max-time 8 http://localhost:11434/api/tags' 2>/dev/null) || {
        log "cannot reach black to list models"
        return 1
    }

    echo "Models fitting in ~${available}GB (with overhead):"
    echo ""

    python3 -c "
import sys, json, re, math
available = float(sys.argv[1])
data = json.loads(sys.argv[2])

def estimate(tag):
    m = re.search(r'[:\-]([0-9]+(?:\.[0-9]+)?)b', tag, re.I)
    if not m: return None
    params = float(m.group(1))

    if 'q4_0' in tag.lower(): q = 0.5
    elif 'q4_k' in tag.lower(): q = 0.55
    elif 'q5_k' in tag.lower(): q = 0.65
    elif 'q6_k' in tag.lower(): q = 0.75
    elif 'q8' in tag.lower(): q = 1.0
    elif 'fp16' in tag.lower() or 'f16' in tag.lower(): q = 2.0
    elif 'fp32' in tag.lower() or 'f32' in tag.lower(): q = 4.0
    else: q = 0.55

    return math.ceil(params * q * 1.2)

fits = []
for m in data.get('models', []):
    name = m.get('name', '?')
    vram = estimate(name)
    if vram is None: continue
    if vram <= available:
        fits.append((vram, name, m.get('details',{}).get('parameter_size','?'), m.get('details',{}).get('quantization_level','?')))

fits.sort()
for vram, name, psize, q in fits:
    print(f'  + {name} (~{vram}GB, {psize}, {q})')

if not fits:
    print('  (no models fit — consider smaller quantizations or models)')
" "$available" "$models_json"

    echo ""
    echo "Models exceeding ${available}GB:"
    python3 -c "
import sys, json, re, math
available = float(sys.argv[1])
data = json.loads(sys.argv[2])

def estimate(tag):
    m = re.search(r'[:\-]([0-9]+(?:\.[0-9]+)?)b', tag, re.I)
    if not m: return None
    params = float(m.group(1))

    if 'q4_0' in tag.lower(): q = 0.5
    elif 'q4_k' in tag.lower(): q = 0.55
    elif 'q5_k' in tag.lower(): q = 0.65
    elif 'q6_k' in tag.lower(): q = 0.75
    elif 'q8' in tag.lower(): q = 1.0
    elif 'fp16' in tag.lower() or 'f16' in tag.lower(): q = 2.0
    elif 'fp32' in tag.lower() or 'f32' in tag.lower(): q = 4.0
    else: q = 0.55

    return math.ceil(params * q * 1.2)

oversized = []
for m in data.get('models', []):
    name = m.get('name', '?')
    vram = estimate(name)
    if vram is None: continue
    if vram > available:
        oversized.append((vram, name, m.get('details',{}).get('parameter_size','?'), m.get('details',{}).get('quantization_level','?')))

oversized.sort()
for vram, name, psize, q in oversized:
    print(f'  - {name} (~{vram}GB, {psize}, {q})')
" "$available" "$models_json"
}

# vram_recommend([workload]):
#   Suggest best model for workload type.
#   Workloads: coding, reasoning, chat, general
vram_recommend() {
    local workload="${1:-coding}"
    local available="${2:-11}"

    echo "Recommendations for $workload (GPU: ~${available}GB):"
    echo ""

    case "$workload" in
        coding|code)
            echo "  1. deepseek-r1:14b (Q4_K_M) — ~9.2GB, excellent code reasoning"
            echo "  2. qwen3:8b (Q4_K_M) — ~5.3GB, fast coding + tool use"
            echo "  3. codellama:13b (Q4_K_M) — ~8.6GB, code-specialized"
            echo "  4. gemma4:9b (Q4_K_M) — ~5.9GB, Google, good balance"
            ;;
        reasoning|reason)
            echo "  1. deepseek-r1:14b (Q4_K_M) — ~9.2GB, chain-of-thought reasoning"
            echo "  2. qwen3:14b (Q4_K_M) — ~9.2GB, strong reasoning"
            echo "  3. gemma4:27b (Q4_K_M) — ~17.8GB — MAY NOT FIT your 1080Ti!"
            ;;
        chat|general)
            echo "  1. llama3.1:8b (Q4_K_M) — ~5.3GB, general purpose"
            echo "  2. qwen3:8b (Q4_K_M) — ~5.3GB, multilingual"
            echo "  3. gemma4:9b (Q4_K_M) — ~5.9GB, good balance"
            ;;
        *)
            echo "  Unknown workload '$workload'. Try: coding, reasoning, chat"
            ;;
    esac

    echo ""
    echo "Run 'nasim vram fit' to see exact models on your black server."
}

# vram_check(model_tag):
#   Quick check if model fits 1080Ti (11GB).
#   Warns if oversized, suggests alternatives.
vram_check() {
    local tag="$1"
    local vram
    vram=$(vram_estimate "$tag")

    if [[ "$vram" == "unknown" ]]; then
        log "cannot estimate VRAM for '$tag'"
        return 0
    fi

    if [[ "$vram" -gt 11 ]]; then
        log "WARNING: '$tag' needs ~${vram}GB VRAM but your 1080Ti has 11GB"
        log "This may cause OOM, slow swapping, or failure to load."
        log "Suggestions:"
        log "  - Use a smaller quantization (Q4_0 instead of Q4_K_M)"
        log "  - Use a smaller parameter count (e.g., :8b instead of :14b)"
        log "  - Run 'nasim vram fit' to see compatible models"
        return 1
    else
        log "'$tag' fits (~${vram}GB / 11GB available)"
        return 0
    fi
}
