# Cleanup Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the unused `grill-notes` skill with a `cleanup` skill that rewrites a topic note down to note level and refreshes the course glossary as a second phase.

**Architecture:** `STYLEGUIDE.md` becomes the single source for the "note level" standard and the glossary format; `cleanup` and `begreber-extract` point at it rather than restating it. `cleanup` performs the glossary step itself — no skill chaining, which this repo forbids. Two skills rewrite by design (`cleanup`, `begreber-extract`) while the other four stay append-only.

**Tech Stack:** Markdown skill definitions (`.claude/skills/*/SKILL.md`), bash, pytest. No Python logic changes.

**Spec:** `docs/superpowers/specs/2026-09-09-cleanup-skill-design.md`

## Global Constraints

Copied verbatim from the spec. Every task's requirements implicitly include this section.

- **LaTeX is preserved verbatim.** Never convert `$A \cap B$` to unicode. `\bigcup_{i=1}^{n}` has no clean unicode form.
- **Never touch** image embeds (`![[Pasted image ...]]`), wikilinks, or a note's language.
- **Never invent or replace a heading scheme** — this covers `**Bold**` pseudo-headings as well as `#` headings.
- **Vault layout is** `<vault>/<Course>/Week N/<NN - Title>.md`, with `transcript_raw.md` in a sibling `<NN - Title>/` folder. The glossary is `<vault>/<Course>/Begreber.md` — **capital B**.
- **Vault path resolves via** `python3 scripts/config.py VAULT_PATH` from the repo root. Never re-parse `config.env`.
- **No skill auto-chaining.** A skill never invokes another skill.
- **`STYLEGUIDE.md` is authoritative for formats.** Skills point at it; they do not restate its rules.
- **Six skills after this change:** `cleanup`, `lecture-enhance`, `slides-enhance`, `review-notes`, `flashcards-make`, `begreber-extract`.
- **Cleanup and begreber-extract rewrite in place.** Git is the undo. The append-only rule still binds the other four skills.
- The four already-cleaned statistics notes are the **reference output**. If the written skill would produce materially different results on the same input, the skill is wrong.

---

### Task 1: Deprecate `makenotes.sh`

Never used; folders are created by hand and that convention is staying. Moving it rather than fixing it makes its lowercase `begreber.md` bug unreachable.

**Files:**
- Move: `scripts/makenotes.sh` → `deprecated/makenotes.sh`
- Move: `tests/test_makenotes.sh` → `deprecated/test_makenotes.sh`
- Modify: `deprecated/makenotes.sh` (config.py path)
- Modify: `deprecated/test_makenotes.sh` (script path)

**Interfaces:**
- Consumes: nothing.
- Produces: `deprecated/` directory, referenced by Task 2's STYLEGUIDE text and Task 5's CLAUDE.md and README.md text.

- [ ] **Step 1: Move both files**

```bash
mkdir -p deprecated
git mv scripts/makenotes.sh deprecated/makenotes.sh
git mv tests/test_makenotes.sh deprecated/test_makenotes.sh
```

- [ ] **Step 2: Run the test to verify it now fails**

```bash
bash deprecated/test_makenotes.sh
```

Expected: FAIL. The test calls `"$REPO_ROOT/scripts/makenotes.sh"`, which no longer exists, so bash reports "No such file or directory".

- [ ] **Step 3: Fix the script's path to `config.py`**

`makenotes.sh` resolves `config.py` relative to its own directory. Now that it lives in `deprecated/`, that resolution points at `deprecated/config.py`, which does not exist. In `deprecated/makenotes.sh`, replace:

```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_PATH="$(python3 "$SCRIPT_DIR/config.py" VAULT_PATH)"
```

with:

```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
VAULT_PATH="$(python3 "$REPO_ROOT/scripts/config.py" VAULT_PATH)"
```

- [ ] **Step 4: Fix the test's path to the script**

In `deprecated/test_makenotes.sh`, there are three invocations of the script. Replace all of them:

