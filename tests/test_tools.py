from pathlib import Path

import pytest

from jarvis_assistant.tools import Toolset


def test_path_escape_blocked(tmp_path: Path):
    tools = Toolset(workspace=tmp_path)
    with pytest.raises(ValueError):
        tools.read_file("../outside.txt")


def test_write_and_read_file(tmp_path: Path):
    tools = Toolset(workspace=tmp_path)
    msg = tools.write_file("notes/test.txt", "hello")
    assert "Wrote notes/test.txt" in msg
    assert tools.read_file("notes/test.txt") == "hello"


def test_shell_disabled_by_default(tmp_path: Path):
    tools = Toolset(workspace=tmp_path, allow_shell=False)
    out = tools.run_shell("echo hi")
    assert "disabled" in out
