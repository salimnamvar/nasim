"""Nasim Bridge — Anthropic Messages API proxy to Ollama (thin transport).

Runs on the model server. Accepts Anthropic Messages API requests from the CLI,
translates them with the pure :mod:`nasim.bridge.translator` package, and
forwards them to a local Ollama instance. This module holds **transport only** —
no translation logic (see ``.claude/rules/architecture.md``).

Endpoints:
    GET  /health                    Liveness + Ollama connectivity + inventory.
    GET  /v1/models                 Model list for the CLI model picker.
    POST /v1/messages               Chat (streaming and non-streaming).
    POST /v1/messages/count_tokens  Token estimate.
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, AsyncIterator, Dict

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

from nasim.bridge import translator
from nasim.config import Config

_CONFIG = Config.load()
logging.basicConfig(level=_CONFIG.log_level)
logger = logging.getLogger("nasim-bridge")

app = FastAPI(title="Nasim Bridge", version="1.0.0")


def _error(a_status: int, a_message: str, a_type: str = "api_error") -> JSONResponse:
    """Build an Anthropic-style error response."""
    return JSONResponse(
        status_code=a_status,
        content={"type": "error", "error": {"type": a_type, "message": a_message}},
    )


def _tool_schemas(a_body: Dict[str, Any]) -> Dict[str, Any]:
    """Extract a {tool_name: input_schema} map from an Anthropic request body."""
    result: Dict[str, Any] = {}
    for tool in a_body.get("tools", []):
        name = tool.get("name")
        if name:
            result[name] = tool.get("input_schema", {})
    return result


async def _ollama_chunks(a_response: httpx.Response) -> AsyncIterator[Dict[str, Any]]:
    """Parse an Ollama JSONL stream into chunk dicts."""
    async for line in a_response.aiter_lines():
        if line.strip():
            yield json.loads(line)


def _dump(a_label: str, a_payload: Dict[str, Any]) -> None:
    """Write a payload to the debug-dump dir when enabled (diagnostics only)."""
    if _CONFIG.debug_dump:
        try:
            out_dir = Path(_CONFIG.debug_dump)
            out_dir.mkdir(parents=True, exist_ok=True)
            stamp = f"{time.time():.3f}_{a_label}"
            (out_dir / f"{stamp}.json").write_text(json.dumps(a_payload, indent=2), encoding="utf-8")
        except OSError as exc:  # never let diagnostics break the hot path
            logger.warning("debug dump failed: %s", exc)


@app.get("/health")
async def health() -> Dict[str, Any]:
    """Report bridge and Ollama status plus available models."""
    result: Dict[str, Any]
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{_CONFIG.ollama_url}/api/tags")
            models = [m["name"] for m in resp.json().get("models", [])]
        result = {
            "status": "ok",
            "ollama": "connected",
            "default_model": _CONFIG.default_model,
            "fast_model": _CONFIG.fast_model,
            "recommended_model": _CONFIG.recommended_model,
            "num_ctx": _CONFIG.num_ctx,
            "available_models": models,
        }
    except Exception as exc:  # noqa: BLE001 — health must never raise
        result = {"status": "degraded", "ollama": "unreachable", "error": str(exc)}
    return result


@app.get("/v1/models")
async def list_models() -> Dict[str, Any]:
    """List models: the default/fast aliases plus real Ollama tags."""
    entries = [
        {"id": _CONFIG.default_model, "type": "model", "display_name": "Default (mapped)"},
        {"id": _CONFIG.fast_model, "type": "model", "display_name": "Fast (mapped)"},
    ]
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{_CONFIG.ollama_url}/api/tags")
            for model in resp.json().get("models", []):
                if model["name"] not in {e["id"] for e in entries}:
                    entries.append({"id": model["name"], "type": "model", "display_name": model["name"]})
    except Exception as exc:  # noqa: BLE001
        logger.warning("model list: ollama unreachable: %s", exc)
    return {
        "data": entries,
        "first_id": entries[0]["id"],
        "last_id": entries[-1]["id"],
        "has_more": False,
    }


@app.post("/v1/messages/count_tokens")
async def count_tokens(a_request: Request) -> Dict[str, Any]:
    """Return a heuristic input token count."""
    body = await a_request.json()
    return {"input_tokens": translator.estimate_tokens(body)}


@app.post("/v1/messages")
async def messages(a_request: Request) -> Any:
    """Handle an Anthropic Messages request, streaming or not."""
    try:
        body = await a_request.json()
    except json.JSONDecodeError:
        return _error(400, "request body is not valid JSON", "invalid_request_error")

    requested_model = body.get("model", _CONFIG.default_model)
    schemas = _tool_schemas(body)
    ollama_body = translator.anthropic_to_ollama(
        body,
        _CONFIG.default_model,
        _CONFIG.fast_model,
        _CONFIG.num_ctx,
        _CONFIG.keep_alive,
        _CONFIG.tool_temperature,
    )
    _dump("request", {"anthropic": body, "ollama": ollama_body})
    logger.info(
        "messages: model=%s -> %s stream=%s msgs=%d tools=%d",
        requested_model,
        ollama_body["model"],
        ollama_body["stream"],
        len(ollama_body["messages"]),
        len(ollama_body.get("tools", [])),
    )

    if not ollama_body["stream"]:
        try:
            async with httpx.AsyncClient(timeout=_CONFIG.request_timeout) as client:
                resp = await client.post(f"{_CONFIG.ollama_url}/api/chat", json=ollama_body)
        except httpx.HTTPError as exc:
            return _error(503, f"ollama unreachable: {exc}", "overloaded_error")
        if resp.status_code != 200:
            return _error(502, f"ollama error {resp.status_code}: {resp.text[:500]}")
        return JSONResponse(translator.ollama_to_anthropic(resp.json(), requested_model, schemas))

    async def stream() -> AsyncIterator[str]:
        try:
            async with httpx.AsyncClient(timeout=_CONFIG.request_timeout) as client:
                async with client.stream("POST", f"{_CONFIG.ollama_url}/api/chat", json=ollama_body) as resp:
                    if resp.status_code != 200:
                        detail = (await resp.aread()).decode(errors="replace")[:500]
                        yield translator.sse(
                            "error",
                            {
                                "type": "error",
                                "error": {"type": "api_error", "message": f"ollama error {resp.status_code}: {detail}"},
                            },
                        )
                        return
                    async for event in translator.stream_ollama_to_anthropic(
                        _ollama_chunks(resp), requested_model, schemas
                    ):
                        yield event
        except httpx.HTTPError as exc:
            yield translator.sse(
                "error",
                {"type": "error", "error": {"type": "overloaded_error", "message": f"ollama unreachable: {exc}"}},
            )

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
