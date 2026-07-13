from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .base import (
    Message,
    Session,
    SessionAdapter,
    SessionError,
    clean_visible_text,
    current_session_id,
    first_line_title,
    iso_timestamp,
    read_jsonl,
)


UUID_FILE = re.compile(
    r"^([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.jsonl$",
    re.IGNORECASE,
)


class ClaudeAdapter(SessionAdapter):
    name = "claude"

    def _paths(self) -> dict[str, Path]:
        paths: dict[str, Path] = {}
        root = self.home / "projects"
        if not root.exists():
            return paths
        for path in root.rglob("*.jsonl"):
            match = UUID_FILE.match(path.name)
            if match:
                paths[match.group(1)] = path
        return paths

    def _history(self) -> dict[str, dict[str, Any]]:
        grouped: dict[str, dict[str, Any]] = {}
        path = self.home / "history.jsonl"
        if not path.exists():
            return grouped
        for row in read_jsonl(path):
            identifier = row.get("sessionId")
            if not isinstance(identifier, str):
                continue
            current = grouped.setdefault(identifier, {})
            timestamp = row.get("timestamp")
            if not current.get("first_prompt") and isinstance(row.get("display"), str):
                current["first_prompt"] = row["display"]
            if not current.get("project") and isinstance(row.get("project"), str):
                current["project"] = row["project"]
            if isinstance(timestamp, (int, float)) and timestamp >= current.get("timestamp", 0):
                current["timestamp"] = timestamp
        return grouped

    @staticmethod
    def _metadata(path: Path) -> tuple[str, str, str, str]:
        title = ""
        identifier = ""
        project = ""
        first_user = ""
        timestamp = ""
        for row in read_jsonl(path):
            identifier = str(row.get("sessionId") or identifier)
            timestamp = iso_timestamp(row.get("timestamp"), path) or timestamp
            project = str(row.get("cwd") or project)
            if row.get("type") == "ai-title" and isinstance(row.get("aiTitle"), str):
                title = row["aiTitle"].strip() or title
            if row.get("type") == "user" and not row.get("isSidechain") and not first_user:
                message = row.get("message")
                if isinstance(message, dict):
                    first_user = clean_visible_text(_content_text(message.get("content")))
        return identifier, title, project, first_user or timestamp

    def discover(self, limit: int, include_current: bool = False) -> list[Session]:
        path_map = self._paths()
        history = self._history()
        current = "" if include_current else current_session_id(self.name)
        sessions: list[Session] = []
        used: set[str] = set()

        candidates = sorted(
            ((identifier, path, history.get(identifier, {})) for identifier, path in path_map.items()),
            key=lambda item: item[2].get("timestamp", item[1].stat().st_mtime * 1000),
            reverse=True,
        )
        for identifier, path, row in candidates:
            if identifier == current:
                continue
            meta_id, title, project, first_or_timestamp = self._metadata(path)
            actual_id = meta_id or identifier
            if actual_id in used or actual_id == current:
                continue
            first_prompt = str(row.get("first_prompt") or "")
            if not title:
                title = first_line_title(first_prompt or first_or_timestamp, fallback=f"Claude session {actual_id[:8]}")
            updated = iso_timestamp(row.get("timestamp"), path)
            sessions.append(
                Session(
                    actual_id,
                    title,
                    updated,
                    str(row.get("project") or project),
                    path,
                    self.name,
                )
            )
            used.add(actual_id)
            if len(sessions) >= limit:
                break

        return sessions

    def extract(self, identifier: str) -> tuple[Session, list[Message]]:
        path_map = self._paths()
        stubs = [Session(item_id, "", "", "", path, self.name) for item_id, path in path_map.items()]
        stub = self.resolve(identifier, stubs)
        history = self._history().get(stub.id, {})
        meta_id, title, project, first_or_timestamp = self._metadata(stub.path)
        actual_id = meta_id or stub.id
        if not title:
            title = first_line_title(
                str(history.get("first_prompt") or first_or_timestamp),
                fallback=f"Claude session {actual_id[:8]}",
            )
        session = Session(
            actual_id,
            title,
            iso_timestamp(history.get("timestamp"), stub.path),
            str(history.get("project") or project),
            stub.path,
            self.name,
        )
        messages: list[Message] = []
        for row in read_jsonl(session.path):
            role = row.get("type")
            if role not in ("user", "assistant") or row.get("isSidechain"):
                continue
            message = row.get("message")
            if not isinstance(message, dict):
                continue
            text = clean_visible_text(_content_text(message.get("content")))
            if text:
                messages.append(Message(role, text, iso_timestamp(row.get("timestamp"))))
        if not messages:
            raise SessionError(f"No visible dialogue found in Claude session {session.id}")
        return session, messages


def _content_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    texts: list[str] = []
    for block in content:
        if not isinstance(block, dict) or block.get("type") != "text":
            continue
        text = block.get("text")
        if isinstance(text, str) and text.strip():
            texts.append(text.strip())
    return "\n\n".join(texts)
