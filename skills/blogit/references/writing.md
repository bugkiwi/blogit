# Writing guide

Use this guide during outlining and drafting, not during session discovery.

## Narrative shape

Build the article around a change in understanding:

1. **Situation:** Open inside a specific constraint, surprise, failure, or question.
2. **Pressure:** Explain why the obvious approach was insufficient.
3. **Investigation:** Select only the experiments and evidence that moved the work forward.
4. **Turn:** Show the decision or realization that reorganized the problem.
5. **Result:** State what changed, including limits and remaining uncertainty.
6. **Transfer:** End with a precise principle the reader can reuse.

This is a shape, not a required six-heading template. Merge or omit stages to suit the material.

Apply this arc to the article, not as a miniature template inside every section. Preserve negative space: a rejected approach, false green, tradeoff, or still-unresolved issue may end without a neat lesson. Reserve the synthesized Transfer for the ending; a section's planned reader takeaway is an editorial check, not a required closing maxim.

## First-person truthfulness

- Use first person for actions, judgments, and lessons supported by the history.
- Attribute tool or agent discoveries naturally: “The trace showed…” or “When I inspected…” rather than pretending unaided recall.
- Do not claim an implementation shipped when the record shows only a proposal or local change.
- Do not invent emotions. “I was frustrated” needs evidence; “The mismatch was easy to miss” usually does not.
- Paraphrase dialogue. Use quotation marks only for short, exact, consequential wording present in the source.
- Keep uncertainty visible when it shaped the decision.

For at least one important wrong assumption when the source contains one, explain what I believed, why it was reasonable at the time, what evidence disproved it, and how the new model changed the implementation. Prefer a change in reasoning over invented drama.

## Evidence hierarchy

Prefer, in order:

1. repository files, test definitions and recorded results, measurements, and final artifacts anchored to the relevant worktree, commit, date, or release;
2. explicit user constraints and decisions;
3. results explicitly confirmed by both user and assistant;
4. assistant-only statements, clearly labeled as hypotheses until independently verified.

Never claim a final implementation, correct approach, or shipped result from an assistant turn alone. Omit unsupported specifics. When external research would materially improve the article, ask before browsing because transcript or repository material must not become a search query.

For coverage, test counts, benchmarks, costs, or multipliers, preserve the available date or commit, measured package or component, source anchor, environment, sample count, cache and network state, measurement boundaries, and whether the value is a mean, median, best run, or representative snapshot. If important context is missing, round or remove the value and label what remains as a historical or illustrative snapshot instead of presenting false precision.

## Evidence and density budget

- Use at most three primary evidence scenes by default; compress supporting incidents into short corroboration.
- Use at most three deep sections. Give each section one main claim and one internal reader takeaway; do not turn every takeaway into an explicit principle paragraph.
- Introduce only the terms required to understand the section's claim. Define a necessary unfamiliar term where it first matters.
- Remove a case when it repeats an earlier proof, adds more terminology than reusable insight, or mainly records completed work.
- Treat the approved length and per-section allocations as ceilings, not space to fill.

## Remove the AI aftertaste

- Start with substance, not “In today's rapidly evolving world.”
- Prefer concrete nouns and verbs to inflated adjectives.
- Vary sentence length. Let an important short sentence stand alone.
- Use headings that make claims or mark turns, not repetitive labels such as “Background,” “Analysis,” and “Conclusion.”
- Avoid mechanical signposts: “firstly,” “secondly,” “last but not least,” “it is worth noting,” and their Chinese equivalents.
- Avoid repeated contrast templates such as “not only X, but also Y.”
- Delete throat-clearing, duplicate summaries, and conclusions that merely restate every section.
- Keep a few telling constraints, failed attempts, and corrections. Perfect linear progress sounds false.
- Do not mention prompts, tokens, agents, or “the conversation” unless AI-assisted work is itself the article's subject.
- Do not append generic “future outlook” sections without evidence.

Run a cadence audit for repeated rhetorical frames, including `不是……而是……`, `不只是……`, `看起来……实际上……`, `这让我……`, `我确认了一件事……`, `真正的……是……`, `最终我……`, `X 从来不是……`, and their English equivalents. Allow no more than two uses of the same frame in the full article. Use the complete `problem → fix → principle` rhythm in at most two sections; let other sections end on evidence, tradeoff, or uncertainty.

## Technical material

- Include a code block only when the reader needs exact syntax or when a small before/after proves the point.
- Trim imports, setup, logs, and generated output not relevant to the argument.
- Explain why a technical detail matters immediately before or after it.
- Give each important number a safe, reproducible anchor such as a test, fixture, script, table note, commit, or dated measurement; otherwise weaken or remove the number.
- Use tables only for true comparisons across repeated fields.
- Prefer a diagram when three or more components or states interact and prose becomes hard to follow.
- When the thesis has three or more layers, components, states, or decision criteria, include one reusable synthesis artifact such as a comparison table, checklist, decision tree, layered diagram, or compact framework summary. Introduce it before or near the first detailed case and complete it near the end.

## Language

In Chinese, prefer direct contemporary prose. Use `我` naturally, avoid dense strings of four-character slogans, and replace vague phrases such as “赋能、沉淀、抓手、闭环” unless they are the author's normal domain vocabulary. Default to 1,800–3,000 Chinese characters, excluding frontmatter and code.

In English, prefer contractions when they match the author, avoid corporate filler, and use active voice without forcing every sentence into the same cadence. Default to 1,000–1,600 words, excluding frontmatter and code.

## Final edit

Apply the structural, compression, voice, and verification passes from `SKILL.md`. Each pass may rewrite the draft. Cut any paragraph whose removal does not weaken the thesis, evidence, or reader understanding.
