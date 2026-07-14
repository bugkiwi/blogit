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

Read [references/writing.md](references/writing.md) before analyzing the story, building the article contract, or drafting.

Choose one primary article mode before outlining:

- incident retrospective;
- engineering method;
- concept explanation;
- benchmark or comparison;
- implementation walkthrough;
- opinion supported by evidence.

Other modes may provide evidence, but they must not compete for the article's structure.

Read the extracted dialogue and identify:

- the central problem or question;
- the initial assumption and the evidence that changed it;
- the few decisions that materially affected the result;
- concrete proof: errors, measurements, constraints, code behavior, or outcomes;
- setbacks, tradeoffs, and unresolved uncertainty;
- one useful lesson the reader can apply elsewhere.

Prefer one strong thesis over a chronological inventory. Combine multiple sessions only when they support the same thesis; otherwise propose separate articles.

Do not turn assistant claims into facts merely because they appear in the transcript. Distinguish observed results from suggestions, and omit claims that the dialogue never verifies.

Select primary evidence scenes by distinct contribution, not by a numeric cap. Keep every scene needed to establish a different claim, reasoning change, boundary, or reusable lesson. Compress or remove a scene when another proves substantially the same point, removing it does not weaken the thesis, it introduces more concepts than reusable insight, or it mainly demonstrates how much work was completed. When many scenes support one thesis, group them under a clear framework; when they support competing theses, propose separate articles.

### 4. Verify falsifiable technical claims

Before proposing the article contract, create an internal claims ledger for statements about the final or current mechanism, API and package names, tests and coverage, measurements and costs, and shipped or deployed status.

Use each selected session's displayed project path to inspect only the relevant repository, read-only. Capture the current commit and worktree status, then use targeted file reads, search, test names, manifests, and `git log` or `git show` when history matters. Do not modify the repository, run broad scans, upload repository content, or browse with it. Never treat an uncommitted worktree as proof that something shipped.

For each claim, record a safe source anchor and mark it `verified-current`, `verified-historical`, `conflicting`, or `unverified`. Apply these rules:

- let the current repository override dialogue summaries for present-tense or final-implementation claims;
- anchor historical claims to the relevant date, commit, test, or artifact instead of judging them only from today's code;
- describe rejected and intermediate designs as evolution, never as the final answer;
- treat assistant-only statements as hypotheses, even when they sound conclusive;
- treat a test definition as proof that the test exists, not that it passed, and repository code as proof of implementation, not deployment; require a recorded result, release, deployment artifact, or explicit user confirmation for the stronger claim;
- when the repository is unavailable or evidence remains ambiguous, soften or omit the claim and keep it in `claims needing verification`.

Do not expose private paths or repository details in the article contract. Show only material verification gaps that affect the proposed scope or title.

### 5. Propose the article contract

Present:

1. two or three non-clickbait title options;
2. the primary article mode;
3. the primary reader stance—engineering retrospective, product or stakeholder observer, open-source adoption, or a clearly named user-specific equivalent—plus the technical altitude: concept, mechanism, or reproducible troubleshooting;
4. the title promise, one-sentence thesis, intended reader, and promised value;
5. what the reader must understand within the first 20% of the article;
6. the necessary primary evidence scenes with verification status and safe anchors, supporting evidence to compress, explicit scope exclusions, and material claims needing verification;
7. a section plan whose entries each state `deep` or `supporting`, the claim, evidence and anchor, new value over the previous section, reader takeaway, and estimated space;
8. a synthesis artifact—table, checklist, decision tree, layered diagram, compact framework summary, or `none`;
9. a visual plan: `none` or each visual's purpose, placement, preferred format, and fallback format;
10. a bottom-up estimated length range with a short rationale, plus the proposed output path.

Require a synthesis artifact when the thesis contains three or more layers, components, states, or decision criteria. Introduce the framework before or near the first detailed case, then return to its completed form near the end.

Choose the number and depth of sections from the amount of distinct, verified information the thesis requires. Estimate length bottom-up from the context, mechanism, evidence, transitions, and synthesis each section needs. Present the estimate as a range, not a limit or target. Do not compress unique evidence to fit a preset size, and do not pad sparse material to reach one. When the user supplies a hard limit, reduce scope transparently or propose multiple articles rather than squeezing every selected session into it.

Resolve the output root in this order:

1. a directory explicitly named by the user;
2. `~/Documents/blogit` on macOS or Linux;
3. the user's Windows Documents known folder plus `blogit`, obtained with `[Environment]::GetFolderPath('MyDocuments')`; fall back to `%USERPROFILE%\Documents\blogit` only when the known folder cannot be resolved.

Propose `<output-root>/<descriptive-slug>.md`, with `~` and environment variables expanded before file operations. If the chosen root is outside the current writable scope, request narrowly scoped permission before drafting; if permission is unavailable, ask the user for a writable directory instead of silently changing the destination. Do not create the article or asset directories until the article contract is approved.

Pause for article-contract approval. Do not draft the full article before approval. Apply requested changes and confirm again when they substantially alter the thesis, scope, or structure.

### 6. Draft in first person

Make the author the sole narrator. Write from the author's first-person perspective (`I` in English, `我` in Chinese) and never reveal or adopt an AI, assistant, agent, model, chat, session, prompt, or tool-process perspective. Do not write phrases such as “the assistant suggested,” “the agent found,” “the conversation showed,” or “we discovered” when `we` means the author plus AI. Use `we` only for an explicitly established human team supported by the source.

When an insight originated in assistant text or tool activity, verify it independently and express it through the author's reasoning or the evidence itself—for example, “I changed my model after…,” “the trace showed…,” or “the test failed at…”. Never invent an action for the author merely to hide the AI source; use an evidence-led construction or omit the claim when authorship is unsupported. Codex, Claude, or another AI may appear only as an object the author used, evaluated, or discussed when it is genuinely part of the article's subject; it must never become the narrator or co-authorial voice.

