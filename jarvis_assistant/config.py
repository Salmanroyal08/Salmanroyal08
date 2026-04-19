from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(slots=True)
class Settings:
    openai_api_key: str
    openai_model: str
    memory_file: Path
    workspace: Path


def load_settings() -> Settings:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing. Add it in your environment or .env file.")

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    memory_file = Path(os.getenv("JARVIS_MEMORY_FILE", ".jarvis_memory.json")).resolve()
    workspace = Path(os.getenv("JARVIS_WORKSPACE", ".")).resolve()

    return Settings(
        openai_api_key=api_key,
        openai_model=model,
        memory_file=memory_file,
        workspace=workspace,
    )
