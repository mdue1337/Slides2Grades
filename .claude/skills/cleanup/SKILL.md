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

- `<vault>/<Course>/Week N/<NN - Title>.md` — the topic note. If it does not
  exist or is empty, say so rather than inventing content. Accepts more than
  one topic in a single invocation.
- `<vault>/<Course>/Begreber.md` — the glossary target, created if absent,
  per `STYLEGUIDE.md`.

Course and topic come from the skill arguments; if not supplied, ask. Topics
are named by note filename (`05 - Diskrete stokastiske variabler og PMF`),
not by week folder — glob `<vault>/<Course>/Week */<NN - Title>.md` to find
which week holds the note.

Resolve `<vault>` by running `python3 scripts/config.py VAULT_PATH` from the
repo root.

## Phase 1 — clean the note

Apply the **Note level** standard in `STYLEGUIDE.md` at the repo root. It is
the authoritative list of what to keep and what to delete; do not restate or
reinterpret it here.

Beyond that standard:

1. **Merge duplicates.** Content stated twice in one file collapses to one
   entry. The survivor may move under whichever *existing* heading fits best.

   Content that a merge orphans — a wikilink or image embed that trailed a
   removed duplicate heading and is not itself duplicated — is never deleted.
   Move it under the surviving heading it fits by topic; if none fits, leave
   it where it sits relative to the surrounding content.
2. **Strip `[FROM LECTURE]` markers.** `lecture-enhance` keeps emitting them;
   they are a review aid between the two passes, not permanent metadata.

   `## From Lecture` and `## From Slides` are staging areas, not permanent
   sections: content under them that survives and is not a duplicate moves
   into the existing section it belongs to, and an append heading left with
   nothing under it is removed.
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
6. **Highlight calculation formulas.** Last step of the phase, after cutting
   and merging, so nothing about to be deleted gets highlighted. Follow
   **Highlight** under **Note level** in `STYLEGUIDE.md` for what qualifies
   and where the `==` goes.
7. **Idempotence.** If the note is already at note level, with every
   qualifying formula already highlighted, report "already at note level" and
   leave the note byte-for-byte unchanged. Re-running must not keep shrinking
   a note, nor add, move or remove highlights. Continue to Phase 2 regardless — refreshing a stale
   glossary against an already-clean note is a legitimate use of this skill.

**Calibration.** The four notes in `<vault>/3. Semester/Introduktion til
sandsynlighedsteori og statistik/` cleaned by hand — `01 - Mængder,
Kardinalitet`, `02 - SS-mål og endelige udfaldsrum`, `03 - Betingede
Sandsynligheder & Uafhængighed` and `05 - Diskrete stokastiske variabler og
PMF` — are the reference output for how aggressive to be. Read one before a
first run on a new course. If this skill produces materially different
results on that input, the skill is wrong, not the notes. Highlights are
excepted: those notes predate the highlight step, so added `==` marks are
not a difference.

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
- which formulas were highlighted, and which qualifying display formulas were
  left unmarked for lack of a label line
- which glossary terms were added
- which glossary entries were removed or replaced

Then remind the user that `git diff` in the vault reviews the change.
