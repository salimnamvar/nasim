"""Rank Ollama models from a CSV by suitability for a remote machine.

Default server is 'black' — run with no server argument to use it.

Two sources of machine spec:
  - SSH probe (default: black, or any host passed as second arg)
  - --vram / --ram overrides (for offline use, skips SSH)

Usage:
    python scripts/analyze.py data/ollama.csv                          # probes black
    python scripts/analyze.py data/ollama.csv myserver                 # probes myserver
    python scripts/analyze.py data/ollama.csv --output data/ranked.csv
    python scripts/analyze.py data/ollama.csv --top 50
    python scripts/analyze.py data/ollama.csv --vram 24 --ram 64

Fit tiers (written to 'Fit' column):
    GPU   — model fits in VRAM  (≤ vram × 0.95, leaves ~5 % for KV-cache overhead)
    CPU   — model fits in RAM   (≤ ram  × 0.80, GPU too small)
    SKIP  — model exceeds RAM (excluded from output unless --include-skip)

Score (written to 'Score' column) — higher is better within each tier:
    Quantization quality  × 30  (Q8=8, F16=9, Q4_K_M=5.5, …)
    Parameter count       × 20  (log₁₀ scale, more params → more capable)
    Context window        × 10  (log₁₀ scale, larger → more flexible)
    Popularity            ×  5  (log₁₀ downloads)
    Tier bonus: GPU +1000, CPU +100
"""

import argparse
import csv
import logging
import math
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# 1. VALUE PARSERS
# ──────────────────────────────────────────────

def parse_size_gb(s: str) -> float:
    """'4.5GB' / '581MB' → float GiB."""
    s = s.strip().upper()
    m = re.match(r"^([\d.]+)\s*(GB|MB|KB)$", s)
    if not m:
        return 0.0
    val, unit = float(m.group(1)), m.group(2)
    return {"GB": val, "MB": val / 1024, "KB": val / 1024 ** 2}[unit]


def parse_context_tokens(s: str) -> int:
    """'128K' / '1M' / '32K' → int token count."""
    s = s.strip().upper()
    m = re.match(r"^([\d.]+)\s*([KMG]?)$", s)
    if not m:
        return 0
    val, suffix = float(m.group(1)), m.group(2)
    return int(val * {"": 1, "K": 1_024, "M": 1_048_576, "G": 1_073_741_824}.get(suffix, 1))


def parse_downloads(s: str) -> float:
    """'1.1M' / '958K' / '13K' → float count."""
    s = s.strip().upper()
    m = re.match(r"^([\d.]+)\s*([KMBT]?)$", s)
    if not m:
        return 0.0
    val, suffix = float(m.group(1)), m.group(2)
    return val * {"": 1, "K": 1e3, "M": 1e6, "B": 1e9, "T": 1e12}.get(suffix, 1)


def parse_params_b(s: str) -> float:
    """'7B' / '70B' / '3.21B' → float billions (0 if unknown)."""
    s = s.strip().upper()
    m = re.match(r"^([\d.]+)\s*([BM]?)$", s)
    if not m:
        return 0.0
    val, suffix = float(m.group(1)), m.group(2)
    return val if suffix in ("B", "") else val / 1000


# Quantization → quality rank (higher = more bits retained = better output quality).
# F16/BF16 are unquantized; Q8_0 is near-lossless; Q2_K is most compressed (worst quality).
_QUANT_RANK: dict[str, float] = {
    "F32": 10.0, "F16": 9.5, "BF16": 9.5,
    "Q8_0": 8.0,
    "Q6_K": 7.0,
    "Q5_K_M": 6.5, "Q5_K_S": 6.3, "Q5_1": 6.2, "Q5_0": 6.0,
    "Q4_K_M": 5.5, "Q4_K_S": 5.3, "Q4_1": 5.1, "Q4_0": 5.0,
    "IQ4_XS": 5.2, "IQ4_NL": 5.0,
    "Q3_K_L": 4.3, "Q3_K_M": 4.2, "Q3_K_S": 4.0,
    "IQ3_M": 4.1, "IQ3_S": 4.0,
    "Q2_K": 3.0, "IQ2_M": 3.2, "IQ2_S": 3.0,
    "MXFP4": 5.0,
}


def quant_rank(q: str) -> float:
    return _QUANT_RANK.get(q.strip().upper(), 4.0)


