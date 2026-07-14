# Blogit

**English** | [简体中文](README.zh-CN.md)

Turn recent Codex or Claude coding sessions into evidence-backed, first-person Markdown articles.

Blogit does more than compress a chat transcript into a summary. It finds the story worth telling: the original problem, the evidence that changed the author's understanding, the decisions that mattered, the failed paths, and the lesson a reader can reuse. It asks you to select the source sessions, approve an Article contract covering title, evidence, and scope, and only then writes the complete article.

## What it does

- Discovers recent local Codex or Claude sessions.
- Extracts only user- and assistant-visible dialogue while filtering system prompts, hidden reasoning, tool calls, and tool results.
- Performs targeted, read-only repository verification for falsifiable claims such as the final implementation, the correct mechanism, or deployment status.
- Combines related sessions into one coherent article.
- Sets no default length limit; it estimates length bottom-up from the number of distinct claims, the evidence, and the explanation depth.
- Starts every article with consistent YAML frontmatter containing title, date, description, tags, slug, and draft status.
- Stores Markdown and relative image assets under the user's `Documents/blogit` directory by default, while supporting a user-selected folder.
- Presents an Article contract with the article mode, title promise, evidence structure, scope exclusions, and a dynamic length estimate before drafting.
- Runs four pass/fail editing gates—structure, compression, voice, and verification—and rewrites the draft when a gate fails.
- Keeps the author as the article's only narrator. It never exposes an assistant, agent, conversation, prompt, or tool-process viewpoint, and never uses “we” to mean the author plus AI.
- Redacts sensitive material and distinguishes verified facts from unresolved claims.
- Adds useful visuals for architecture, state changes, timelines, and comparisons: Codex prefers available image or diagram generation; Claude first checks for connected drawing tools and falls back to character diagrams when none are available.

## Workflow

```text
Discover sessions → you select sessions → extract visible dialogue → choose article mode
      → verify the repository read-only → you approve the Article contract
      → draft → four editing gates → output Markdown
```

Blogit pauses for confirmation at two points:

1. selecting the sessions to use;
2. approving the Article contract covering the title, thesis, evidence structure, scope boundaries, and dynamic length estimate.

This prevents the wrong history from being selected and avoids drafting a long article before its direction is settled.

When the client exposes a true native multi-select tool, Blogit uses that interface for session selection. It checks the tool's actual capabilities instead of assuming every desktop client supports multi-select. If only single-select or plain text interaction is available, it falls back to a numbered list rather than simulating checkboxes in Markdown.

## Installation

### Requirements

- Codex App, Codex CLI, or an IDE extension with Skills support;
- Python 3.10 or newer;
- local Codex or Claude session history.

Check your Python version:

```bash
python3 --version
```

If it is older than 3.10, install a newer version and make sure `python3` resolves to it. Blogit uses only the Python standard library and has no extra Python dependencies.

### Ask Codex to install it (recommended)

Send this prompt in Codex:

```text
Use $skill-installer to install Blogit from https://github.com/bugkiwi/blogit/tree/main/skills/blogit.
```

The installer downloads the repository into a temporary directory and installs only the runtime files under `skills/blogit`. It does not retain Git history, the repository README files, or tests. You can use `$blogit` in your next message after installation.

If Blogit does not appear in the Skills list, restart Codex. In Codex CLI or an IDE, you can also use `/skills` to confirm that it was discovered.

### Use Skills CLI