```bash
sed -i 's|\$REPO_ROOT/scripts/makenotes.sh|$REPO_ROOT/deprecated/makenotes.sh|g' deprecated/test_makenotes.sh
```

Verify three occurrences were changed:

```bash
grep -c 'deprecated/makenotes.sh' deprecated/test_makenotes.sh
```

Expected: `3`

- [ ] **Step 5: Run the test to verify it passes**

```bash
bash deprecated/test_makenotes.sh
```

Expected: `PASS: test_makenotes.sh`

- [ ] **Step 6: Verify the Python suite is unaffected**

```bash
python3 -m pytest -v
```

Expected: PASS. `conftest.py` puts `scripts/` on `sys.path`; only `config.py` and `transcribe.py` live there now, and neither moved.

- [ ] **Step 7: Commit**

```bash
git add -A deprecated scripts tests
git commit -m "chore: deprecate makenotes.sh, folders are made by hand"
```

---

### Task 2: Rewrite `STYLEGUIDE.md`

This is the shared rules source both new skills point at, so it lands before them. The current file is stale in three ways: it documents a vault layout that does not exist, a `Notes Clarity` standard that caused the bloat, and the old five-line glossary format.

**Files:**
- Modify: `STYLEGUIDE.md` (full rewrite)

**Interfaces:**
- Consumes: `deprecated/` from Task 1.
- Produces: two named sections that Tasks 3 and 4 reference by name — **`## Note level`** and **`### Begreber (course glossary)`**. The skills say "follow `STYLEGUIDE.md`'s `<section name>`", so these names must match exactly.

- [ ] **Step 1: Replace the whole file**

Write `STYLEGUIDE.md` with exactly this content:

````markdown
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

Course and week folders are created by hand. `scripts/makenotes.sh` is
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
- May merge content stated twice in one file, moving the survivor under
  whichever *existing* heading fits best.
- Strips `[FROM LECTURE]` markers.
- Mixed-language note: the **dominant** language wins when merging a
  duplicate across the language boundary. Never translate anything that is
  not a duplicate.
- Cross-file duplication is out of scope — the merge rule is within one file.
- Idempotent: on an already-clean note, report "already at note level" and
  write nothing.

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
````

- [ ] **Step 2: Verify the section names the skills will reference exist**

```bash
grep -n '^## Note level$' STYLEGUIDE.md
grep -n '^### Begreber (course glossary)$' STYLEGUIDE.md
```

Expected: one line of output each. If either is missing, Tasks 3 and 4 will point at a section that does not exist.

- [ ] **Step 3: Verify the stale content is gone**

```bash
grep -n 'Grill-Notes\|Concept Clarity\|Level 3: notes.md\|begreber\.md' STYLEGUIDE.md
```

Expected: no output. `Grill-Notes` and `Concept Clarity` are deleted; lowercase `begreber.md` is now `Begreber.md`.

- [ ] **Step 4: Commit**

```bash
git add STYLEGUIDE.md
git commit -m "docs: make STYLEGUIDE the shared source for note level and glossary format"
```

---

### Task 3: Create the `cleanup` skill and delete `grill-notes`

**Files:**
- Create: `.claude/skills/cleanup/SKILL.md`
- Create: `tests/fixtures/sample_topic/notes_bloated.md`
- Delete: `.claude/skills/grill-notes/SKILL.md` (and its directory)

**Interfaces:**
- Consumes: `STYLEGUIDE.md`'s `## Note level` and `### Begreber (course glossary)` sections from Task 2.
- Produces: skill name `cleanup`, referenced by Task 5's CLAUDE.md table, README.md table, and the pointer line added to `lecture-enhance/SKILL.md`.

Skills cannot be tested by pytest — they are instructions, not code. Per `CLAUDE.md`, skill changes are verified by walking the SKILL.md's own instructions against fixture data, because Claude Code's Skill tool can fail to discover project skills created mid-session. So the fixture comes first and acts as the test.

- [ ] **Step 1: Write the fixture that acts as the failing test**

