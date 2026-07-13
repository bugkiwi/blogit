from __future__ import annotations

import re
from datetime import datetime
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


UUID_AT_END = re.compile(
    r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.jsonl$",
    re.IGNORECASE,
)


class CodexAdapter(SessionAdapter):
    name = "codex"

    def _paths(self) -> dict[str, Path]:
        paths: dict[str, Path] = {}
        roots = (self.home / "sessions", self.home / "archived_sessions")
        for root in roots:
            if not root.exists():
                continue
            for path in root.rglob("*.jsonl"):
                match = UUID_AT_END.search(path.name)
                if match:
                    paths[match.group(1)] = path
        return paths

    def _index(self) -> dict[str, dict[str, Any]]:
        index: dict[str, dict[str, Any]] = {}
        path = self.home / "session_index.jsonl"
        if not path.exists():
            return index
        for row in read_jsonl(path):
            identifier = row.get("id")
            if isinstance(identifier, str):
                index[identifier] = row
        return index

    @staticmethod
    def _metadata(path: Path) -> tuple[str, str, str, str, bool]:
        identifier = ""
        created = ""
        project = ""
        first_user = ""
        is_subagent = False
        for row in read_jsonl(path):
            row_type = row.get("type")
            payload = row.get("payload")
            if row_type == "session_meta" and isinstance(payload, dict):
                identifier = str(payload.get("id") or payload.get("session_id") or identifier)
                created = iso_timestamp(payload.get("timestamp") or row.get("timestamp"), path)
                project = str(payload.get("cwd") or "")
                source = payload.get("source")
                is_subagent = payload.get("thread_source") == "subagent" or (
                    isinstance(source, dict) and "subagent" in source
                )
            elif row_type == "response_item" and isinstance(payload, dict):
                if payload.get("type") == "message" and payload.get("role") == "user":
                    first_user = clean_visible_text(_content_text(payload.get("content")))
                    if first_user:
                        break
            if identifier and first_user:
                break
        return identifier, created or iso_timestamp(None, path), project, first_user, is_subagent

    def _candidate_paths(self) -> list[tuple[str, Path, dict[str, Any]]]:
        path_map = self._paths()
        index = self._index()
        return sorted(
            (
                (identifier, path, index.get(identifier, {}))
                for identifier, path in path_map.items()
            ),
            key=lambda item: _sort_time(item[2].get("updated_at"), item[1]),
            reverse=True,
        )

    def discover(self, limit: int, include_current: bool = False) -> list[Session]:
        current = "" if include_current else current_session_id(self.name)
        sessions: list[Session] = []
        seen: set[str] = set()

        for identifier, path, row in self._candidate_paths():
            if identifier == current:
                continue
            meta_id, _created, project, first_user, is_subagent = self._metadata(path)
            actual_id = meta_id or identifier
            if is_subagent or actual_id in seen or actual_id == current:
                continue
            title = str(row.get("thread_name") or "").strip()
            if not title:
                title = first_line_title(first_user, fallback=f"Codex session {actual_id[:8]}")
            updated = iso_timestamp(row.get("updated_at"), path) if row else iso_timestamp(None, path)
            sessions.append(
                Session(actual_id, title, updated, project, path, self.name)
            )
            seen.add(actual_id)
            if len(sessions) >= limit:
                break

        return sessions

    def extract(self, identifier: str) -> tuple[Session, list[Message]]:
        candidates = self._candidate_paths()
        stubs = [Session(item_id, "", "", "", path, self.name) for item_id, path, _ in candidates]
        stub = self.resolve(identifier, stubs)
        row = next((row for item_id, _, row in candidates if item_id == stub.id), {})
        meta_id, _created, project, first_user, _ = self._metadata(stub.path)
        title = str(row.get("thread_name") or "").strip() or first_line_title(
            first_user, fallback=f"Codex session {(meta_id or stub.id)[:8]}"
        )
        session = Session(
            meta_id or stub.id,
            title,
            iso_timestamp(row.get("updated_at"), stub.path) if row else iso_timestamp(None, stub.path),
            project,
            stub.path,
            self.name,
        )
        messages: list[Message] = []
        for row in read_jsonl(session.path):
            if row.get("type") != "response_item":
                continue
            payload = row.get("payload")
            if not isinstance(payload, dict) or payload.get("type") != "message":
                continue
            role = payload.get("role")
            if role not in ("user", "assistant"):
                continue
            text = clean_visible_text(_content_text(payload.get("content")))
            if text:
                messages.append(Message(role, text, iso_timestamp(row.get("timestamp"))))
        if not messages:
            raise SessionError(f"No visible dialogue found in Codex session {session.id}")
        return session, messages


def _content_text(content: Any) -> str:
    if not isinstance(content, list):
        return ""
    texts: list[str] = []
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type") not in ("input_text", "output_text", "text"):
            continue
        text = block.get("text")
        if isinstance(text, str) and text.strip():
            texts.append(text.strip())
    return "\n\n".join(texts)


def _sort_time(value: Any, path: Path) -> float:
    if isinstance(value, str) and value:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
        except ValueError:
            pass
    if isinstance(value, (int, float)):
        return value / 1000 if value > 10_000_000_000 else float(value)
    return path.stat().st_mtime
