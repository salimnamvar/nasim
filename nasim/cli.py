"""Interactive CLI for the nasim code agent."""

import argparse
import sys

from nasim.agent import Agent
from nasim.llm import OllamaClient


BANNER = """nasim v0.1.0 — code agent CLI
Powered by Ollama | Type /help for commands
"""


def parse_args():
    parser = argparse.ArgumentParser(description="nasim — code agent CLI")
    parser.add_argument("--model", default="qwen2.5-coder:14b", help="Ollama model name")
    parser.add_argument("--server", default="http://192.168.70.125:11434", help="Ollama server URL")
    parser.add_argument("--no-stream", action="store_true", help="Disable streaming output")
    parser.add_argument("-c", "--command", help="Run a single command and exit")
    return parser.parse_args()


def print_help():
    print("""
Commands:
  /help     Show this help
  /reset    Clear conversation history
  /model    Show current model
  /quit     Exit
""")


def repl(args):
    client = OllamaClient(args.server, args.model)
    agent = Agent(client)

    print(BANNER)
    print(f"Model:   {args.model}")
    print(f"Server:  {args.server}")
    print()

    while True:
        try:
            user_input = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not user_input:
            continue

        if user_input == "/quit" or user_input == "/exit":
            print("Bye.")
            break
        if user_input == "/help":
            print_help()
            continue
        if user_input == "/reset":
            agent.reset()
            print("History cleared.")
            continue
        if user_input == "/model":
            print(f"Current model: {args.model}")
            continue

        try:
            if args.no_stream:
                response = agent.run(user_input)
                print(f"nasim> {response}")
            else:
                print("nasim> ", end="", flush=True)
                agent.run_streaming(user_input)
        except KeyboardInterrupt:
            print("\n(interrupted)")
        except Exception as e:
            print(f"\nError: {e}")


def single_command(args):
    client = OllamaClient(args.server, args.model)
    agent = Agent(client)
    try:
        if args.no_stream:
            response = agent.run(args.command)
            print(response)
        else:
            agent.run_streaming(args.command)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    args = parse_args()
    if args.command:
        single_command(args)
    else:
        repl(args)


if __name__ == "__main__":
    main()
