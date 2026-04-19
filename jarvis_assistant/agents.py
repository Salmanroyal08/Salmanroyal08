from __future__ import annotations

from dataclasses import dataclass

from .llm import LLMClient
from .tools import Toolset

ROUTER_SYSTEM = """
You are Jarvis router. Classify intent into one category:
research | coding | automation | general.
Return JSON: {"intent": "...", "reason": "..."}
""".strip()

PLANNER_SYSTEM = """
You are the planner. Build an actionable sequence for the request.
Return JSON:
{
  "goal": "...",
  "steps": ["..."],
  "risks": ["..."]
}
""".strip()

EXECUTOR_SYSTEM = """
You are the executor. Respond in JSON using one of these shapes:
1) {"action":"tool", "tool":"web_search|run_shell|read_file|write_file|list_files", "input":"...", "why":"..."}
2) {"action":"final", "answer":"..."}
Use tools when needed. Never invent tool output.
""".strip()

CRITIC_SYSTEM = """
You are the critic. Improve the draft for accuracy, clarity, and practical next actions.
Return JSON: {"final":"..."}
""".strip()


@dataclass(slots=True)
class AgentOutputs:
    route: str
    plan: str
    draft: str
    final: str


class MultiAgentCore:
    def __init__(self, llm: LLMClient, tools: Toolset, max_tool_steps: int = 4) -> None:
        self.llm = llm
        self.tools = tools
        self.max_tool_steps = max_tool_steps

    def run(self, user_text: str, context: list[dict[str, str]]) -> AgentOutputs:
        route_data = self.llm.ask_json(ROUTER_SYSTEM, [*context, {"role": "user", "content": user_text}])
        intent = route_data.get("intent", "general")

        plan_data = self.llm.ask_json(
            PLANNER_SYSTEM,
            [*context, {"role": "user", "content": f"Intent: {intent}\nRequest: {user_text}"}],
        )

        plan_text = self._format_plan(plan_data)
        draft = self._execute(user_text=user_text, intent=intent, plan_text=plan_text, context=context)

        final_data = self.llm.ask_json(
            CRITIC_SYSTEM,
            [{"role": "user", "content": f"Request:\n{user_text}\n\nDraft:\n{draft}"}],
        )
        final = final_data.get("final", draft)

        return AgentOutputs(route=intent, plan=plan_text, draft=draft, final=final)

    def _execute(self, user_text: str, intent: str, plan_text: str, context: list[dict[str, str]]) -> str:
        tool_history: list[str] = []
        for _ in range(self.max_tool_steps):
            exec_data = self.llm.ask_json(
                EXECUTOR_SYSTEM,
                [
                    *context,
                    {
                        "role": "user",
                        "content": (
                            f"Intent: {intent}\n"
                            f"Request: {user_text}\n"
                            f"Plan:\n{plan_text}\n"
                            f"Tool history:\n{chr(10).join(tool_history) if tool_history else '(none)'}"
                        ),
                    },
                ],
            )
            action = exec_data.get("action")
            if action == "final":
                return exec_data.get("answer", "")

            if action == "tool":
                tool = exec_data.get("tool", "")
                tool_input = exec_data.get("input", "")
                result = self.tools.run(tool, tool_input)
                tool_history.append(f"Tool {tool} input={tool_input!r}\nResult:\n{result}")
                continue

            return "I could not determine the next action from executor output."

        return (
            "I hit the tool step limit while solving this task. "
            "Please refine your request or allow a larger tool budget."
        )

    @staticmethod
    def _format_plan(plan_data: dict) -> str:
        goal = plan_data.get("goal", "No goal provided.")
        steps = plan_data.get("steps", [])
        risks = plan_data.get("risks", [])
        steps_text = "\n".join(f"{idx+1}. {step}" for idx, step in enumerate(steps)) or "1. No steps provided"
        risks_text = "\n".join(f"- {risk}" for risk in risks) or "- No major risks listed"
        return f"Goal: {goal}\n\nSteps:\n{steps_text}\n\nRisks:\n{risks_text}"
