"""Knowledge-base indexing + RAG query via Ollama embeddings on black.

Indexes text/code files into a local vector store (``chunks``/``embeddings`` JSONL),
embedding through the nasim tunnel so no laptop GPU is needed, and answers queries
with cosine similarity. Mirrors ``kb.sh`` using the standard library.

Functions:
    index: Build a named KB from a path.
    query: Return top-k relevant chunks for a question.
    kb_list: Show indexed KBs.
    rm: Delete a KB.
    is_indexed: Whether any KB exists.
    index_path: Root KB directory (for status display).
"""

from __future__ import annotations

import datetime
import json
import math
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

from nasim import config
from nasim.util import log

EMBED_MODEL = os.environ.get("NASIM_KB_EMBED_MODEL", "nomic-embed-text:latest")
CHUNK_SIZE = int(os.environ.get("NASIM_KB_CHUNK_SIZE", "512"))
TOP_K = int(os.environ.get("NASIM_KB_TOP_K", "5"))

_TEXT_EXT = {
    ".md", ".txt", ".rst", ".py", ".rs", ".js", ".ts", ".go", ".java",
    ".c", ".cpp", ".h", ".sh", ".yaml", ".yml", ".json", ".toml", ".ini", ".cfg",
}
_SKIP_DIRS = {"node_modules", ".git", "target", "dist", "build", "venv", "__pycache__", ".pytest_cache", ".mypy_cache"}


def _resolve_url() -> tuple[str, bool]:
    """Return an Ollama URL for embeddings and whether we started a temp tunnel.

    Returns:
        tuple[str, bool]: (url, started_temp_tunnel).
    """
    from nasim import daemon
    from nasim.transport import setup_ssh_tunnel

    if daemon.is_running():
        return daemon.url(), False
    log("starting temporary tunnel for KB operation...")
    return setup_ssh_tunnel(), True


