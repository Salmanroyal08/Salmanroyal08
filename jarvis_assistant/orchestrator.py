from __future__ import annotations

from rich.console import Console
from rich.panel import Panel

from .agents import MultiAgentCore
from .memory import MemoryStore


class JarvisAssistant:
    def __init__(self, core: MultiAgentCore, memory: MemoryStore) -> None:
        self.core = core
        self.memory = memory
        self.console = Console()

    def ask(self, user_text: str) -> str:
        context = self.memory.recent_context()
        outputs = self.core.run(user_text=user_text, context=context)
        self.memory.append_turn(user_text, outputs.final)

        self.console.print(Panel(outputs.route, title="Router", border_style="magenta"))
        self.console.print(Panel(outputs.plan, title="Planner", border_style="cyan"))
        self.console.print(Panel(outputs.final, title="Jarvis", border_style="green"))
        return outputs.final
