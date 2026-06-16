"""Exhaustive-surface transport tests (X01-X06).

These are *client-side* Claude Code features (MCP, sub-agents, plan mode, hooks,
skills, web tools). The bridge's only job is to relay their tool definitions and
the model's tool_use faithfully; whether the model correctly *drives* a feature
is model-capability bound (recorded in docs/model-guidance.md). Each test asserts
the transport guarantee deterministically: any tool carrying an input_schema —
whatever family it belongs to — is forwarded into the Ollama request unchanged.
"""

import pytest

from nasim.bridge.translator.request import anthropic_to_ollama

_DEF = "qwen2.5-coder:14b"
_FAST = "qwen2.5-coder:7b"


def _forwarded_tools(a_tool):
    """Translate a request carrying one tool and return the Ollama tools list."""
    body = {"messages": [{"role": "user", "content": "go"}], "tools": [a_tool]}
    return anthropic_to_ollama(body, _DEF, _FAST, 32768, "60m").get("tools", [])


@pytest.mark.parametrize(
    "surface_id,tool",
    [
        (
            "X01-mcp",
            {
                "name": "mcp__github__create_issue",
                "description": "Create a GitHub issue via MCP.",
                "input_schema": {"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]},
            },
        ),
        (
            "X02-subagent-task",
            {
                "name": "Task",
                "description": "Launch a sub-agent.",
                "input_schema": {
                    "type": "object",
                    "properties": {"prompt": {"type": "string"}, "subagent_type": {"type": "string"}},
                    "required": ["prompt"],
                },
            },
        ),
        (
            "X03-plan-mode",
            {
                "name": "ExitPlanMode",
                "description": "Exit plan mode with a plan.",
                "input_schema": {"type": "object", "properties": {"plan": {"type": "string"}}, "required": ["plan"]},
            },
        ),
        (
            "X05-skill",
            {
                "name": "Skill",
                "description": "Invoke a skill / slash command.",
                "input_schema": {"type": "object", "properties": {"skill": {"type": "string"}}, "required": ["skill"]},
            },
        ),
        (
            "X06-webfetch",
            {
                "name": "WebFetch",
                "description": "Fetch a URL.",
                "input_schema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]},
            },
        ),
        (
            "X06-websearch",
            {
                "name": "WebSearch",
                "description": "Search the web.",
                "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
            },
        ),
    ],
)
def test_surface_tool_relayed_verbatim(surface_id, tool):
    """Each tool family is forwarded to Ollama with name, description, schema intact."""
    forwarded = _forwarded_tools(tool)
    assert len(forwarded) == 1, surface_id
    fn = forwarded[0]["function"]
    assert fn["name"] == tool["name"]
    assert fn["description"] == tool["description"]
    assert fn["parameters"] == tool["input_schema"]  # schema relayed unchanged


def test_x04_hooks_are_client_side_bridge_is_agnostic():
    """X04 — hooks live entirely in the client; the bridge carries no hook concept.

    A normal request translates cleanly and contains no hook-related field, which
    is the guarantee: nothing in the bridge can interfere with client-side hooks.
    """
    body = {
        "messages": [{"role": "user", "content": "run"}],
        "tools": [{"name": "Bash", "input_schema": {"type": "object"}}],
    }
    out = anthropic_to_ollama(body, _DEF, _FAST, 32768, "60m")
    assert "hooks" not in out
    assert out["tools"][0]["function"]["name"] == "Bash"


def test_surface_mixed_families_all_relayed():
    """A request mixing MCP, Task, and web tools forwards all of them."""
    tools = [
        {"name": "mcp__db__query", "input_schema": {"type": "object"}},
        {"name": "Task", "input_schema": {"type": "object"}},
        {"name": "WebSearch", "input_schema": {"type": "object"}},
    ]
    body = {"messages": [{"role": "user", "content": "go"}], "tools": tools}
    out = anthropic_to_ollama(body, _DEF, _FAST, 32768, "60m")
    names = {t["function"]["name"] for t in out["tools"]}
    assert names == {"mcp__db__query", "Task", "WebSearch"}
