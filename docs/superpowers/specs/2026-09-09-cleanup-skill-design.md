# Design: `cleanup` skill, replacing `grill-notes`

**Date:** 2026-09-09
**Status:** Approved for planning

## Problem

`grill-notes` has never been run. Neither have `review-notes` or
`flashcards-make` — no `exercises.md`, `exam_questions.md`, or
`flashcards.md` exists anywhere in the vault. Only `lecture-enhance` and
`begreber-extract` have produced output on disk.

Meanwhile the notes have the opposite problem from the one the skill set
was built for. `lecture-enhance` and `slides-enhance` append; nothing ever
removes. A note that started at 6 KB is now 18 KB of narrative — motivation,
history, proof prose, lecturer asides. The user reads notes *while doing
exercises*, and searches them in Obsidian. For that job the notes need to be
short: formulas, definitions, conditions of use, and the traps. Prose is
overhead.

`begreber-extract` has the same disease in a different form: five lines per
term, 157 lines for one course. A glossary is a lookup surface; density is
its entire value.

Separately, `begreber-extract` is easy to forget, because it is a separate
manual step with no natural trigger.

## Decisions

| Decision | Choice | Why |
|---|---|---|
| What replaces `grill-notes` | A `cleanup` skill that rewrites a note down to note level | The unmet need is subtraction, not more generated artifacts |
| Note shape | Terse, worked examples kept as stripped computations, plus a one-line "why/when" where a formula earns it | Notes are a reference surface for exercises, not a textbook |
| Narrative prose | Deleted outright | Recoverable from the textbook and lecture video; not worth file weight |
| Math notation | LaTeX preserved verbatim | Obsidian renders it, and `\bigcup_{i=1}^{n}` has no clean unicode form |
| Safety | Rewrite in place; `git` is the undo | Vault is a git repo; extra gating slows the loop for no real gain |
| Restructuring | May merge duplicates and move a line under a better-fitting **existing** heading | Duplication across sections is the largest single source of bloat |
| Heading scheme | Never invented or replaced | Notes mirror the textbook's section numbering; that is worth keeping |
| Glossary entry format | One line per term, `## [[Topic]]` heading carries provenance | Matches the user's own hand-written HCI glossary; ~5× denser than current |
| Glossary writes | Derived, not accumulated — rebuild the topic's section each run | Existing extractions were judged not useful; a rebuild beats a migration |
| Glossary trigger | `cleanup` performs the glossary step itself | Removes the "I forget to run it" failure mode |
| Skill wiring | Two skills, shared rules in `STYLEGUIDE.md` | Matches the repo's existing pattern; no skill-chaining, which the repo forbids |
| Skill roster | Delete `grill-notes` only | `review-notes` and `flashcards-make` are exam-time tools; it is not exam time |
| `[FROM LECTURE]` markers | `lecture-enhance` keeps emitting; `cleanup` strips | Markers are a review aid between the two passes, not permanent metadata |
| `scripts/makenotes.sh` | Moved to `deprecated/` | Never used; folders are made by hand and that convention is staying |

## The `cleanup` skill

New file: `.claude/skills/cleanup/SKILL.md`.

### Frontmatter

```yaml
name: cleanup
description: Rewrite a topic's note down to note level — terse definitions,
  formulas, conditions and stripped worked examples — then refresh the course
  glossary. Destructive; git is the undo. Use after lecture-enhance or
  slides-enhance has bloated a note.
```

### Inputs

- The topic note. Course and topic come from the skill arguments; if not
  supplied, ask. Accepts more than one topic in a single invocation.
- `<Course>/Begreber.md` — the glossary target, created if absent.

Resolve `<vault>` via `python3 scripts/config.py VAULT_PATH` from the repo
root, per the config seam.

Vault layout is `<vault>/<Course>/Week N/<NN - Title>.md`, with transcripts in
a sibling `<NN - Title>/` folder. The glossary is `<vault>/<Course>/Begreber.md`.

### Phase 1 — clean the note

**Delete outright:**

