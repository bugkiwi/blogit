#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

from parsers import SessionError, make_adapter


AGENTS = ("auto", "codex", "claude")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Discover and extract visible dialogue from local agent sessions."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="list recent sessions")
    add_common_args(list_parser)
    list_parser.add_argument("--limit", type=positive_int, default=10)
    list_parser.add_argument("--include-current", action="store_true")
    list_parser.add_argument("--format", choices=("table", "json"), default="table")

    extract_parser = subparsers.add_parser("extract", help="extract visible dialogue")
    add_common_args(extract_parser)
    extract_parser.add_argument(
        "--session", action="append", required=True, help="full session ID or unique prefix; repeatable"
    )
    extract_parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    extract_parser.add_argument("--output", help="write to a UTF-8 file instead of stdout")
    return parser


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--agent", choices=AGENTS, default="auto")
    parser.add_argument("--home", help="override the selected agent config directory")


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def table_output(sessions) -> str:
    if not sessions:
        return "No sessions found."
    rows = []
    for index, session in enumerate(sessions, 1):
        date = display_date(session.updated_at)
        project = clip_display(session.project or "—", 44)
        title = clip_display(session.title.replace("\n", " "), 56)
        rows.append((str(index), title, date, project, session.id))
    headers = ("#", "Title", "Date", "Project", "Session ID")
    widths = [max(display_width(row[i]) for row in [headers, *rows]) for i in range(len(headers))]
    line = "  ".join(pad_display(headers[i], widths[i]) for i in range(len(headers)))
    separator = "  ".join("-" * widths[i] for i in range(len(headers)))
    body = ["  ".join(pad_display(row[i], widths[i]) for i in range(len(headers))) for row in rows]
    return "\n".join([line, separator, *body])


def display_date(value: str) -> str:
    if not value:
        return "unknown"
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone()
        return parsed.date().isoformat()
    except ValueError:
        return value[:10]


def display_width(value: str) -> int:
    return sum(2 if unicodedata.east_asian_width(character) in ("W", "F") else 1 for character in value)


def clip_display(value: str, maximum: int) -> str:
    if display_width(value) <= maximum:
        return value
    result: list[str] = []
    width = 0
    for character in value:
        character_width = 2 if unicodedata.east_asian_width(character) in ("W", "F") else 1
        if width + character_width > maximum - 1:
            break
        result.append(character)
        width += character_width
    return "".join(result).rstrip() + "…"


def pad_display(value: str, width: int) -> str:
    return value + " " * max(0, width - display_width(value))


def markdown_output(extracted) -> str:
    chunks = ["# Selected agent conversations"]
    for session, messages in extracted:
        title = session.title.replace("\n", " ").strip()
        chunks.append(f"\n## {title}\n")
        for message in messages:
            label = "User" if message.role == "user" else "Assistant"
            chunks.append(f"**{label}**\n\n{message.text}\n")
    return "\n".join(chunks).rstrip() + "\n"


def json_output(extracted) -> str:
    data = [
        {
            "session": session.public_dict(),
            "messages": [message.public_dict() for message in messages],
        }
        for session, messages in extracted
    ]
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def emit(content: str, output: str | None = None) -> None:
    if output:
        path = Path(output).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(path)
    else:
        sys.stdout.write(content)


def main() -> int:
    args = build_parser().parse_args()
    try:
        adapter = make_adapter(args.agent, args.home)
        if args.command == "list":
            sessions = adapter.discover(args.limit, args.include_current)
            content = (
                json.dumps([s.public_dict() for s in sessions], ensure_ascii=False, indent=2) + "\n"
                if args.format == "json"
                else table_output(sessions) + "\n"
            )
            emit(content)
            return 0

        extracted = [adapter.extract(identifier) for identifier in args.session]
        content = json_output(extracted) if args.format == "json" else markdown_output(extracted)
        emit(content, args.output)
        return 0
    except SessionError as exc:
        print(f"blogit: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
