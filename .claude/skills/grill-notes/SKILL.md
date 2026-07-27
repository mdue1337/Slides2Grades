---
name: grill-notes
description: Generate comprehension-check questions from a topic's notes.md into exercises.md, testing understanding rather than recall. Use soon after a topic's notes are written up to self-check understanding.
---

# Grill-Notes

Generates comprehension questions from `notes.md` for one topic into
`exercises.md`.

## Inputs

- `<vault>/<Course>/<Topic>/notes.md`

Resolve `<vault>` via `python3 scripts/config.py VAULT_PATH`.

## What to do

1. Read `notes.md`.
2. Write 5-10 questions that test understanding of the material, not just
   recall of facts. Prefer questions that require explaining *why* or
   *how*, or applying a concept to a new scenario, over "what is X".
3. Include a range of difficulty: some Easy, some Medium, some Hard. At
   least one Hard question must require synthesizing two or more concepts
   from the notes together.
4. Format each question per `STYLEGUIDE.md`:

```
## Question 1 [Easy]
**Q**: [Question text]
**A**: [Answer with reasoning]
```

5. Follow all formatting rules in `STYLEGUIDE.md` at the repo root (bold
   key terms, bullet points, no inline HTML, UTF-8) within each answer,
   not just the Q&A block shape.
6. Append new questions to the end of `exercises.md` (create it with a
   `# <Topic>` header first if it doesn't exist). Never delete or renumber
   existing questions — continue numbering from the highest existing
   question number.

## Output

Write the updated content to `exercises.md`.