Create `tests/fixtures/sample_topic/notes_bloated.md`. It carries one instance of every category cleanup must delete and every category it must keep, so a walk-through has something to catch.

````markdown
# Binary Search Trees

## Motivation
The binary search tree was one of the great ideas of early computer science.
In the 1960s, as memory became cheap enough to hold large collections in
core, researchers looked for a structure that would give the lookup speed of
a sorted array without the insertion cost. The BST was the answer, and it
remains the mental model behind most ordered containers today. Think of it
as the data-structure equivalent of binary search itself, made persistent.

## Definition
A **binary search tree** is a binary tree where every node's key is greater
than all keys in its left subtree and less than all keys in its right
subtree.

- [FROM LECTURE] The invariant must hold for **every** node, not just the
  root. A tree that satisfies it only at the root is not a BST.

## Complexity
Lookup, insert and delete are all $O(h)$ where $h$ is the height.
$$h = \Theta(\log n) \text{ if balanced}, \qquad h = \Theta(n) \text{ worst case}$$

Requires the keys to be **totally ordered** — no BST over an unordered type.

> **Trap:** the worst case is not exotic. Inserting already-sorted data gives
> a linked list, not a tree.

## Proof that in-order traversal is sorted
We argue by induction on the height of the tree. For the base case, a tree of
height 0 is empty and the empty sequence is trivially sorted. For the
inductive step, assume the claim holds for all trees of height less than $h$
and consider a tree of height $h$ with root $r$. By the inductive hypothesis
the traversal of the left subtree is sorted, and every key in it is less than
$r$ by the BST invariant. The same argument applies on the right. Therefore
the concatenation is sorted, which completes the induction.

## Example 4.2
Insert 5, 3, 8, 1 into an empty tree.
First we insert 5, which becomes the root because the tree is empty. Then we
insert 3; we compare it against 5, find it smaller, and go left, where we
find an empty slot. Then 8, which is larger than 5, so it goes right. Then 1,
which is smaller than 5 and then smaller than 3, so it ends up as the left
child of 3. The resulting tree has height 2.
```
     5
    / \
   3   8
  /
 1
```

## Aside
This was the part of the lecture where the projector failed, so the last ten
minutes ran over into the break. The exercise sheet is on the course page and
is due Friday.

**Exam advice:** always state which balance invariant you are assuming. Half
the marks lost on this topic come from claiming $O(\log n)$ without saying
the tree is balanced.

## Complexity again
As noted above, lookup is $O(h)$, which is $\Theta(\log n)$ when the tree is
balanced and $\Theta(n)$ in the worst case.

See [[Sorting Algorithms]] for the traversal connection.

![[Pasted image bst-example.png]]
````

- [ ] **Step 2: Write the skill**

Create `.claude/skills/cleanup/SKILL.md`:

````markdown
---
name: cleanup
description: Rewrite a topic's note down to note level — terse definitions, formulas, conditions and stripped worked examples — then refresh the course glossary. Destructive; git is the undo. Use after lecture-enhance or slides-enhance has bloated a note.
---

# Cleanup

Rewrites a topic note down to **note level**, then rebuilds that topic's
section of the course glossary.

This skill **deletes content**, unlike the append-only skills. That is the
point: `lecture-enhance` and `slides-enhance` only ever add, so notes drift
from a reference surface into a textbook. The vault is a git repo, so `git
diff` reviews the change and `git checkout` reverts it.

## Inputs

- `<vault>/<Course>/Week N/<NN - Title>.md` — the topic note. Accepts more
  than one topic in a single invocation.
- `<vault>/<Course>/Begreber.md` — the glossary target; create it with a
  `# Begreber — <Course>` header if it does not exist.

Course and topic come from the skill arguments; if not supplied, ask. Topics
are named by note filename (`05 - Diskrete stokastiske variabler og PMF`),
not by week folder.

Resolve `<vault>` by running `python3 scripts/config.py VAULT_PATH` from the
repo root.

## Phase 1 — clean the note

Apply the **Note level** standard in `STYLEGUIDE.md` at the repo root. It is
the authoritative list of what to keep and what to delete; do not restate or
reinterpret it here.

