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

   Content that a merge orphans — a wikilink or image embed that trailed a
   removed duplicate heading and is not itself duplicated — is never deleted.
   Move it under the surviving heading it fits by topic; if none fits, leave
   it where it sits relative to the surrounding content.
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
