---
name: blogit
description: Turn one or more recent Codex or Claude agent sessions into a grounded, first-person Markdown article, with session discovery, privacy-aware transcript extraction, outline approval, natural-sounding drafting, and optional explanatory images. Use when the user asks to write, publish, recap, document, or make a blog post from agent/chat/session history, recent coding work, or past AI-assisted problem solving.
---

# Blogit

Convert recent agent work into an article that reads like lived experience rather than a transcript summary.

## Workflow

### 1. Discover sessions

Determine the current runtime and run:

```bash
python3 <skill-dir>/scripts/blogit.py list --agent codex --limit 10
python3 <skill-dir>/scripts/blogit.py list --agent claude --limit 10
```

Use `--agent auto` only when the runtime is uncertain. It detects Codex or Claude from environment variables. The list excludes the current session when its ID is available; add `--include-current` only when the user explicitly wants it.

Let the user choose one or more sessions; never choose for them. Prefer a client-native selection tool only when its available schema explicitly supports selecting multiple options in one prompt. Put the session title in each option label and its date and project in the description. If the tool limits options but supports several native multi-select questions in one invocation, split the ten sessions into the fewest clearly numbered batches and combine all selections.

Do not infer multi-select support merely because the runtime is a desktop app. Do not simulate it with HTML, Markdown checkboxes, or repeated single-select prompts. When no true native multi-select tool is available, show the ten results as a compact numbered text list with title, date, and project, then ask for one or more numbers. Accept a short optional note about intended audience, publication, tone, or desired length, but do not require it.

Pause for the user's selection.

### 2. Extract only the dialogue

Translate the selected numbers to their displayed session IDs, then run one extraction command per agent source:

```bash
python3 <skill-dir>/scripts/blogit.py extract \
  --agent codex \
  --session <id-1> --session <id-2> \
  --output /tmp/blogit-transcript.md
```

The parser retains only user and assistant visible text. It removes system/developer prompts, environment blocks, reasoning, tool calls, tool results, attachments, and transport events. Never substitute raw JSONL or broad file reads for the parser unless the parser reports an unsupported format.

Treat extracted history as sensitive local material. Before analysis, redact credentials, tokens, private keys, personal contact details, internal URLs, and unrelated private content. Do not upload or browse with transcript text. If a sensitive fact is essential to the story, generalize it and flag the change to the user.

### 3. Find the story

Read the extracted dialogue and identify:

- the central problem or question;
- the initial assumption and the evidence that changed it;
- the few decisions that materially affected the result;
- concrete proof: errors, measurements, constraints, code behavior, or outcomes;
- setbacks, tradeoffs, and unresolved uncertainty;
- one useful lesson the reader can apply elsewhere.

Prefer one strong thesis over a chronological inventory. Combine multiple sessions only when they support the same thesis; otherwise propose separate articles.

Do not turn assistant claims into facts merely because they appear in the transcript. Distinguish observed results from suggestions, and omit claims that the dialogue never verifies.

### 4. Propose the outline

Present:

1. two or three non-clickbait title options;
2. a one-sentence thesis;
3. the intended reader and promised value;
4. a section outline, with the evidence or scene used in each section;
5. an image plan: `none` or the purpose and placement of each necessary image;
6. the proposed output path.

Default to a focused 1,200–2,000 word article. Resolve the output root in this order:

1. a directory explicitly named by the user;
2. `~/Documents/blogit` on macOS or Linux;
3. the user's Windows Documents known folder plus `blogit`, obtained with `[Environment]::GetFolderPath('MyDocuments')`; fall back to `%USERPROFILE%\Documents\blogit` only when the known folder cannot be resolved.

Propose `<output-root>/<descriptive-slug>.md`, with `~` and environment variables expanded before file operations. If the chosen root is outside the current writable scope, request narrowly scoped permission before drafting; if permission is unavailable, ask the user for a writable directory instead of silently changing the destination. Do not create the article or asset directories until the outline is approved.

Pause for outline approval. Do not draft the full article before approval. Apply requested changes and confirm again when they substantially alter the thesis or structure.

### 5. Draft in first person

Read [references/writing.md](references/writing.md) before drafting.

Write from the author's first-person perspective (`I` in English, `我` in Chinese). Reconstruct a coherent problem-solving narrative instead of replaying alternating chat turns. Preserve exact technical details that carry the lesson, but remove operational noise.

Match the user's language unless asked otherwise. Match their vocabulary and level of directness from the selected sessions without imitating typos or exposing private speech. Never invent feelings, quotations, chronology, success, or certainty.

Every article file must start at the first byte with this YAML frontmatter, using this exact field order and shape:

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

Replace the placeholders with the approved title, the current local date, a concise one-sentence description, two to five specific tags, and the descriptive slug. Keep `draft: true` as a YAML boolean. Make `slug` lowercase hyphen-case and keep it identical to the Markdown filename stem and the article's asset-directory name. Quote YAML string values when needed to preserve punctuation or avoid implicit scalar types. After the frontmatter, write ordinary Markdown; do not repeat the title as an H1 unless the user's publishing convention requires it.

### 6. Generate images only when they teach

Generate an image only when it explains a relationship that prose or a small code sample cannot explain as clearly—for example an architecture, state transition, before/after comparison, or conceptual model. Skip generic hero art and decorative stock imagery.

When an image is approved in the outline:

1. use an available image-generation or diagram tool;
2. save it under `<output-root>/assets/<article-slug>/`;
3. use a stable lowercase filename;
4. embed it as `assets/<article-slug>/<filename>` with meaningful alt text;
5. add a short caption when the interpretation is not obvious.

Create the asset directory only when it will contain an approved image. If no image tool is available, insert a clearly marked image brief rather than fabricating a path.

### 7. Perform the final pass

Verify that:

- the opening starts with a concrete tension, observation, or decision;
- every section advances the thesis;
- first-person claims are supported by the selected dialogue;
- code, commands, names, and results are accurate;
- secrets and irrelevant personal details are absent;
- the required frontmatter is the first content in the file, uses the specified field order, and contains no placeholders;
- `date` is a valid `YYYY-MM-DD`, `draft` is the boolean `true`, and `slug` matches the filename stem;
- links and image paths resolve;
- article assets stay under `<output-root>/assets/<slug>/` and use relative paths;
- no conversation scaffolding, tool chatter, or AI self-reference remains;
- the ending gives a specific earned insight instead of a generic recap.

Return the article path, final title, approximate word count, and any material redactions or unverified claims. Do not include the extracted transcript in the final response.

## Parser failures

If discovery finds no sessions, report the checked config directory and suggest an explicit `--agent` or `--home`. If extraction finds an ambiguous ID, use the full ID shown by `list`. If the local format has changed, inspect only a few record keys—not private content—and follow [references/adapters.md](references/adapters.md) to update or add an adapter.
