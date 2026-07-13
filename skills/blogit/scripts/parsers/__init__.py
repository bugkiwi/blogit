from __future__ import annotations

import os
from pathlib import Path

from .base import SessionAdapter, SessionError
from .claude import ClaudeAdapter
from .codex import CodexAdapter


def detect_agent() -> str:
    if os.environ.get("CLAUDE_SESSION_ID") or os.environ.get("CLAUDECODE"):
        return "claude"
    if os.environ.get("CODEX_THREAD_ID") or os.environ.get("CODEX_CI"):
        return "codex"
    raise SessionError("Could not detect the current agent; pass --agent codex or --agent claude")


def default_home(agent: str) -> Path:
    if agent == "codex":
        return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    if agent == "claude":
        return Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude"))
    raise SessionError(f"Unsupported agent: {agent}")


def make_adapter(agent: str, home: str | None = None) -> SessionAdapter:
    selected = detect_agent() if agent == "auto" else agent
    root = Path(home).expanduser() if home else default_home(selected)
    adapters = {
        "codex": CodexAdapter,
        "claude": ClaudeAdapter,
    }
    try:
        return adapters[selected](root)
    except KeyError as exc:
        raise SessionError(f"Unsupported agent: {selected}") from exc


__all__ = [
    "ClaudeAdapter",
    "CodexAdapter",
    "SessionAdapter",
    "SessionError",
    "detect_agent",
    "make_adapter",
]