Reconstruct a coherent problem-solving narrative instead of replaying alternating chat turns. Preserve exact technical details that carry the lesson, but remove operational noise.

Match the user's language unless asked otherwise. Match their vocabulary and level of directness from the selected sessions without imitating typos or exposing private speech. Never invent feelings, quotations, chronology, success, or certainty.

In the opening section, establish the concrete tension and deliver every applicable part of the article contract: define an unfamiliar project or system, define the key term in operational language, and state or preview the organizing framework before the detailed cases begin. Give this orientation as much space as the system's unfamiliarity requires; do not impose a fixed character or word cap.

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

### 7. Add visuals when they improve understanding

During the article contract, inspect frameworks, state changes, timelines, comparisons, and multi-component interactions for useful visual treatment. Add visuals where they materially reduce cognitive load, make a reusable framework easier to scan, or clarify a sequence that prose handles poorly. Skip generic hero art and decorative filler.

Resolve visual capability at runtime:

1. In Codex, use the available native image-generation skill or tool for an approved raster illustration, and prefer a structured diagram format or renderer for flows and architecture when it produces a portable result.
2. In Claude, first inspect the available tools and skills for real image-generation or diagram capability and use it when present.
3. In any runtime without drawing capability, render conceptual flows, frameworks, state machines, and comparisons as a concise ASCII or Unicode character diagram inside a fenced `text` block. Use plain ASCII when portability is uncertain and verify labels and alignment in monospace.
4. Use an image brief only when the visual truly requires raster artwork and a character diagram cannot carry the intended meaning; never fabricate an asset path.

For generated visual assets, save them under `<output-root>/assets/<article-slug>/`, use a stable lowercase filename, embed them as `assets/<article-slug>/<filename>` with meaningful alt text, and add a short caption when interpretation is not obvious. Create the asset directory only when it will contain an actual file; character diagrams remain inline and need no asset directory. Give any external visual tool only a generalized, redacted brief—never transcript text, repository content, secrets, or private identifiers.

### 8. Edit through pass/fail gates

Run four separate editing passes. Each pass may rewrite or remove material; do not merely report that it passed. When a gate fails or remains uncertain, revise the draft and rerun the affected pass before writing or reporting the final article.

**Structural pass**

- Extract the important claims and nouns from the title. Verify that each is defined, appears in the thesis, receives sufficient evidence, and is resolved by the conclusion; otherwise narrow the title or deliberately expand the article contract.
- Verify that the primary article mode, reader stance, and technical altitude control the structure, the opening delivers its contract, and any required synthesis artifact appears early enough to organize the cases.
- Verify that every section adds unique value. Remove any section whose absence does not weaken the thesis, evidence, or reader understanding.

**Compression pass**

- Compare the draft with the estimated range and section estimates as diagnostics, not quotas. If distinct, necessary material makes the draft longer, update the estimate instead of deleting useful evidence; if it is shorter, do not pad it.
- Remove or collapse secondary incidents, repeated explanations, and terminology that does not support the section's claim.
- Keep every primary scene and deep section that adds distinct value; merge or remove only redundant material or content belonging to another thesis.

**Voice pass**

- Apply the cadence audit in [references/writing.md](references/writing.md) and rewrite repeated rhetorical frames.
- Fail the pass if any sentence exposes an assistant, agent, model, session, prompt, conversation, or tool-process viewpoint. Rewrite it in the author's voice or remove it; verify that every claimed first-person action belongs to the author.
- Reject `we` when it implies an author–AI partnership. Keep it only for a source-supported human team.
- Preserve at least one supported change in reasoning when the source contains one, including why the earlier assumption was reasonable.
- Keep the full `problem → fix → principle` pattern in at most two sections. Preserve a failed path, rejected design, false green, tradeoff, or unresolved point when the source supports one.
- Remove polished but generic aphorisms, conversation scaffolding, tool chatter, and irrelevant AI self-reference.

**Verification pass**

- Recheck every falsifiable claim against the claims ledger. Ensure the described final mechanism matches the current repository or is explicitly historical, and ensure no rejected design appears as the final answer.
- Give coverage, test counts, durations, costs, and multipliers a date or commit, measured package or scope, snapshot status, and a safe source anchor. Remove or soften numbers that lack this context.
- Verify first-person claims, technical facts, code, commands, names, measurements, and benchmark context against the selected dialogue and repository evidence.
- Remove secrets and irrelevant personal details; label material uncertainty rather than smoothing it over.
- Preserve unresolved entries in `claims needing verification`; never silently upgrade them during editing.
- Verify that the required frontmatter is first, ordered correctly, and contains no placeholders; `date` is `YYYY-MM-DD`, `draft` is the boolean `true`, and `slug` matches the filename stem.
- Resolve every link and image path. Keep article assets under `<output-root>/assets/<slug>/` and use relative paths; verify inline character diagrams remain aligned and understandable without client-specific rendering.
- End with a specific earned insight instead of a generic recap.

Use pass/fail judgments, not numeric self-scores. Do not expose the internal audit unless the user asks. Return the article path, final title, approximate Chinese-character or English-word count, and a concise verification summary of repository or historical anchors checked, claims still unverified, and material redactions or generalizations. Do not expose sensitive paths or include the extracted transcript in the final response.

## Parser failures

If discovery finds no sessions, report the checked config directory and suggest an explicit `--agent` or `--home`. If extraction finds an ambiguous ID, use the full ID shown by `list`. If the local format has changed, inspect only a few record keys—not private content—and follow [references/adapters.md](references/adapters.md) to update or add an adapter.