# ──────────────────────────────────────────────
# 2. MACHINE SPEC (SSH PROBE)
# ──────────────────────────────────────────────

@dataclass
class MachineSpec:
    vram_gb: float = 0.0
    ram_gb: float = 0.0
    cpu_cores: int = 1
    gpu_name: str = ""
    ollama_installed: bool = False


def _ssh(host: str, cmd: str) -> str:
    result = subprocess.run(
        ["ssh", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes", host, cmd],
        capture_output=True, text=True, timeout=30,
    )
    return result.stdout.strip()


def probe_machine(host: str) -> MachineSpec:
    """SSH into *host* and collect VRAM, RAM, CPU, and ollama presence."""
    log.info("Probing %s …", host)
    spec = MachineSpec()

    # VRAM — sum across all GPUs
    gpu_out = _ssh(
        host,
        "nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits 2>/dev/null",
    )
    if gpu_out:
        total_mb = 0.0
        names: list[str] = []
        for line in gpu_out.splitlines():
            parts = line.rsplit(",", 1)
            if len(parts) == 2:
                name = parts[0].strip()
                try:
                    total_mb += float(parts[1].strip())
                    names.append(name)
                except ValueError:
                    pass
        spec.vram_gb = total_mb / 1024
        spec.gpu_name = ", ".join(names)

    # System RAM (bytes → GiB)
    ram_out = _ssh(host, "free -b | awk '/^Mem:/{print $2}'")
    if ram_out:
        try:
            spec.ram_gb = int(ram_out) / 1024 ** 3
        except ValueError:
            pass

    # CPU cores
    cpu_out = _ssh(host, "nproc")
    if cpu_out:
        try:
            spec.cpu_cores = int(cpu_out)
        except ValueError:
            pass

    spec.ollama_installed = bool(_ssh(host, "command -v ollama"))

    log.info(
        "  GPU: %s (%.1f GB VRAM)  RAM: %.1f GB  CPUs: %d  ollama: %s",
        spec.gpu_name or "none",
        spec.vram_gb,
        spec.ram_gb,
        spec.cpu_cores,
        "yes" if spec.ollama_installed else "no",
    )
    return spec


# ──────────────────────────────────────────────
# 3. SCORING
# ──────────────────────────────────────────────

# Fraction of VRAM / RAM to consider safely usable.
# 0.95 on VRAM: Ollama manages its own allocation; 5 % covers driver overhead.
# 0.80 on RAM: leaves headroom for OS + other processes when running CPU inference.
_VRAM_HEADROOM = 0.95
_RAM_HEADROOM = 0.80


def _log10_safe(x: float) -> float:
    return math.log10(max(x, 1.0))


def score_row(row: dict, spec: MachineSpec) -> tuple[str, float, str]:
    """Return (fit_tier, score, detail_str) for one CSV row."""
    size_gb = parse_size_gb(row.get("Size", ""))
    gpu_limit = spec.vram_gb * _VRAM_HEADROOM
    ram_limit = spec.ram_gb * _RAM_HEADROOM

    if size_gb == 0.0:
        return ("UNKNOWN", 0.0, "size_missing")

    if size_gb <= gpu_limit:
        fit = "GPU"
        tier_bonus = 1000.0
    elif size_gb <= ram_limit:
        fit = "CPU"
        tier_bonus = 100.0
    else:
        return ("SKIP", 0.0, f"size={size_gb:.1f}GB > ram_limit={ram_limit:.1f}GB")

    q = quant_rank(row.get("Quantization", "")) * 30
    ctx = _log10_safe(parse_context_tokens(row.get("Context", ""))) * 10
    dl = _log10_safe(parse_downloads(row.get("Downloads", ""))) * 5
    params = _log10_safe(parse_params_b(row.get("Parameters", "")) + 1) * 20

    score = tier_bonus + q + ctx + dl + params
    detail = (
        f"tier={tier_bonus:.0f} quant={q:.1f} ctx={ctx:.1f} "
        f"dl={dl:.1f} params={params:.1f}"
    )
    return (fit, round(score, 2), detail)


# ──────────────────────────────────────────────
# 4. MAIN
# ──────────────────────────────────────────────

_FIT_ORDER = {"GPU": 0, "CPU": 1, "UNKNOWN": 2, "SKIP": 3}


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Rank Ollama models by suitability for a target machine."
    )
    ap.add_argument("csv", type=Path, help="Input CSV (e.g. data/ollama.csv)")
    ap.add_argument(
        "server", nargs="?", default="black",
        help="SSH host to probe (default: black). Omit to use default.",
    )
    ap.add_argument("--output", "-o", type=Path, default=None,
                    help="Output CSV path. Default: <input_stem>_ranked.csv")
    ap.add_argument("--vram", type=float, default=None,
                    help="Override VRAM in GB (skip SSH probe)")
    ap.add_argument("--ram", type=float, default=None,
                    help="Override RAM in GB (skip SSH probe)")
    ap.add_argument("--top", type=int, default=None,
                    help="Limit output to top N rows per tier")
    ap.add_argument("--include-cpu", action="store_true",
                    help="Include CPU-only models in output (default: included)")
    ap.add_argument("--include-skip", action="store_true",
                    help="Include models that exceed RAM (tagged SKIP)")
    args = ap.parse_args()

    if not args.csv.exists():
        log.error("CSV not found: %s", args.csv)
        sys.exit(1)

    # Build machine spec — manual overrides take priority over SSH probe
    if args.vram is not None or args.ram is not None:
        spec = MachineSpec(
            vram_gb=args.vram or 0.0,
            ram_gb=args.ram or 0.0,
        )
        log.info("Manual spec: VRAM=%.1f GB  RAM=%.1f GB", spec.vram_gb, spec.ram_gb)
    else:
        spec = probe_machine(args.server)

    # Load and score models
    log.info("Loading %s …", args.csv)
    with args.csv.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    log.info("  %d model versions loaded.", len(rows))

    scored: list[tuple[str, float, str, dict]] = []
    for row in rows:
        fit, score, detail = score_row(row, spec)
        scored.append((fit, score, detail, row))

    # Filter
    def _keep(fit: str) -> bool:
        if fit == "SKIP" and not args.include_skip:
            return False
        return True

    scored = [t for t in scored if _keep(t[0])]

    # Sort: GPU first, then CPU, then SKIP; within tier by score descending
    scored.sort(key=lambda t: (_FIT_ORDER.get(t[0], 9), -t[1]))

    # Optional top-N per tier
    if args.top:
        from itertools import groupby
        result: list[tuple] = []
        for _tier, group in groupby(scored, key=lambda t: t[0]):
            result.extend(list(group)[: args.top])
        scored = result

    # Build output CSV
    out_path = args.output or args.csv.parent / (args.csv.stem + "_ranked.csv")
    original_fields = list(rows[0].keys()) if rows else []
    extra_fields = ["Fit", "Score", "Score_Detail", "Size_GB", "GPU_Limit_GB", "RAM_Limit_GB"]
    fieldnames = extra_fields + [f for f in original_fields if f not in extra_fields]

    gpu_limit_gb = spec.vram_gb * _VRAM_HEADROOM
    ram_limit_gb = spec.ram_gb * _RAM_HEADROOM

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for fit, score, detail, row in scored:
            out_row = dict(row)
            out_row["Fit"] = fit
            out_row["Score"] = score
            out_row["Score_Detail"] = detail
            out_row["Size_GB"] = f"{parse_size_gb(row.get('Size', '')):.2f} GB"
            out_row["GPU_Limit_GB"] = f"{gpu_limit_gb:.2f} GB"
            out_row["RAM_Limit_GB"] = f"{ram_limit_gb:.2f} GB"
            writer.writerow(out_row)

    # Summary
    gpu_count = sum(1 for t in scored if t[0] == "GPU")
    cpu_count = sum(1 for t in scored if t[0] == "CPU")
    skip_count = sum(1 for t in scored if t[0] == "SKIP")
    log.info(
        "Output: %s  [GPU=%d  CPU=%d  SKIP=%d]",
        out_path, gpu_count, cpu_count, skip_count,
    )

    if scored:
        log.info("Top 5 GPU models:")
        for fit, score, _detail, row in scored[:5]:
            if fit != "GPU":
                break
            log.info(
                "  %-30s %-25s %6s  score=%.1f",
                row.get("Model Name", ""), row.get("Version", ""),
                row.get("Size", ""), score,
            )


if __name__ == "__main__":
    main()
