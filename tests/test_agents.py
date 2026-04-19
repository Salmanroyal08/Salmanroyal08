from jarvis_assistant.agents import MultiAgentCore


class FakeLLM:
    def __init__(self, payloads):
        self.payloads = payloads

    def ask_json(self, system, messages):
        return self.payloads.pop(0)


class FakeTools:
    def run(self, name, tool_input):
        return f"ran {name} with {tool_input}"


def test_execute_tool_then_final():
    llm = FakeLLM(
        [
            {"intent": "coding", "reason": "code request"},
            {"goal": "build", "steps": ["a"], "risks": []},
            {"action": "tool", "tool": "list_files", "input": ".", "why": "inspect"},
            {"action": "final", "answer": "done"},
            {"final": "done polished"},
        ]
    )
    core = MultiAgentCore(llm=llm, tools=FakeTools(), max_tool_steps=3)

    result = core.run("make code", context=[])

    assert result.route == "coding"
    assert "Goal: build" in result.plan
    assert result.final == "done polished"


def test_format_plan_defaults():
    text = MultiAgentCore._format_plan({})
    assert "No goal provided" in text
    assert "No steps provided" in text
