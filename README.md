# Jarvis-Like Multi-Agent Virtual Assistant (Upgraded)

This is a **ready-to-run, modular Jarvis-style assistant** with a multi-agent architecture and tool execution loop.

## What was upgraded

- Added a dedicated **router agent** to classify requests (`research`, `coding`, `automation`, `general`).
- Upgraded planner/executor/critic pipeline to use **strict JSON contracts** (more reliable than string parsing).
- Added iterative tool loop with configurable budget (`--max-tool-steps`).
- Added safer shell behavior: shell tool is disabled by default and enabled only with `--allow-shell`.
- Added `list_files` tool and richer `write_file` payload format.
- Added basic unit tests for core safety and formatting logic.

## Architecture

1. **Router Agent**: classifies intent.
2. **Planner Agent**: produces goal/steps/risks plan.
3. **Executor Agent**: either calls tools or returns final answer.
4. **Critic Agent**: refines final answer.
5. **Memory Store**: keeps recent conversational context.

## Tools

- `web_search(query)`
- `run_shell(command)` *(disabled unless `--allow-shell`)*
- `read_file(relative_path)`
- `write_file("<relative_path>\\n<content>")`
- `list_files(relative_dir)`

## Quick Start

### 1) Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2) Configure

```bash
cp .env.example .env
```

Set:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
JARVIS_MEMORY_FILE=.jarvis_memory.json
JARVIS_WORKSPACE=.
```

### 3) Run

Safe default (no shell):

```bash
jarvis
```

Enable shell tool + custom tool steps:

```bash
jarvis --allow-shell --max-tool-steps 6
```

## Dev / Tests

```bash
pip install -e .[dev]
pytest
```

## Important reality check

No AI system can literally do *everything* with zero limits. This codebase is a robust advanced foundation you can extend with domain-specific agents, APIs, and enterprise workflows.
