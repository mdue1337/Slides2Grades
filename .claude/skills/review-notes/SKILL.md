---
name: review-notes
description: Generate exam-style practice questions from a topic's note and exercises.md into exam_questions.md, weighting toward concepts not yet covered by existing exercises. Use closer to exam time for a topic.
---

# Review-Notes

Generates exam-format practice questions from a topic's note and its
`exercises.md` into `exam_questions.md`.

## Inputs

- `<vault>/<Course>/Week N/<NN - Title>.md` — the topic note; may not exist
  yet or may be empty; if so, there's no source material to draw from, so say
  that rather than fabricating questions
- `<vault>/<Course>/Week N/<NN - Title>/exercises.md` (if present) — treat
  questions here as already-covered material, not to be repeated verbatim

Course and topic come from the skill arguments (`<course> <topic>`); if not
supplied, ask.

Resolve `<vault>` via `python3 scripts/config.py VAULT_PATH` from the repo
root.

## What to do

1. Read both input files.
2. Write exam-style questions varying in format: definition, application,
   and synthesis questions.
3. If `exercises.md` tests the same concept repeatedly, weight new
   questions toward concepts from the note that aren't well covered yet.
4. Format each question per `STYLEGUIDE.md`:

```
## Question [Difficulty] #tags
**Format**: [Multiple Choice / Short Answer / Essay]
**Q**: [Question]
**Suggested Answer**: [Answer]
```

5. Follow all formatting rules in `STYLEGUIDE.md` at the repo root (bold
   key terms, bullet points, no inline HTML, UTF-8) within each answer,
   not just the block shape.
6. Use topic-relevant `#tags` (e.g. `#binary-search-trees`) so questions
   are filterable in Obsidian.
7. Append to the end of `exam_questions.md` (create it with a `# <Topic>`
   header first if it doesn't exist). Never delete existing questions.

## Output

Write the updated content to `<vault>/<Course>/Week N/<NN - Title>/exam_questions.md`,
the sibling folder of the note.
