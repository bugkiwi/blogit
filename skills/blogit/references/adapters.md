# Session adapter guide

Use this guide only when adding an agent or repairing a parser after a local session format change.

## Contract

Add `<agent>.py` under `scripts/parsers/` and implement a subclass of `SessionAdapter` with:

- `name`: stable lowercase CLI value;
- `discover(limit, include_current) -> list[Session]`;
- `extract(identifier) -> tuple[Session, list[Message]]`.

Discovery must return newest first. A `Session` needs `id`, `title`, `updated_at`, `project`, `path`, and `agent`. Resolve both full IDs and unambiguous prefixes.

Extraction must emit only visible conversational messages:

- include direct user text;
- include assistant text shown to the user;
- exclude system and developer instructions;
- exclude hidden reasoning or thinking;
- exclude tool calls, results, approvals, hooks, transport events, and attachments;
- exclude sidechains unless they are part of the visible primary conversation;
- preserve Markdown and code inside visible text;
- apply `clean_visible_text()` to remove known injected context wrappers.

Never infer prose from tool payloads. The article-writing agent can inspect final visible explanations and ask the user when evidence is missing.

## Registration

Register the adapter in `scripts/parsers/__init__.py`, add its choice in `scripts/blogit.py`, and extend auto-detection only when the runtime exposes a stable environment marker.

## Fixture test

Add a synthetic JSONL fixture or construct one in `tests/test_blogit.py`. Verify at least:

1. newest-session ordering and current-session exclusion;
2. title fallback when no explicit title exists;
3. retention of user and assistant Markdown/code;
4. removal of every non-dialogue record type;
5. full-ID, prefix, and ambiguous-prefix behavior;
6. multi-session extraction through the CLI.

Fixtures must contain invented content, never copied personal history.