Beyond that standard:

1. **Merge duplicates.** Content stated twice in one file collapses to one
   entry. The survivor may move under whichever *existing* heading fits best.
   Never invent a heading scheme, and never replace the note's section
   numbering.
2. **Strip `[FROM LECTURE]` markers.** `lecture-enhance` keeps emitting them;
   they are a review aid between the two passes, not permanent metadata.
3. **Mixed-language notes.** A note may hold an English pre-reading block
   above Danish lecture content. When merging a duplicate across that
   boundary, the note's **dominant** language wins. Never translate anything
   that is not a duplicate.
4. **Cross-file duplication is out of scope.** The merge rule is within one
   file. Two notes may legitimately both carry a rule. At most, replace a
   restatement with a wikilink when the note itself does not need the
   content.
5. **Hand-written prose is cut on the same terms** as transcript-derived
   prose. The rules do not distinguish them.
6. **Idempotence.** If the note is already at note level, report "already at
   note level" and write nothing. Re-running must not keep shrinking a note.

## Phase 2 — refresh the glossary

Rebuild the topic's section of `<Course>/Begreber.md` from the *cleaned*
note, following **Begreber (course glossary)** in `STYLEGUIDE.md`.

Perform this yourself. Do **not** invoke the `begreber-extract` skill — this
repo runs skills manually, one at a time, with no auto-chaining.

## Output

Write the cleaned note back in place. Write `Begreber.md` back in place.

Report, per note:
- rough before/after size
- which categories were cut
- which glossary terms were added

Then remind the user that `git diff` in the vault reviews the change.
````

- [ ] **Step 3: Delete `grill-notes`**

```bash
git rm -r .claude/skills/grill-notes
```

- [ ] **Step 4: Walk the skill against the fixture**

Copy the fixture somewhere scratch so the original stays pristine, then follow `.claude/skills/cleanup/SKILL.md`'s Phase 1 instructions against the copy by hand — reading `STYLEGUIDE.md`'s `## Note level` as the skill tells you to.

```bash
mkdir -p /tmp/cleanup-check
cp tests/fixtures/sample_topic/notes_bloated.md /tmp/cleanup-check/notes.md
```

- [ ] **Step 5: Check the output against the invariants**

Every one of these must hold for the cleaned copy:

**Deleted:**
```bash
grep -c 'great ideas of early computer science' /tmp/cleanup-check/notes.md   # 0 (motivation)
grep -c 'In the 1960s' /tmp/cleanup-check/notes.md                            # 0 (history)
grep -c 'projector failed' /tmp/cleanup-check/notes.md                        # 0 (aside)
grep -c 'inductive hypothesis' /tmp/cleanup-check/notes.md                    # 0 (proof prose)
grep -c 'FROM LECTURE' /tmp/cleanup-check/notes.md                            # 0 (markers)
grep -c 'Complexity again' /tmp/cleanup-check/notes.md                        # 0 (restatement merged)
```

**Kept:**
```bash
grep -c 'totally ordered' /tmp/cleanup-check/notes.md        # >=1 (condition of use)
grep -c 'already-sorted data' /tmp/cleanup-check/notes.md    # >=1 (trap)
grep -c 'balance invariant' /tmp/cleanup-check/notes.md      # >=1 (exam advice)
grep -c 'Example 4.2' /tmp/cleanup-check/notes.md            # >=1 (worked example survives)
grep -c 'Sorting Algorithms' /tmp/cleanup-check/notes.md     # >=1 (wikilink)
grep -c 'bst-example.png' /tmp/cleanup-check/notes.md        # >=1 (image embed)
```

**LaTeX byte-identical** — the height formula must survive unchanged:
```bash
grep -F '$$h = \Theta(\log n) \text{ if balanced}, \qquad h = \Theta(n) \text{ worst case}$$' /tmp/cleanup-check/notes.md
```
Expected: the line, matched exactly. If it does not match, LaTeX was rewritten and the skill's constraint is being violated.