- Motivation and narrative prose ("the idea is due to Kolmogorov; in real
  experiments S is hopelessly complicated…")
- Historical background
- Lecturer asides, exam advice, and course logistics
- Proof prose and bevisskitser
- Any restatement of something already stated elsewhere in the file
- Filler and transitional sentences

**Keep, compressed:**

- Definitions
- Formulas, in LaTeX, verbatim
- Conditions of use (`kræver a ≠ 1`, `kræver P(B) > 0`)
- Traps and warnings (the POF, the `+1` in `365 - k + 1`)
- Named book examples, reduced to bare computations with no narration —
  the setup, the numbers, the answer

**A one-line "why/when" is allowed** where a formula genuinely needs a hook.
Not on every line. If the line does not change how the formula is used, cut it.

**Merging.** Content stated twice in one file collapses to one entry. The
surviving entry may move under whichever *existing* heading fits best.
Cleanup never invents a heading scheme and never replaces the note's
section numbering.

**Strip `[FROM LECTURE]` markers.**

**Never touch:**

- Image embeds (`![[Pasted image 20260824110110.png]]`)
- Wikilinks
- The note's language — a Danish note stays Danish, an English note stays
  English

**Idempotence.** On a note already at note level, report "already at note
level" and write nothing. Re-running must not keep shrinking a note.

**Scope note.** The rules do not distinguish hand-written prose from
transcript-derived prose. Hand-written narrative is deleted on the same
terms as any other narrative.

### Phase 2 — refresh the glossary

Performed by `cleanup` directly. It does **not** invoke `begreber-extract`;
the repo forbids skill auto-chaining.

Rules live in `STYLEGUIDE.md` and are not restated in the skill.

### Output

Write the cleaned note back in place. Write `Begreber.md` back in place.
Report, per note: rough before/after size, what categories were cut, and
which glossary terms were added.

## Glossary format

Target: `<Course>/Begreber.md`.

```markdown
# Begreber — <Course>

## [[01 - Mængder, Kardinalitet]]
**Udfaldsrum (S)** — alle mulige udfald; alt andet er delmængder af S.
**Hændelse** — delmængde af S. Gør SS-regning til mængdelære: ∪/∩/ᶜ = eller/og/ikke.
**Disjunkte** — $A \cap B = \emptyset$. Forudsætning for aksiom 3.
```

Rules:

1. One line per term: `**Term** — definition. Why, only when it earns it.`
2. Provenance comes from the `## [[<NN - Title>]]` section heading. No
   per-entry `Source` line.
3. Topic sections ordered by the note's leading number (`01`, `02`, …). A
   note without a leading number sorts after the numbered ones, by filename.
4. Within a section, terms in **order of first appearance in the note** —
   not alphabetical.
5. A term defined in more than one note gets **one** entry, under the note
   that defines it first. Before adding a term, check every section of the
   file for it, including near-duplicates.
6. Definitions in the user's own words, never the textbook's phrasing.
   LaTeX preserved.
7. Definitions in the source note's language.

**Write semantics — derived, not accumulated.** For each topic the run
processes, any existing content for that topic — whether a `## [[Topic]]`
section, an old-format `## Topic` section, or scattered legacy entries
naming it — is **deleted and rebuilt** from the cleaned note. Nothing is
migrated. Sections belonging to topics the run is not processing are left
byte-for-byte alone, and are read only to avoid defining a term twice
across topics.

Consequence: running `cleanup` across every topic of a course in one
invocation rebuilds the whole glossary coherently in one pass. That is the
recommended first use.

Consequence: the hand-written HCI `Begreber.md` — with its `# Core` /
`# Interaction` theme headings and deliberate non-alphabetical ordering —
will be restructured into per-topic sections when its topics are cleaned.
This is accepted; `git` is the undo.

## `STYLEGUIDE.md` changes

`STYLEGUIDE.md` remains the authoritative formatting source that skills
point at rather than duplicate. Five edits:

1. **Vault Structure** — replace the `Level 2: Topic` / `Level 3: notes.md`
   description with the real layout: `<Course>/Week N/<NN - Title>.md`, a
   sibling `<NN - Title>/` folder for `transcript_raw.md`, `Literature/`,
   `Images/`, and course-level `Begreber.md` (capital B).
2. **"Notes Clarity"** — currently reads *"Concept Clarity: explain as if for
   someone unfamiliar with the topic."* That rule produced the bloat.
   Replace with a **Note level** standard stating the Phase 1 target shape.
   This is the section `cleanup` points at.
3. **Delete the Grill-Notes section.**
4. **Rewrite the Begreber-Extract section** to the format above.
5. **Add a Cleanup section.**

## `begreber-extract` changes

Kept as a standalone skill, for refreshing the glossary without a
destructive note rewrite.

- Points at `STYLEGUIDE.md` for the format; does not restate it.
- Switches from append-only to derive-and-rewrite, matching Phase 2.
- Target corrected from `begreber.md` to `Begreber.md`.
- Description updated to say it is also run automatically as `cleanup`'s
  second phase.

## Ripple

**Deleted:** `.claude/skills/grill-notes/`.

**`CLAUDE.md`:**

- Skill table: swap the `grill-notes` row for `cleanup`; update the
  `begreber-extract` row. Still six skills.
- Split the hard rule. It currently reads *"All writes are append/annotate,
  never a rewrite of existing content — this is a hard rule across all six
  skills."* It stays true for `lecture-enhance`, `slides-enhance`,
  `review-notes`, and `flashcards-make`, and is explicitly false for
  `cleanup` and `begreber-extract`, which rewrite by design with `git` as
  the undo.
- Fix `begreber.md` → `Begreber.md` throughout.
- Rewrite the `makenotes.sh` architecture paragraph to record that it is
  deprecated and that folders are created by hand.

**`README.md`:**

- Workflow table: drop the `grill-notes` row, add `cleanup`, add the missing
  `begreber-extract` row, and mark `makenotes.sh` deprecated. The table
  currently claims `makenotes.sh` scaffolds
  `{notes,exercises,exam_questions,flashcards}.md`, which is wrong on two
  counts — fix it while there.
- Update the test-running section to match the moved bash test.

**`lecture-enhance/SKILL.md`:** behaviour unchanged — it keeps emitting
`[FROM LECTURE]`. Add one line noting `cleanup` is the follow-up pass that
strips them.

**`scripts/makenotes.sh` → `deprecated/makenotes.sh`**, with
`tests/test_makenotes.sh` → `deprecated/test_makenotes.sh` and its path
reference updated so it still runs if invoked. The lowercase `begreber.md`
stub it creates is left as-is; deprecation makes the bug unreachable.

## Verification

Per `CLAUDE.md`, skill changes are verified by walking the SKILL.md's own
instructions against fixture data rather than invoking the Skill tool,
because project skills created or modified mid-session may not be
discoverable.

- Add `tests/fixtures/sample_topic/notes_bloated.md` — a deliberately
  over-written version of the existing binary-search-tree note, carrying one
  instance of each category cleanup is meant to delete (motivation, history,
  proof prose, an aside, a duplicated statement) and each category it must
  keep (definition, LaTeX formula, condition, trap, worked example), plus a
  `[FROM LECTURE]` marker and an image embed.
- Walk `cleanup` against it by hand. Confirm: every "delete" category is
  gone, every "keep" category survives, LaTeX is byte-identical, the image
  embed and wikilinks survive, markers are stripped, headings are unchanged.
- Re-walk against the output to confirm idempotence — the second pass must
  report "already at note level" and change nothing.
- Walk Phase 2 against the same fixture and confirm the one-line format,
  section heading, and ordering rule.
- `tests/fixtures/sample_topic/exercises.md` is kept: `review-notes` reads
  it, and `review-notes` survives.

No Python changes, so `tests/test_config.py` and `tests/test_transcribe.py`
are untouched. `python3 -m pytest -v` must still pass.

## Out of scope

- Deleting `review-notes` or `flashcards-make`. Considered and rejected —
  they are exam-time tools and it is not exam time.
- Automatically running `cleanup` after `lecture-enhance`. The repo's
  no-auto-chaining rule stands.
- Migrating existing glossary entries. They are rebuilt, not migrated.
- Cleaning the four already-bloated statistics notes. That is a use of the
  skill, not part of building it.
