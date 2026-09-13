from __future__ import annotations

import json
from typing import Iterable



class LLMClient:
    def __init__(self, api_key: str, model: str) -> None:
        from openai import OpenAI

        self._client = OpenAI(api_key=api_key)
        self._model = model

    def ask(self, system: str, messages: Iterable[dict[str, str]], temperature: float = 0.2) -> str:
        response = self._client.responses.create(
            model=self._model,
            input=[{"role": "system", "content": system}, *list(messages)],
            temperature=temperature,
        )
        return response.output_text.strip()

    def ask_json(self, system: str, messages: Iterable[dict[str, str]]) -> dict:
        raw = self.ask(
            system=f"{system}\nReturn valid JSON only. No markdown.",
            messages=messages,
            temperature=0,
        )
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # graceful fallback for imperfect model outputs
            start = raw.find("{")
            end = raw.rfind("}")
            if start != -1 and end != -1 and end > start:
                return json.loads(raw[start : end + 1])
            raise ValueError(f"Model did not return JSON: {raw[:300]}")
