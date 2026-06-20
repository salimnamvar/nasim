"""Ollama API client with streaming support."""

import json
from dataclasses import dataclass, field
from typing import Iterator

import requests


@dataclass
class ToolCall:
    name: str
    arguments: dict
    id: str = ""


@dataclass
class LLMResponse:
    content: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    done: bool = False
    total_duration_ms: float = 0
    eval_count: int = 0


class OllamaClient:
    def __init__(self, base_url: str, model: str, timeout: int = 120):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> LLMResponse:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }
        if tools:
            payload["tools"] = tools

        resp = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return self._parse_response(resp.json())

    def chat_stream(
        self, messages: list[dict], tools: list[dict] | None = None
    ) -> Iterator[str | ToolCall]:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }
        if tools:
            payload["tools"] = tools

        resp = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=self.timeout,
            stream=True,
        )
        resp.raise_for_status()

        tool_calls_buf: dict[int, ToolCall] = {}
        final_msg = {}

        for line in resp.iter_lines():
            if not line:
                continue
            chunk = json.loads(line)

            if "message" in chunk:
                msg = chunk["message"]
                final_msg = msg

                content = msg.get("content", "")
                if content:
                    yield content

                for tc in msg.get("tool_calls", []):
                    idx = tc.get("index", 0)
                    func = tc.get("function", {})
                    if idx not in tool_calls_buf:
                        tool_calls_buf[idx] = ToolCall(
                            name=func.get("name", ""),
                            arguments=func.get("arguments", {}),
                        )
                    else:
                        existing = tool_calls_buf[idx]
                        if func.get("name"):
                            existing.name = func["name"]
                        if func.get("arguments"):
                            existing.arguments.update(func["arguments"])

            if chunk.get("done"):
                final_msg = final_msg

        for tc in tool_calls_buf.values():
            yield tc

    def _parse_response(self, data: dict) -> LLMResponse:
        msg = data.get("message", {})
        tool_calls = []
        for tc in msg.get("tool_calls", []):
            func = tc.get("function", {})
            tool_calls.append(
                ToolCall(
                    name=func.get("name", ""),
                    arguments=func.get("arguments", {}),
                    id=tc.get("id", ""),
                )
            )

        return LLMResponse(
            content=msg.get("content", ""),
            tool_calls=tool_calls,
            done=data.get("done", False),
            total_duration_ms=data.get("total_duration", 0) / 1e6,
            eval_count=data.get("eval_count", 0),
        )
