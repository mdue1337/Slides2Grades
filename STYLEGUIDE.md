# Styleguide for LLM-Generated Content

## Vault Structure
- Level 1: Course Name (under a semester folder, e.g. `3. Semester/`)
- Level 1 files: `Begreber.md` — one glossary for the whole course, capital B
- Level 1 folders: `Literature/`, `Images/`
- Level 2: `Week N/` folders
- Level 2 files: `<NN - Title>.md` — the topic note itself
- Level 2 folders: `<NN - Title>/` — sibling folder holding `transcript_raw.md`
- Level 3: `exercises.md`, `exam_questions.md`, `flashcards.md`, each created
  by the skill that writes it, on first run

`Begreber.md` is deliberately course-level, not topic-level: a glossary split
across topic folders cannot be reviewed as a set, which is the only thing a
glossary is for.

Course and week folders are created by hand. `makenotes.sh` is
deprecated and lives in `deprecated/`.

## Format Rules
- Use markdown headers (# ## ###)
- Bold for key terms: **concept**
- Bullet points for lists
- LaTeX for maths, preserved verbatim: `$A \cap B$`, `$\bigcup_{i=1}^{n} A_i$`
- Fenced code blocks for code
- No inline HTML
- UTF-8 encoding required
- Obsidian wikilinks for cross-topic references: `[[NN - Title]]`

## Note level

The target shape for a topic note. `cleanup` enforces it; every other skill
should avoid writing content that violates it.

A note is a reference surface used **while doing exercises**, and it is
searched in Obsidian. It is not a textbook. Short and scannable beats
complete.

**Keep, compressed:**
- Definitions
- Formulas, in LaTeX, verbatim
- Conditions of use (`kræver a ≠ 1`, `kræver P(B) > 0`)
- Traps and warnings
- Exam advice
- Named book examples, reduced to bare computations — setup, numbers, answer,
  no narration

**Delete outright:**
- Motivation and narrative prose
- Historical background
- Lecturer asides and course logistics
- Proof prose and proof sketches
- Any restatement of something already stated elsewhere in the same file
- Filler and transitional sentences

**A one-line "why/when"** is allowed where a formula needs a hook. Not on
every line. If the line does not change how the formula is used, cut it.

**Never touch:** image embeds (`![[...]]`), wikilinks, or the note's language.

**Never invent a heading scheme.** This covers `**Bold**` structural labels as
well as `#` headings — keep the note's own.

## Content Quality Standards
- **Density**: essential information, no bloat
- **Hierarchical Organization**: big idea → supporting details → examples
- **Retrievability**: findable and scannable

## For Each Skill

### Cleanup (note level + glossary)
- Phase 1 rewrites the topic note to the **Note level** standard above.
  Destructive; git is the undo.
- Phase 2 rebuilds the course glossary per **Begreber (course glossary)**
  below. Cleanup performs this itself — it never invokes another skill.
- The skill's own operational rules (merging, marker stripping, mixed-language
  handling, idempotence) live in `.claude/skills/cleanup/SKILL.md`.

### Lecture-Enhance (Audio Transcription Enhancement)
- Extract high-density statements (facts, definitions, key relationships)
- Ignore filler and repetition
- Link new content to existing notes with [[wikilinks]]
- Preserve original note structure when adding
- Format: append to the topic note, clearly marked as `[FROM LECTURE]`.
  `cleanup` is the follow-up pass that strips those markers.

### Slides-Enhance (Slide + Notes Comparison)
- Add visual concepts that text notes miss
- Fill gaps between your notes and slide content
- Flag contradictions or updates using Obsidian callouts:
  `> [!CAUTION]` for contradictions, `> [!INFO]` for updates/clarifications
- Preserve existing note structure

### Review-Notes (Exam Preparation)
- Vary question formats: definition, application, synthesis
- Include difficulty level: [Easy], [Medium], [Hard]
- Include topic tags: #topic-name
- Format:

```
## Question [Difficulty] #tags
**Format**: [Multiple Choice / Short Answer / Essay]
**Q**: [Question]
**Suggested Answer**: [Answer]
```

### Begreber (course glossary)
- Target is the **course-level** `Begreber.md`, never a per-topic file
- Created with a `# Begreber — <Course>` header if it does not exist
- One line per term: `**Term** — definition. Why, only when it earns it.`
- Provenance comes from the section heading, which is itself a wikilink:
  `## [[NN - Title]]`. No per-entry `Source` line.
- Topic sections ordered by the note's leading number (`01`, `02`, …). A note
  without a leading number sorts after the numbered ones, by filename.
- Within a section, terms in **order of first appearance in the note** — not
  alphabetical.
- A term defined in more than one note gets **one** entry, under the note that
  defines it first. Check every section for it, including near-duplicates.
- Definitions in own-words prose, never the textbook's phrasing. LaTeX
  preserved. Same language as the source note.
- Omit the "why" clause rather than padding it.
- **Derived, not accumulated:** for each topic processed, delete any existing
  content for that topic — new-format section, old-format `## Topic` section,
  or scattered legacy entries — and rebuild it from the note. Never migrate.
  Sections for topics not being processed are left byte-for-byte alone, and
  are read only for cross-topic deduplication.

Example:

```
# Begreber — Introduktion til sandsynlighedsteori og statistik

## [[01 - Mængder, Kardinalitet]]
**Udfaldsrum (S)** — alle mulige udfald; alt andet er delmængder af S.
**Disjunkte** — $A \cap B = \emptyset$. Forudsætning for aksiom 3.
```

## Flashcards Format
- Use: `Question | Answer` format
- One per line for easy parsing
- Include difficulty metadata: `[Easy/Medium/Hard] Question | Answer`
