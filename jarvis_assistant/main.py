from __future__ import annotations

import argparse

from rich.console import Console

from .agents import MultiAgentCore
from .config import load_settings
from .llm import LLMClient
from .memory import MemoryStore
from .orchestrator import JarvisAssistant
from .tools import Toolset


def run_cli() -> None:
    parser = argparse.ArgumentParser(description="Jarvis multi-agent assistant")
    parser.add_argument("--allow-shell", action="store_true", help="Enable shell tool execution")
    parser.add_argument("--max-tool-steps", type=int, default=4, help="Max tool loop iterations per request")
    args = parser.parse_args()

    console = Console()
    settings = load_settings()

    llm = LLMClient(api_key=settings.openai_api_key, model=settings.openai_model)
    tools = Toolset(workspace=settings.workspace, allow_shell=args.allow_shell)
    memory = MemoryStore(path=settings.memory_file)
    assistant = JarvisAssistant(
        core=MultiAgentCore(llm=llm, tools=tools, max_tool_steps=args.max_tool_steps),
        memory=memory,
    )

    console.print("[bold green]Jarvis Multi-Agent Assistant v0.2[/bold green]")
    console.print("Type 'exit' to quit.\n")

    while True:
        user_text = console.input("[bold cyan]You[/bold cyan]> ").strip()
        if not user_text:
            continue
        if user_text.lower() in {"exit", "quit"}:
            console.print("Goodbye.")
            break
        assistant.ask(user_text)


if __name__ == "__main__":
    run_cli()
