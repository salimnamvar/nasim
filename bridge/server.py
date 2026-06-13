"""Nasim Bridge — Anthropic Messages API proxy to Ollama.

Runs on the model server (black). Accepts requests in Anthropic Messages API
format from the Nasim CLI, translates them with :mod:`translator`, and
forwards them to a local Ollama instance.

Endpoints:
    GET  /health                    Liveness + Ollama connectivity.
    GET  /v1/models                 Model list for the CLI model picker.
    POST /v1/messages               Chat (streaming and non-streaming).
    POST /v1/messages/count_tokens  Token estimate.
"""

import json
import logging
import os
from typing import Any, AsyncIterator, Dict

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

import translator

logging.basicConfig(level=os.environ.get("BRIDGE_LOG_LEVEL", "INFO"))
logger = logging.getLogger("nasim-bridge")

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
REQUEST_TIMEOUT = float(os.environ.get("BRIDGE_TIMEOUT", "600"))

app = FastAPI(title="Nasim Bridge", version="1.0.0")


def _error(a_status: int, a_message: str, a_type: str = "api_error") -> JSONResponse:
    """Build an Anthropic-style error response."""
    return JSONResponse(
        status_code=a_status,
        content={"type": "error", "error": {"type": a_type, "message": a_message}},
    )


@app.get("/health")
async def health() -> Dict[str, Any]:
    """Report bridge and Ollama status plus available models."""
    result: Dict[str, Any]
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            models = [m["name"] for m in resp.json().get("models", [])]
        result = {
            "status": "ok",
            "ollama": "connected",
            "default_model": translator.DEFAULT_MODEL,
            "fast_model": translator.FAST_MODEL,
            "num_ctx": translator.NUM_CTX,
            "available_models": models,
        }
    except Exception as exc:
        result = {"status": "degraded", "ollama": "unreachable", "error": str(exc)}
    return result


@app.get("/v1/models")
async def list_models() -> Dict[str, Any]:
    """List models: virtual Claude-compatible aliases plus real Ollama tags."""
    entries = [
        {"id": translator.DEFAULT_MODEL, "type": "model", "display_name": "Default (mapped)"},
        {"id": translator.FAST_MODEL, "type": "model", "display_name": "Fast (mapped)"},
    ]
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            for m in resp.json().get("models", []):
                if m["name"] not in {e["id"] for e in entries}:
                    entries.append({"id": m["name"], "type": "model", "display_name": m["name"]})
    except Exception as exc:
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


async def _ollama_chunks(a_response: httpx.Response) -> AsyncIterator[Dict[str, Any]]:
    """Parse Ollama JSONL stream into chunk dicts."""
    async for line in a_response.aiter_lines():
        if line.strip():
            yield json.loads(line)


@app.post("/v1/messages")
async def messages(a_request: Request) -> Any:
    """Handle an Anthropic Messages request, streaming or not."""
    try:
        body = await a_request.json()
    except json.JSONDecodeError:
        return _error(400, "request body is not valid JSON", "invalid_request_error")

    requested_model = body.get("model", translator.DEFAULT_MODEL)
    tools = body.get("tools", [])
    tool_names = [t["name"] for t in tools if t.get("name")]
    required_defaults = translator.extract_required_defaults(tools)
    ollama_body = translator.anthropic_to_ollama(body)
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
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                resp = await client.post(f"{OLLAMA_URL}/api/chat", json=ollama_body)
        except httpx.HTTPError as exc:
            return _error(503, f"ollama unreachable: {exc}", "overloaded_error")
        if resp.status_code != 200:
            return _error(502, f"ollama error {resp.status_code}: {resp.text[:500]}")
        return JSONResponse(
            translator.ollama_to_anthropic(
                resp.json(), requested_model, tool_names, required_defaults
            )
        )

    async def stream() -> AsyncIterator[str]:
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                async with client.stream(
                    "POST", f"{OLLAMA_URL}/api/chat", json=ollama_body
                ) as resp:
                    if resp.status_code != 200:
                        detail = (await resp.aread()).decode(errors="replace")[:500]
                        yield translator._sse(
                            "error",
                            {
                                "type": "error",
                                "error": {
                                    "type": "api_error",
                                    "message": f"ollama error {resp.status_code}: {detail}",
                                },
                            },
                        )
                        return
                    async for event in translator.stream_ollama_to_anthropic(
                        _ollama_chunks(resp), requested_model, tool_names, required_defaults
                    ):
                        yield event
        except httpx.HTTPError as exc:
            yield translator._sse(
                "error",
                {
                    "type": "error",
                    "error": {"type": "overloaded_error", "message": f"ollama unreachable: {exc}"},
                },
            )

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