Also confirm by eye: the ASCII tree diagram in Example 4.2 survives, the `# Binary Search Trees` and `## Definition` headings are unchanged, and the note is materially shorter.

- [ ] **Step 6: Verify idempotence**

Walk Phase 1 against the *cleaned* copy a second time.

Expected: the response is "already at note level" and the file is unchanged:

```bash
cp /tmp/cleanup-check/notes.md /tmp/cleanup-check/notes-pass1.md
# ...second walk...
diff /tmp/cleanup-check/notes.md /tmp/cleanup-check/notes-pass1.md
```
Expected: no output.

If the second pass shrinks the file further, the Note level standard is under-specified — fix `STYLEGUIDE.md`, not the output.

- [ ] **Step 7: Clean up the scratch copy**

```bash
rm -rf /tmp/cleanup-check
```

- [ ] **Step 8: Commit**

```bash
git add .claude/skills/cleanup/SKILL.md tests/fixtures/sample_topic/notes_bloated.md
git add -A .claude/skills/grill-notes
git commit -m "feat: add cleanup skill, remove unused grill-notes"
```

---

### Task 4: Rewrite `begreber-extract`

It survives as a standalone skill so the glossary can be refreshed without a destructive note rewrite. It switches from append-only to derive-and-rewrite, and stops restating the format.

**Files:**
- Modify: `.claude/skills/begreber-extract/SKILL.md` (full rewrite)

**Interfaces:**
- Consumes: `STYLEGUIDE.md`'s `### Begreber (course glossary)` section from Task 2; the `cleanup` skill name from Task 3.
- Produces: the updated `description` frontmatter that Task 5 quotes in the CLAUDE.md and README.md tables.

- [ ] **Step 1: Replace the file**

````markdown
---
name: begreber-extract
description: Rebuild a topic's section of the course-level Begreber.md glossary from its note, as one dense line per term. Rewrites; git is the undo. Runs automatically as cleanup's second phase — use this standalone only to refresh the glossary without touching notes.
---

# Begreber-Extract

Rebuilds one topic's section of the **course-level** `Begreber.md` from that
topic's note.

The point of `Begreber.md` is that it is *one* file per course: a glossary
scattered across topic folders can't be reviewed as a set, which is the only
thing a glossary is for. So this skill always writes one level up from the
topic.

`cleanup` runs this same step automatically as its Phase 2. Use this skill on
its own when you want the glossary refreshed without a destructive note
rewrite.

## Inputs

- `<vault>/<Course>/Week N/<NN - Title>.md` — the topic note. If it does not
  exist or is empty, say so rather than inventing terms. Accepts more than
  one topic in a single invocation.
- `<vault>/<Course>/Begreber.md` — the target; create it with a
  `# Begreber — <Course>` header if it does not exist.

Course and topic come from the skill arguments; if not supplied, ask. Topics
are named by note filename, not by week folder.

Resolve `<vault>` by running `python3 scripts/config.py VAULT_PATH` from the
repo root.

## What to do

Follow **Begreber (course glossary)** in `STYLEGUIDE.md` at the repo root. It
is the authoritative format; do not restate or reinterpret it here.

Term selection, in order of preference:

1. Terms already bolded in the note (`**concept**`) — the user marked those
   deliberately.
2. Named theorems, laws, principles, models, and patterns.
3. Terms the note defines but does not bold.

Skip terms that are common knowledge in the field rather than course
vocabulary, and skip anything the note merely mentions without defining.

This skill **rewrites**. For each topic processed, delete any existing
content for that topic and rebuild it from the note — never migrate old
entries. Sections for other topics are left byte-for-byte alone, and are read
only so a term is not defined twice across topics.

## Output

Write `<vault>/<Course>/Begreber.md` back in place. Report which terms were
added, and which were skipped as already defined under another topic. Then
remind the user that `git diff` in the vault reviews the change.
````

- [ ] **Step 2: Verify it points at the styleguide rather than restating it**

```bash
grep -c 'Begreber (course glossary)' .claude/skills/begreber-extract/SKILL.md
```
Expected: `1`

