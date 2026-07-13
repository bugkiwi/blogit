from __future__ import annotations

import json
import os
import re
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


INJECTED_BLOCKS = (
    "environment_context",
    "permissions instructions",
    "app-context",
    "collaboration_mode",
    "skills_instructions",
    "apps_instructions",
    "plugins_instructions",
    "multi_agent_mode",
    "system-reminder",
    "image",
)


@dataclass(slots=True)
class Session:
    id: str
    title: str
    updated_at: str
    project: str
    path: Path
    agent: str

    def public_dict(self) -> dict[str, str]:
        data = asdict(self)
        data["path"] = str(self.path)
        return data


@dataclass(slots=True)
class Message:
    role: str
    text: str
    timestamp: str = ""

    def public_dict(self) -> dict[str, str]:
        return asdict(self)


class SessionError(RuntimeError):
    pass


class SessionAdapter(ABC):
    name: str

    def __init__(self, home: Path):
        self.home = home.expanduser()

    @abstractmethod
    def discover(self, limit: int, include_current: bool = False) -> list[Session]:
        raise NotImplementedError

    @abstractmethod
    def extract(self, identifier: str) -> tuple[Session, list[Message]]:
        raise NotImplementedError

    def resolve(self, identifier: str, sessions: Iterable[Session]) -> Session:
        exact = [s for s in sessions if s.id == identifier]
        if exact:
            return exact[0]
        prefix = [s for s in sessions if s.id.startswith(identifier)]
        if len(prefix) == 1:
            return prefix[0]
        if not prefix:
            raise SessionError(f"No {self.name} session matches {identifier!r}")
        ids = ", ".join(s.id for s in prefix[:5])
        raise SessionError(f"Ambiguous {self.name} session prefix {identifier!r}: {ids}")


def read_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                try:
                    value = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(value, dict):
                    yield value
    except OSError as exc:
        raise SessionError(f"Could not read {path}: {exc}") from exc


def clean_visible_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    text = value.replace("\r\n", "\n").strip()
    for tag in INJECTED_BLOCKS:
        pattern = re.compile(
            rf"<\s*{re.escape(tag)}(?:\s[^>]*)?>.*?<\s*/\s*{re.escape(tag)}\s*>",
            re.IGNORECASE | re.DOTALL,
        )
        text = pattern.sub("", text).strip()
    request_marker = re.search(
        r"^\s*#{1,6}\s*My request for Codex:\s*",
        text,
        re.IGNORECASE | re.MULTILINE,
    )
    if request_marker:
        text = text[request_marker.end() :].strip()
    elif re.match(r"^\s*#{1,6}\s*Files mentioned by the user\s*:", text, re.IGNORECASE):
        return ""
    lowered = text.lstrip().lower()
    if any(lowered.startswith(f"<{tag}") for tag in INJECTED_BLOCKS):
        return ""
    return text


def first_line_title(text: str, fallback: str = "Untitled session", limit: int = 88) -> str:
    cleaned = clean_visible_text(text)
    if not cleaned:
        return fallback
    line = re.sub(r"\s+", " ", cleaned.splitlines()[0]).strip("#>* `\t")
    if not line or not any(character.isalnum() for character in line):
        return fallback
    return line if len(line) <= limit else line[: limit - 1].rstrip() + "…"


def iso_timestamp(value: Any, fallback_path: Path | None = None) -> str:
    if isinstance(value, str) and value:
        return value
    if isinstance(value, (int, float)):
        seconds = value / 1000 if value > 10_000_000_000 else value
        return datetime.fromtimestamp(seconds, tz=timezone.utc).isoformat()
    if fallback_path is not None:
        return datetime.fromtimestamp(fallback_path.stat().st_mtime, tz=timezone.utc).isoformat()
    return ""


def current_session_id(agent: str) -> str:
    names = {
        "codex": ("CODEX_THREAD_ID",),
        "claude": ("CLAUDE_SESSION_ID",),
    }
    for name in names.get(agent, ()):
        if os.environ.get(name):
            return os.environ[name]
    return ""
