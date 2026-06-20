"""Tool registry and implementations."""

import os
import subprocess
from pathlib import Path

TOOL_REGISTRY: dict[str, dict] = {}


def tool(name: str, description: str, parameters: dict):
    """Decorator to register a tool."""

    def decorator(func):
        TOOL_REGISTRY[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "handler": func,
        }
        return func

    return decorator


def get_tool_definitions() -> list[dict]:
    """Return OpenAI-compatible tool definitions for Ollama."""
    defs = []
    for t in TOOL_REGISTRY.values():
        defs.append(
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["parameters"],
                },
            }
        )
    return defs


def execute_tool(name: str, arguments: dict) -> str:
    """Execute a registered tool and return the result as a string."""
    if name not in TOOL_REGISTRY:
        return f"Error: unknown tool '{name}'"
    try:
        result = TOOL_REGISTRY[name]["handler"](**arguments)
        return result
    except Exception as e:
        return f"Error executing {name}: {e}"


@tool(
    name="read_file",
    description="Read the contents of a file at the given path.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Absolute or relative file path"},
            "offset": {
                "type": "integer",
                "description": "Line number to start reading from (1-indexed, default 1)",
            },
            "limit": {
                "type": "integer",
                "description": "Max lines to read (default 2000)",
            },
        },
        "required": ["path"],
    },
)
def read_file(path: str, offset: int = 1, limit: int = 2000) -> str:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        return f"Error: file not found: {path}"
    if not p.is_file():
        return f"Error: not a file: {path}"
    try:
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        start = max(0, offset - 1)
        end = start + limit
        chunk = lines[start:end]
        numbered = [f"{start + i + 1}: {line}" for i, line in enumerate(chunk)]
        result = "\n".join(numbered)
        if end < len(lines):
            result += f"\n... ({len(lines) - end} more lines)"
        return result
    except Exception as e:
        return f"Error reading {path}: {e}"


@tool(
    name="write_file",
    description="Write content to a file. Creates the file if it doesn't exist, overwrites if it does.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File path to write to"},
            "content": {"type": "string", "description": "Content to write"},
        },
        "required": ["path", "content"],
    },
)
def write_file(path: str, content: str) -> str:
    p = Path(path).expanduser().resolve()
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error writing {path}: {e}"


@tool(
    name="edit_file",
    description="Replace an exact string in a file with a new string.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File path"},
            "old_string": {"type": "string", "description": "Exact text to find"},
            "new_string": {"type": "string", "description": "Replacement text"},
        },
        "required": ["path", "old_string", "new_string"],
    },
)
def edit_file(path: str, old_string: str, new_string: str) -> str:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        return f"Error: file not found: {path}"
    try:
        content = p.read_text(encoding="utf-8")
        count = content.count(old_string)
        if count == 0:
            return f"Error: old_string not found in {path}"
        if count > 1:
            return f"Error: old_string found {count} times in {path}. Provide more context to make it unique."
        new_content = content.replace(old_string, new_string, 1)
        p.write_text(new_content, encoding="utf-8")
        return f"Edited {path}: replaced 1 occurrence"
    except Exception as e:
        return f"Error editing {path}: {e}"


@tool(
    name="list_dir",
    description="List files and directories at the given path.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Directory path (default: current directory)",
            },
        },
    },
)
def list_dir(path: str = ".") -> str:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        return f"Error: path not found: {path}"
    if not p.is_dir():
        return f"Error: not a directory: {path}"
    try:
        entries = sorted(p.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
        lines = []
        for entry in entries:
            prefix = "  " if entry.is_file() else "d "
            lines.append(f"{prefix}{entry.name}")
        return "\n".join(lines) if lines else "(empty directory)"
    except Exception as e:
        return f"Error listing {path}: {e}"


@tool(
    name="shell_exec",
    description="Execute a shell command and return its output.",
    parameters={
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Shell command to execute"},
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds (default 30)",
            },
        },
        "required": ["command"],
    },
)
def shell_exec(command: str, timeout: int = 30) -> str:
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.getcwd(),
        )
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += ("\n" if output else "") + result.stderr
        if result.returncode != 0:
            output += f"\n(exit code: {result.returncode})"
        return output.strip() if output.strip() else "(no output)"
    except subprocess.TimeoutExpired:
        return f"Error: command timed out after {timeout}s"
    except Exception as e:
        return f"Error executing command: {e}"