```bash
grep -c 'Why it matters\|\*\*Source\*\*\|order of first appearance' .claude/skills/begreber-extract/SKILL.md
```
Expected: `0` — the old five-line format is gone and the ordering rule lives only in `STYLEGUIDE.md`.

- [ ] **Step 3: Walk it against the fixture**

Following this SKILL.md and `STYLEGUIDE.md`'s glossary section, derive the entries for `tests/fixtures/sample_topic/notes_bloated.md` into a scratch file.

Confirm the output:
- has a `## [[Binary Search Trees]]` heading — a wikilink, not plain text
- is one line per term, in the form `**Term** — definition.`
- has no `**Definition**:`, `**Why it matters**:`, or `**Source**:` lines
- lists terms in order of first appearance (`binary search tree` before the
  complexity terms), not alphabetically
- preserves LaTeX such as `$O(h)$` verbatim

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/begreber-extract/SKILL.md
git commit -m "feat: rebuild begreber-extract as derive-and-rewrite, one line per term"
```

---

### Task 5: Update `CLAUDE.md`, `README.md`, and `lecture-enhance`

The docs describe a skill that no longer exists, a hard rule that two skills now break, and a `makenotes.sh` that has both moved and never done what the README claims.

**Files:**
- Modify: `CLAUDE.md`
- Modify: `README.md`
- Modify: `.claude/skills/lecture-enhance/SKILL.md`

**Interfaces:**
- Consumes: `deprecated/` (Task 1), the `cleanup` skill name (Task 3), the `begreber-extract` description (Task 4).
- Produces: nothing downstream — this is the last task.

- [ ] **Step 1: Add the follow-up pointer to `lecture-enhance`**

In `.claude/skills/lecture-enhance/SKILL.md`, after the numbered "What to do" list, add:

```markdown
Markers are deliberate and stay. `cleanup` is the follow-up pass that strips
them once you have reviewed what was added.
```

- [ ] **Step 2: Swap the `grill-notes` row for `cleanup` in `CLAUDE.md`**

In the **Skill content flow** table, delete the `grill-notes` row and add:

```markdown
| `cleanup` | topic note + `Begreber.md` | topic note (rewritten to note level) + `<Course>/Begreber.md` (topic's section rebuilt) |
```

Update the `begreber-extract` row to:

```markdown
| `begreber-extract` | topic note | `<Course>/Begreber.md` (topic's section rebuilt, one line per term) |
```

- [ ] **Step 3: Split the append-only hard rule in `CLAUDE.md`**

Replace:

```markdown
All writes are append/annotate, never a rewrite
of existing content — this is a hard rule across all six skills.
```

with:

```markdown
`lecture-enhance`, `slides-enhance`, `review-notes` and `flashcards-make`
only ever append or annotate — never a rewrite of existing content. That is
a hard rule for those four.

`cleanup` and `begreber-extract` are the deliberate exceptions: they rewrite
by design, because the append-only skills are what turn a note into a
textbook and something has to subtract. The vault is a git repo, so `git
diff` reviews the change and `git checkout` reverts it.
```

- [ ] **Step 4: Fix the remaining `CLAUDE.md` staleness**

Replace the `**makenotes.sh` creates directories, not note bodies.**` paragraph with:

```markdown
**`makenotes.sh` is deprecated.** It lives in `deprecated/` and is not part
of any workflow. Course and week folders are created by hand, and note
content comes from the vault's Obsidian template at
`<vault>/_templates/topic-note.md`. Don't reintroduce scaffolding into the
active scripts.
```

Then fix the glossary filename throughout:

```bash
sed -i 's/`begreber\.md`/`Begreber.md`/g' CLAUDE.md
grep -c 'begreber\.md' CLAUDE.md
```
Expected: `0`

- [ ] **Step 5: Update the `README.md` workflow table**

Replace the table body with:

```markdown
| Step | Tool | What it does |
|---|---|---|
| New topic | (by hand) | Create `<Course>/Week N/` and the `<NN - Title>.md` note in Obsidian |
| After a lecture recording | `scripts/transcribe.py <audio> <course> <topic>` | Runs faster-whisper locally, writes `transcript_raw.md` |
| After transcribing | `lecture-enhance` skill | Merges the transcript into the note, marked `[FROM LECTURE]` |
| After slides are posted | `slides-enhance` skill | Adds what slides cover that notes miss, flags contradictions |
| When a note has got long | `cleanup` skill | Rewrites the note down to note level and rebuilds its glossary section. Destructive; git is the undo |
| To refresh only the glossary | `begreber-extract` skill | Rebuilds a topic's section of `<Course>/Begreber.md` |
| Closer to exam time | `review-notes` skill | Generates exam-style questions into `exam_questions.md` |
| Any time | `flashcards-make` skill | Generates spaced-repetition cards into `flashcards.md` |
```

- [ ] **Step 6: Update the `README.md` test section**

Replace:

```bash
python3 -m pytest -v
bash tests/test_makenotes.sh
```

with:

```bash
python3 -m pytest -v
bash deprecated/test_makenotes.sh   # deprecated tool, kept working
```

- [ ] **Step 7: Verify no stale references survive anywhere**

```bash
grep -rn 'grill-notes\|grill_notes' --include='*.md' . | grep -v docs/superpowers
```
Expected: no output. (The spec and this plan mention it by design; they are excluded.)

```bash
grep -rn 'scripts/makenotes.sh' --include='*.md' .
```
Expected: no output.

```bash
grep -rn 'all six skills' CLAUDE.md
```
Expected: no output — the hard rule no longer applies to all six.

- [ ] **Step 8: Verify the suite still passes**

```bash
python3 -m pytest -v
bash deprecated/test_makenotes.sh
```
Expected: both PASS.

- [ ] **Step 9: Commit**

```bash
git add CLAUDE.md README.md .claude/skills/lecture-enhance/SKILL.md
git commit -m "docs: retarget skill docs at cleanup, split the append-only rule"
```

---

## Self-Review

**Spec coverage.** Walked each spec section against the tasks:

| Spec section | Task |
|---|---|
| The `cleanup` skill — frontmatter, inputs, Phase 1, Phase 2, output | 3 |
| Mixed-language / bold pseudo-headings / cross-file duplication rules | 2 (STYLEGUIDE) + 3 (SKILL.md) |
| Glossary format and derive-not-migrate semantics | 2 (STYLEGUIDE) + 4 (skill) |
| `STYLEGUIDE.md` — all five edits | 2 |
| `begreber-extract` changes | 4 |
| Ripple: delete grill-notes | 3 |
| Ripple: CLAUDE.md, README.md, lecture-enhance | 5 |
| Ripple: deprecate makenotes.sh | 1 |
| Verification: bloated fixture, walk, idempotence re-walk | 3 |
| Verification: `exercises.md` fixture kept (review-notes reads it) | untouched by every task — correct |
| Verification: pytest unaffected | 1 (step 6), 5 (step 8) |

No gaps.

**Placeholder scan.** No "TBD", no "similar to Task N", no "add appropriate error handling". Every file that gets written has its full content inline. Every verification step has the exact command and its expected output.

**Type consistency.** The two `STYLEGUIDE.md` section names are the interface between Task 2 and Tasks 3–4, and they are spelled identically in all three places: `## Note level` and `### Begreber (course glossary)`. Task 2 step 2 asserts both exist before the skills point at them. The skill name `cleanup` is consistent across the SKILL.md frontmatter, the CLAUDE.md table, the README table, and the `lecture-enhance` pointer line.

**One risk worth flagging to the executor.** Tasks 3 and 4 are verified by a human walk-through, not an automated test — that is the repo's established practice for skills, because the Skill tool can fail to discover project skills created mid-session. The grep assertions in Task 3 step 5 make the objective half of that check mechanical, but "is this actually a good note?" stays a judgement call. The four cleaned statistics notes in the vault are the reference standard.
