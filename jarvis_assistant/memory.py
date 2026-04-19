from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class MemoryStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(json.dumps({"history": []}, indent=2), encoding="utf-8")

    def load(self) -> dict[str, Any]:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"history": []}

    def append_turn(self, user: str, assistant: str) -> None:
        payload = self.load()
        payload.setdefault("history", []).append({"user": user, "assistant": assistant})
        payload["history"] = payload["history"][-30:]
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def recent_context(self, limit: int = 6) -> list[dict[str, str]]:
        history = self.load().get("history", [])[-limit:]
        result: list[dict[str, str]] = []
        for turn in history:
            result.append({"role": "user", "content": turn.get("user", "")})
            result.append({"role": "assistant", "content": turn.get("assistant", "")})
        return result
