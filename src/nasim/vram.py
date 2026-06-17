"""Model–VRAM fit calculator.

Heuristic VRAM estimate from a model tag's parameter count and quantization hint,
plus helpers to list which models on black fit the GPU and to warn before launch.

Functions:
    estimate: Estimated VRAM (GB) for a tag, or None if unknown.
    fit: Print models on black that do / don't fit a budget.
    recommend: Print curated recommendations for a workload.
    check: Warn (and return False) if a tag likely exceeds the GPU.
"""

from __future__ import annotations

import math
import re
from typing import Optional

from nasim import config
from nasim.probe import _ssh_tags_json
from nasim.util import log


def _quant_factor(a_tag: str) -> float:
    """Return the bytes-per-parameter factor implied by a tag's quant hint.

    Args:
        a_tag (str): Model tag.

    Returns:
        float: Multiplier (defaults to Q4_K_M ~0.55).
    """
    t = a_tag.lower()
    factor = 0.55
    if "q4_0" in t or "q4-0" in t:
        factor = 0.5
    elif "q4_k" in t or "q4-k" in t:
        factor = 0.55
    elif "q5_k" in t or "q5-k" in t:
        factor = 0.65
    elif "q6_k" in t or "q6-k" in t:
        factor = 0.75
    elif "q8" in t:
        factor = 1.0
    elif "fp16" in t or "f16" in t:
        factor = 2.0
    elif "fp32" in t or "f32" in t:
        factor = 4.0
    return factor


def estimate(a_tag: str) -> Optional[int]:
    """Estimate VRAM (GB) needed for a model tag.

    Args:
        a_tag (str): Model tag like ``deepseek-r1:14b`` or ``qwen3:8b``.

    Returns:
        Optional[int]: Estimated GB (rounded up), or None if the size is unknown.
    """
    match = re.search(r"[:\-]([0-9]+(?:\.[0-9]+)?)b", a_tag, re.IGNORECASE)
    if not match:
        match = re.search(r"([0-9]+(?:\.[0-9]+)?)b", a_tag, re.IGNORECASE)
    result: Optional[int] = None
    if match:
        params = float(match.group(1))
        result = math.ceil(params * _quant_factor(a_tag) * 1.2)
    return result


def fit(a_available_gb: Optional[int] = None) -> None:
    """Print models on black grouped by whether they fit the VRAM budget.

    Args:
        a_available_gb (Optional[int]): Budget in GB; defaults to config value.
    """
    cfg = config.get_config()
    available = a_available_gb if a_available_gb is not None else cfg.gpu_vram_gb
    log(f"checking models that fit in {available}GB VRAM...")
    data = _ssh_tags_json(cfg.black_host)
    if not data:
        log("cannot reach black to list models")
        return

    fits, oversized = [], []
    for m in data.get("models", []):
        name = m.get("name", "?")
        gb = estimate(name)
        if gb is None:
            continue
        details = m.get("details", {})
        row = (gb, name, details.get("parameter_size", "?"), details.get("quantization_level", "?"))
        (fits if gb <= available else oversized).append(row)

    fits.sort()
    oversized.sort()
    print(f"Models fitting in ~{available}GB (with overhead):\n")
    if fits:
        for gb, name, ps, q in fits:
            print(f"  + {name} (~{gb}GB, {ps}, {q})")
    else:
        print("  (no models fit — consider smaller quantizations or models)")
    print(f"\nModels exceeding {available}GB:")
    for gb, name, ps, q in oversized:
        print(f"  - {name} (~{gb}GB, {ps}, {q})")


def recommend(a_workload: str = "coding", a_available_gb: Optional[int] = None) -> None:
    """Print curated model recommendations for a workload.

    Args:
        a_workload (str): One of ``coding``, ``reasoning``, ``chat``/``general``.
        a_available_gb (Optional[int]): Budget in GB; defaults to config value.
    """
    cfg = config.get_config()
    available = a_available_gb if a_available_gb is not None else cfg.gpu_vram_gb
    print(f"Recommendations for {a_workload} (GPU: ~{available}GB):\n")
    if a_workload in ("coding", "code"):
        lines = [
            "  1. deepseek-r1:14b (Q4_K_M) — ~9.2GB, excellent code reasoning",
            "  2. qwen3:8b (Q4_K_M) — ~5.3GB, fast coding + tool use",
            "  3. codellama:13b (Q4_K_M) — ~8.6GB, code-specialized",
            "  4. gemma4:9b (Q4_K_M) — ~5.9GB, good balance",
        ]
    elif a_workload in ("reasoning", "reason"):
        lines = [
            "  1. deepseek-r1:14b (Q4_K_M) — ~9.2GB, chain-of-thought reasoning",
            "  2. qwen3:14b (Q4_K_M) — ~9.2GB, strong reasoning",
            "  3. gemma4:27b (Q4_K_M) — ~17.8GB — MAY NOT FIT an 11GB GPU!",
        ]
    elif a_workload in ("chat", "general"):
        lines = [
            "  1. llama3.1:8b (Q4_K_M) — ~5.3GB, general purpose",
            "  2. qwen3:8b (Q4_K_M) — ~5.3GB, multilingual",
            "  3. gemma4:9b (Q4_K_M) — ~5.9GB, good balance",
        ]
    else:
        lines = [f"  Unknown workload '{a_workload}'. Try: coding, reasoning, chat"]
    for line in lines:
        print(line)
    print("\nRun 'nasim vram fit' to see exact models on your black server.")


def check(a_tag: str) -> bool:
    """Warn if a tag likely exceeds the GPU budget; return whether it fits.

    Args:
        a_tag (str): Model tag.

    Returns:
        bool: True if it fits (or is unknown), False if it likely will not.
    """
    cfg = config.get_config()
    gb = estimate(a_tag)
    fits = True
    if gb is None:
        log(f"cannot estimate VRAM for '{a_tag}'")
    elif gb > cfg.gpu_vram_gb:
        log(f"WARNING: '{a_tag}' needs ~{gb}GB VRAM but your GPU has {cfg.gpu_vram_gb}GB")
        log("This may cause OOM, slow swapping, or failure to load.")
        log("Suggestions: smaller quant (Q4_0), smaller params (:8b), or 'nasim vram fit'.")
        fits = False
    else:
        log(f"'{a_tag}' fits (~{gb}GB / {cfg.gpu_vram_gb}GB available)")
    return fits
