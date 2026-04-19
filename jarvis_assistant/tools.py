from __future__ import annotations

import subprocess
from pathlib import Path



class Toolset:
    def __init__(self, workspace: Path, allow_shell: bool = False) -> None:
        self.workspace = workspace
        self.allow_shell = allow_shell

    def run(self, name: str, tool_input: str) -> str:
        if name == "web_search":
            return self.web_search(tool_input)
        if name == "run_shell":
            return self.run_shell(tool_input)
        if name == "read_file":
            return self.read_file(tool_input)
        if name == "write_file":
            path, _, content = tool_input.partition("\n")
            if not path.strip() or not content:
                return "write_file expects '<relative_path>\\n<content>'"
            return self.write_file(path.strip(), content)
        if name == "list_files":
            return self.list_files(tool_input or ".")
        return f"Unknown tool: {name}"

    def web_search(self, query: str, max_results: int = 5) -> str:
        from duckduckgo_search import DDGS

        rows: list[str] = []
        with DDGS() as ddgs:
            for item in ddgs.text(query, max_results=max_results):
                title = item.get("title", "")
                href = item.get("href", "")
                body = item.get("body", "")
                rows.append(f"- {title}\n  {href}\n  {body}")
        return "\n".join(rows) if rows else "No results found."

    def run_shell(self, command: str, timeout: int = 120) -> str:
        if not self.allow_shell:
            return "Shell tool is disabled. Start CLI with --allow-shell to enable it."

        proc = subprocess.run(
            command,
            cwd=self.workspace,
            shell=True,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = []
        if proc.stdout.strip():
            output.append(f"STDOUT:\n{proc.stdout.strip()}")
        if proc.stderr.strip():
            output.append(f"STDERR:\n{proc.stderr.strip()}")
        output.append(f"EXIT_CODE: {proc.returncode}")
        return "\n\n".join(output)

    def _resolve_path(self, relative_path: str) -> Path:
        path = (self.workspace / relative_path).resolve()
        if not str(path).startswith(str(self.workspace)):
            raise ValueError("Blocked: path escapes workspace.")
        return path

    def write_file(self, relative_path: str, content: str) -> str:
        path = self._resolve_path(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Wrote {relative_path}"

    def read_file(self, relative_path: str) -> str:
        path = self._resolve_path(relative_path)
        if not path.exists():
            return "File not found."
        return path.read_text(encoding="utf-8")

    def list_files(self, relative_dir: str = ".") -> str:
        target = self._resolve_path(relative_dir)
        if not target.exists():
            return "Directory not found."
        if target.is_file():
            return str(target.relative_to(self.workspace))

        files: list[str] = []
        for child in sorted(target.iterdir()):
            prefix = "[D]" if child.is_dir() else "[F]"
            files.append(f"{prefix} {child.relative_to(self.workspace)}")
        return "\n".join(files) if files else "(empty directory)"