If you prefer command-line installation with easy update and removal, use the open-source [Skills CLI](https://github.com/vercel-labs/skills). It requires Node.js 18 or newer.

Install globally for the current user:

```bash
npx skills add bugkiwi/blogit --skill blogit --global --agent codex --yes
```

Update to the latest version:

```bash
npx skills update blogit --global --yes
```

Remove it:

```bash
npx skills remove blogit --global --yes
```

To enable it only for the current project, omit `--global`:

```bash
npx skills add bugkiwi/blogit --skill blogit --agent codex --yes
```

Skills CLI installs the actual Skill subdirectory, so these commands also exclude the repository README files, tests, and `.git` directory.

### Develop from local source

When modifying Blogit locally, use a symlink so changes take effect immediately:

```bash
git clone https://github.com/bugkiwi/blogit.git
cd blogit
mkdir -p "$HOME/.agents/skills"
ln -s "$(pwd)/skills/blogit" "$HOME/.agents/skills/blogit"
```

If the destination already exists, inspect whether it is an older installation or an existing symlink before deciding whether to replace it.

Codex discovers both user-level and project-level Skills and follows symlinks to Skill directories. See the [official Codex Skills documentation](https://learn.chatgpt.com/docs/build-skills#where-to-save-skills) for directory precedence.

## Usage

Mention `$blogit` directly and describe the article you want:

```text
Use $blogit to turn my recent Codex session about debugging cache invalidation into an English technical article.
Write for experienced backend engineers, estimate the length from the information density, and add any visuals that materially improve understanding.
```

Blogit can also find one shared thesis across multiple sessions:

```text
Use $blogit to turn my recent Claude sessions about retries and idempotency into one article.
First decide which sessions belong together; do not force unrelated work into the same story.
```

Even without an explicit `$blogit` mention, Codex can activate the Skill when the request clearly asks for a blog post, retrospective, or technical article grounded in recent Codex or Claude sessions.

## Complete example

The following interaction is illustrative. Session titles and IDs are examples only.

**You:**

```text
Use $blogit to write an English technical article about my recent work fixing duplicate charges.
The audience is backend engineers who build payment systems.
```

**Blogit:**

```text
Recent sessions:

1. Add idempotency keys         2026-07-12  payments-api
2. Debug duplicate charges      2026-07-11  payments-api
3. Update landing page          2026-07-10  marketing-site

Choose one or more numbers.
```

**You:**

```text
Use 1 and 2. Exclude 3.
```

**Blogit:**

```text
Title options:
1. The Duplicate Charge That Changed How I Think About Idempotency
2. A Retry Is Not Just Another Execution: Rebuilding a Payment API for Idempotency
3. From Duplicate Charges to Safe Replay: The Constraints I Added to a Payment API

Thesis: Reliable retries need more than an idempotency key. They require a stable
request identity, atomic writes, and explicit handling for in-progress requests.

Article mode: engineering method
Reader altitude: engineering retrospective / mechanism level
Title promise: explain how request identity, atomic writes, and intermediate states
combine to make payment requests safe to replay.
Primary evidence: duplicate charges, a race-condition failure, and replay tests
(verified read-only against implementation files and test names).
Scope exclusions: the full payment SDK architecture and unrelated operational workflows.
Claims needing verification: none.
Synthesis artifact: a safe-replay checklist.
Estimated length: about 1,600–2,200 words, derived from three mechanism-level sections,
two supporting sections, and the opening and synthesis. This is a forecast, not a cap.

Section plan:
1. [deep / ~300 words] Claim: duplicate charges expose unstable request identity;
   Evidence: incident record; New value: define the failure boundary;
   Takeaway: stabilize request identity first.
2. [deep / ~400 words] Claim: an idempotency record alone still races;
   Evidence: rejected design and tests; New value: explain the intermediate state;
   Takeaway: preserve in-progress semantics.
3. [deep / ~500 words] Claim: atomic writes prevent duplicate side effects;
   Evidence: implementation and race test; New value: establish the final mechanism;
   Takeaway: keep the record and business write inside one atomic boundary.
4. [supporting / ~300 words] Claim: replay testing verifies the repair;
   Evidence: test names and historical result; New value: complete verification;
   Takeaway: cover concurrent replay.
5. [supporting / ~250 words] Claim: the method transfers;
   Evidence: the verified mechanism above; New value: compress it into a checklist;
   Takeaway: reuse it for other write APIs.

Visual plan: a state flow for atomic writes and replay. Codex should prefer a generated
diagram; Claude should use a character flow diagram when no drawing tool is available.
Output: ~/Documents/blogit/payments-idempotency.md
```

**You:**

```text
Use title 2. The Article contract is approved.
```

Blogit then generates the article and returns its final title, file path, approximate length, and any material redactions or unverified claims.

Generated Markdown always begins with this structure, in this field order:

```yaml
---
title: xxx
date: YYYY-MM-DD
description: yyy
tags: [aaa, bbb, ]
slug: xxxxx
draft: true
---
```

Blogit replaces `xxx`, `yyy`, the tags, and the slug with article-specific values. `draft` remains the YAML boolean `true`. On macOS and Linux, the default output is `~/Documents/blogit/<slug>.md`; on Windows, it uses `blogit\<slug>.md` under the current user's known Documents folder. Generated images are stored under `assets/<slug>/` beside the article root and referenced with relative Markdown paths. Character diagrams stay inline inside fenced `text` blocks and do not create empty asset directories. A user-specified output directory always takes precedence.

## CLI commands

You normally do not need to run the parser directly; Codex follows `SKILL.md`. These commands are useful when diagnosing session discovery or parsing.

List the ten most recent Codex sessions:

```bash
python3 skills/blogit/scripts/blogit.py list --agent codex --limit 10
```

List the ten most recent Claude sessions:

```bash
python3 skills/blogit/scripts/blogit.py list --agent claude --limit 10
```

Extract visible dialogue from one or more sessions:

```bash
python3 skills/blogit/scripts/blogit.py extract \
  --agent codex \
  --session <session-id-1> \
  --session <session-id-2> \
  --output /tmp/blogit-transcript.md
```

Use `--home <path>` with either `list` or `extract` to override the default agent configuration directory.

## Privacy

Session history may contain code, internal URLs, account data, or other sensitive material. Blogit's parser reads local session files and filters system prompts, hidden reasoning, tool calls, tool results, and attachment placeholders. The writing workflow also removes credentials, tokens, private keys, personal contact details, internal URLs, and unrelated private information before analysis.

The parser does not send session content to search, image generation, or another third-party tool, and it does not mine tool results for so-called evidence hints. The writing workflow uses only the session's existing project path for targeted, read-only inspection of relevant files and Git history; it does not upload repository content. Technical claims that cannot be verified are softened or listed in the final handoff. Temporary transcript files are never included in the final response. Even with these safeguards, review the article and generated assets before publishing.

## Development and testing

```bash
python3 -m unittest discover -s tests -v
```

Repository structure:

```text
blogit/
├── README.md             # Default English documentation
├── README.zh-CN.md       # Simplified Chinese documentation
├── skills/blogit/          # Minimal installable Skill directory
│   ├── SKILL.md            # Core Skill workflow
│   ├── agents/openai.yaml  # Codex UI metadata
│   ├── scripts/            # Session discovery and extraction CLI
│   └── references/         # Writing and adapter guidance
└── tests/                  # Repository tests, not installed
```
