"""Core agentic loop — orchestrates LLM + tools."""

from nasim.llm import OllamaClient, LLMResponse, ToolCall
from nasim.tools import get_tool_definitions, execute_tool

SYSTEM_PROMPT = """You are nasim, a code agent. You help users with software engineering tasks.

You have access to these tools:
- read_file: Read file contents
- write_file: Create or overwrite a file
- edit_file: Replace exact strings in a file
- list_dir: List directory contents
- shell_exec: Run shell commands

Rules:
- Always read files before editing them.
- Use shell_exec to run tests, linter, build commands after making changes.
- Be concise. No unnecessary explanations.
- When you finish a task, say what you did in 1-2 sentences.
- If a command fails, diagnose the error and try to fix it.
"""


class Agent:
    def __init__(self, client: OllamaClient, system_prompt: str = SYSTEM_PROMPT):
        self.client = client
        self.messages: list[dict] = [{"role": "system", "content": system_prompt}]
        self.tools = get_tool_definitions()
        self.max_iterations = 20

    def run(self, user_input: str) -> str:
        """Execute one user turn, returning the final text response."""
        self.messages.append({"role": "user", "content": user_input})

        for _ in range(self.max_iterations):
            response: LLMResponse = self.client.chat(self.messages, self.tools)

            if response.tool_calls:
                self.messages.append(
                    {"role": "assistant", "content": response.content, "tool_calls": [
                        {"id": tc.id or f"call_{i}", "type": "function", "function": {"name": tc.name, "arguments": tc.arguments}}
                        for i, tc in enumerate(response.tool_calls)
                    ]}
                )
                for tc in response.tool_calls:
                    result = execute_tool(tc.name, tc.arguments)
                    self.messages.append(
                        {"role": "tool", "content": result, "tool_call_id": tc.id or f"call_0"}
                    )
                continue

            if response.content:
                self.messages.append({"role": "assistant", "content": response.content})
                return response.content

            return "(no response)"

        return "(max tool iterations reached)"

    def run_streaming(self, user_input: str) -> str:
        """Execute one user turn with streaming output. Returns final text."""
        self.messages.append({"role": "user", "content": user_input})
        full_response = ""

        for _ in range(self.max_iterations):
            collected_text = ""
            tool_calls_buf: dict[int, ToolCall] = {}

            for chunk in self.client.chat_stream(self.messages, self.tools):
                if isinstance(chunk, str):
                    collected_text += chunk
                    print(chunk, end="", flush=True)
                elif isinstance(chunk, ToolCall):
                    tool_calls_buf[len(tool_calls_buf)] = chunk

            if tool_calls_buf:
                tool_calls_list = list(tool_calls_buf.values())
                self.messages.append(
                    {"role": "assistant", "content": collected_text, "tool_calls": [
                        {"id": f"call_{i}", "type": "function", "function": {"name": tc.name, "arguments": tc.arguments}}
                        for i, tc in enumerate(tool_calls_list)
                    ]}
                )
                if collected_text:
                    print()
                for tc in tool_calls_list:
                    print(f"\n  > {tc.name}({tc.arguments})")
                    result = execute_tool(tc.name, tc.arguments)
                    self.messages.append(
                        {"role": "tool", "content": result, "tool_call_id": f"call_0"}
                    )
                    print(f"    {result[:200]}{'...' if len(result) > 200 else ''}")
                print()
                continue

            if collected_text:
                self.messages.append({"role": "assistant", "content": collected_text})
                print()
                return collected_text

            print("\n(no response)")
            return "(no response)"

        print("\n(max tool iterations reached)")
        return "(max tool iterations reached)"

    def reset(self):
        """Clear conversation history."""
        self.messages = [self.messages[0]]  # keep system prompt