def _embed(a_url: str, a_text: str) -> list[float]:
    """Request an embedding vector for text from Ollama.

    Args:
        a_url (str): Ollama base URL.
        a_text (str): Text to embed.

    Returns:
        list[float]: Embedding vector (empty on failure).
    """
    payload = json.dumps({"model": EMBED_MODEL, "prompt": a_text}).encode()
    req = urllib.request.Request(
        a_url.rstrip("/") + "/api/embeddings",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    vec: list[float] = []
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            vec = json.loads(resp.read()).get("embedding", []) or []
    except (urllib.error.URLError, ValueError, OSError) as exc:
        log(f"embed error: {exc}")
    return vec


def _chunk(a_text: str) -> list[str]:
    """Split text into paragraph-packed chunks bounded by CHUNK_SIZE.

    Args:
        a_text (str): File text.

    Returns:
        list[str]: Chunks.
    """
    paras = [p.strip() for p in re.split(r"\n\s*\n", a_text) if len(p.strip()) > 20]
    chunks: list[str] = []
    current = ""
    for p in paras:
        if len(current) + len(p) < CHUNK_SIZE:
            current = f"{current}\n{p}" if current else p
        else:
            if current:
                chunks.append(current)
            current = p
    if current:
        chunks.append(current)
    return [c[: CHUNK_SIZE * 2] for c in chunks]


def index(a_path: str = ".", a_name: Optional[str] = None) -> int:
    """Index files under a path into a named KB.

    Args:
        a_path (str): Directory to index.
        a_name (Optional[str]): KB name (defaults to the directory's basename).

    Returns:
        int: 0 on success, 1 on failure.
    """
    from nasim.probe import model_exists_on_black
    from nasim.transport import cleanup_tunnel

    root = Path(a_path).resolve()
    name = a_name or root.name
    idx_dir = config.KB_DIR / name
    idx_dir.mkdir(parents=True, exist_ok=True)
    log(f"indexing KB '{name}' from {a_path} ...")
    log(f"using embed model: {EMBED_MODEL} (on black)")

    url, temp = _resolve_url()
    rc = 0
    if not model_exists_on_black(EMBED_MODEL):
        log(f"WARNING: embed model '{EMBED_MODEL}' not found on black. Run on black: ollama pull {EMBED_MODEL}")
        rc = 1
    else:
        files = [
            p
            for p in root.rglob("*")
            if p.is_file() and p.suffix in _TEXT_EXT and not any(s in _SKIP_DIRS for s in p.parts)
        ]
        log(f"found {len(files)} files to index")
        embeds_path = idx_dir / "embeddings.jsonl"
        with embeds_path.open("w", encoding="utf-8") as out:
            for i, f in enumerate(files, 1):
                if i % 50 == 0:
                    log(f"  indexed {i}/{len(files)} files...")
                try:
                    text = f.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                for cid, chunk in enumerate(_chunk(text)):
                    vec = _embed(url, chunk)
                    if vec:
                        out.write(json.dumps({"file": str(f), "chunk_id": cid, "text": chunk, "embedding": vec}) + "\n")
        (idx_dir / "meta.json").write_text(
            json.dumps(
                {
                    "name": name,
                    "path": str(root),
                    "created": datetime.datetime.now().astimezone().isoformat(),
                    "embed_model": EMBED_MODEL,
                    "chunk_size": CHUNK_SIZE,
                }
            ),
            encoding="utf-8",
        )
        n = sum(1 for _ in embeds_path.open(encoding="utf-8"))
        log(f"KB '{name}' indexed — {n} chunks with embeddings")
        print(f"Usage: nasim kb query {name} 'your question'")

    if temp:
        cleanup_tunnel(f"/tmp/nasim-ssh-tunnel-{os.getpid()}.pid")
    return rc


def query(a_name: str, a_query: str) -> str:
    """Return the top-k most relevant chunks for a query.

    Args:
        a_name (str): KB name.
        a_query (str): The question.

    Returns:
        str: Formatted ``score | file | text`` lines, or empty on failure.
    """
    from nasim.transport import cleanup_tunnel

    idx_dir = config.KB_DIR / a_name
    if not idx_dir.is_dir():
        log(f"KB '{a_name}' not found. Run: nasim kb index <path> {a_name}")
        return ""

    url, temp = _resolve_url()
    q_vec = _embed(url, a_query)
    out_lines: list[str] = []
    if not q_vec:
        log("failed to embed query")
    else:
        scored = []
        embeds_path = idx_dir / "embeddings.jsonl"
        if embeds_path.is_file():
            for line in embeds_path.open(encoding="utf-8"):
                if not line.strip():
                    continue
                rec = json.loads(line)
                emb = rec.get("embedding", [])
                if emb and len(emb) == len(q_vec):
                    scored.append((_cosine(q_vec, emb), rec))
        scored.sort(key=lambda t: t[0], reverse=True)
        for score, rec in scored[:TOP_K]:
            text = rec["text"][:300].replace("\n", " ")
            out_lines.append(f"{score:.3f} | {rec['file']} | {text}")
    if temp:
        cleanup_tunnel(f"/tmp/nasim-ssh-tunnel-{os.getpid()}.pid")
    return "\n".join(out_lines)


def _cosine(a_a: list[float], a_b: list[float]) -> float:
    """Cosine similarity between two equal-length vectors.

    Args:
        a_a (list[float]): First vector.
        a_b (list[float]): Second vector.

    Returns:
        float: Similarity in [-1, 1] (0 if either is zero).
    """
    dot = sum(x * y for x, y in zip(a_a, a_b))
    na = math.sqrt(sum(x * x for x in a_a))
    nb = math.sqrt(sum(x * x for x in a_b))
    return 0.0 if na == 0 or nb == 0 else dot / (na * nb)


def kb_list() -> None:
    """Print indexed knowledge bases with metadata."""
    config.KB_DIR.mkdir(parents=True, exist_ok=True)
    dirs = [d for d in config.KB_DIR.iterdir() if d.is_dir()]
    if not dirs:
        print("No knowledge bases indexed.\nRun: nasim kb index <path> [name]")
        return
    print("Knowledge Bases:")
    for d in dirs:
        meta = d / "meta.json"
        if meta.is_file():
            m = json.loads(meta.read_text(encoding="utf-8"))
            embeds = d / "embeddings.jsonl"
            n = sum(1 for _ in embeds.open(encoding="utf-8")) if embeds.is_file() else 0
            print(f"  {d.name} — {n} chunks, model: {m.get('embed_model', '?')}, created: {m.get('created', '?')}")
        else:
            print(f"  {d.name} (no metadata)")


def rm(a_name: str) -> int:
    """Delete a KB index.

    Args:
        a_name (str): KB name.

    Returns:
        int: 0 if removed, 1 if not found.
    """
    import shutil

    idx_dir = config.KB_DIR / a_name
    rc = 1
    if idx_dir.is_dir():
        shutil.rmtree(idx_dir)
        log(f"KB '{a_name}' removed")
        rc = 0
    else:
        log(f"KB '{a_name}' not found")
    return rc


def is_indexed() -> bool:
    """Return whether at least one KB exists.

    Returns:
        bool: True if a KB directory is present.
    """
    return config.KB_DIR.is_dir() and any(config.KB_DIR.iterdir())


def index_path() -> str:
    """Return the KB root directory path if any KB exists.

    Returns:
        str: KB root path or empty string.
    """
    return str(config.KB_DIR) if is_indexed() else ""
