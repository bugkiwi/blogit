from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "blogit" / "scripts" / "blogit.py"


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records), encoding="utf-8")


class BlogitCliTests(unittest.TestCase):
    def run_cli(self, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        merged_env = os.environ.copy()
        merged_env.pop("CODEX_THREAD_ID", None)
        merged_env.pop("CLAUDE_SESSION_ID", None)
        if env:
            merged_env.update(env)
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            text=True,
            capture_output=True,
            env=merged_env,
            check=False,
        )

    def test_codex_discovers_and_extracts_only_visible_dialogue(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            session_id = "11111111-1111-4111-8111-111111111111"
            path = home / "sessions" / "2026" / "01" / "02" / f"rollout-test-{session_id}.jsonl"
            write_jsonl(
                path,
                [
                    {"timestamp": "2026-01-02T10:00:00Z", "type": "session_meta", "payload": {"id": session_id, "cwd": "/work/demo"}},
                    {"type": "response_item", "payload": {"type": "message", "role": "developer", "content": [{"type": "input_text", "text": "secret instructions"}]}},
                    {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "<environment_context>noise</environment_context>"}]}},
                    {"timestamp": "2026-01-02T10:01:00Z", "type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "# Files mentioned by the user:\n\n## trace.png: /tmp/trace.png\n\n## My request for Codex:\nWhy did the cache miss?"}, {"type": "input_text", "text": "<image name='trace'>binary placeholder</image>"}]}},
                    {"type": "response_item", "payload": {"type": "function_call", "name": "shell", "arguments": "{}"}},
                    {"timestamp": "2026-01-02T10:02:00Z", "type": "response_item", "payload": {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "The key changed after normalization.\n\n```txt\nA -> a\n```"}]}},
                ],
            )
            write_jsonl(home / "session_index.jsonl", [{"id": session_id, "thread_name": "Debugging a cache miss", "updated_at": "2026-01-02T10:02:00Z"}])
            child_id = "11111111-1111-4111-8111-111111111112"
            child_path = home / "sessions" / "2026" / "01" / "02" / f"rollout-test-{child_id}.jsonl"
            write_jsonl(
                child_path,
                [
                    {"type": "session_meta", "payload": {"session_id": session_id, "id": child_id, "thread_source": "subagent", "cwd": "/work/demo"}},
                    {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "Invisible subagent work"}]}},
                ],
            )

            listed = self.run_cli("list", "--agent", "codex", "--home", str(home), "--format", "json")
            self.assertEqual(listed.returncode, 0, listed.stderr)
            sessions = json.loads(listed.stdout)
            self.assertEqual(len(sessions), 1)
            self.assertEqual(sessions[0]["title"], "Debugging a cache miss")

            extracted = self.run_cli("extract", "--agent", "codex", "--home", str(home), "--session", session_id)
            self.assertEqual(extracted.returncode, 0, extracted.stderr)
            self.assertIn("Why did the cache miss?", extracted.stdout)
            self.assertIn("A -> a", extracted.stdout)
            self.assertNotIn("secret instructions", extracted.stdout)
            self.assertNotIn("environment_context", extracted.stdout)
            self.assertNotIn("Files mentioned by the user", extracted.stdout)
            self.assertNotIn("binary placeholder", extracted.stdout)

    def test_claude_uses_title_and_filters_thinking_and_tools(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            session_id = "22222222-2222-4222-8222-222222222222"
            path = home / "projects" / "-work-demo" / f"{session_id}.jsonl"
            write_jsonl(
                path,
                [
                    {"type": "user", "sessionId": session_id, "timestamp": "2026-01-03T10:00:00Z", "cwd": "/work/demo", "message": {"role": "user", "content": "Make retries safe."}},
                    {"type": "assistant", "sessionId": session_id, "timestamp": "2026-01-03T10:01:00Z", "message": {"role": "assistant", "content": [{"type": "thinking", "thinking": "hidden"}, {"type": "tool_use", "name": "read"}, {"type": "text", "text": "I added an idempotency key."}]}},
                    {"type": "assistant", "sessionId": session_id, "timestamp": "2026-01-03T10:02:00Z", "message": {"role": "assistant", "content": "The replay test passed."}},
                    {"type": "user", "sessionId": session_id, "message": {"role": "user", "content": [{"type": "tool_result", "content": "private command output"}]}},
                    {"type": "ai-title", "sessionId": session_id, "aiTitle": "Making retries idempotent"},
                ],
            )
            write_jsonl(home / "history.jsonl", [{"display": "Make retries safe.", "timestamp": 1767434460000, "project": "/work/demo", "sessionId": session_id}])

            listed = self.run_cli("list", "--agent", "claude", "--home", str(home), "--format", "json")
            self.assertEqual(listed.returncode, 0, listed.stderr)
            self.assertEqual(json.loads(listed.stdout)[0]["title"], "Making retries idempotent")

            extracted = self.run_cli("extract", "--agent", "claude", "--home", str(home), "--session", session_id)
            self.assertEqual(extracted.returncode, 0, extracted.stderr)
            self.assertIn("Make retries safe.", extracted.stdout)
            self.assertIn("I added an idempotency key.", extracted.stdout)
            self.assertIn("The replay test passed.", extracted.stdout)
            self.assertNotIn("hidden", extracted.stdout)
            self.assertNotIn("private command output", extracted.stdout)

    def test_current_codex_session_is_excluded_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            session_id = "33333333-3333-4333-8333-333333333333"
            path = home / "sessions" / f"rollout-{session_id}.jsonl"
            write_jsonl(path, [{"type": "session_meta", "payload": {"id": session_id}}, {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "Current work"}]}}])

            result = self.run_cli("list", "--agent", "codex", "--home", str(home), env={"CODEX_THREAD_ID": session_id})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("No sessions found", result.stdout)


if __name__ == "__main__":
    unittest.main()
