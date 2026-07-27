---
name: flashcards-make
description: Generate spaced-repetition flashcards from a topic's notes.md into flashcards.md. Use any time after notes.md has meaningful content for a topic.
---

# Flashcards-Make

Generates flashcards from `notes.md` for one topic into `flashcards.md`.

## Inputs

- `<vault>/<Course>/<Topic>/notes.md` — may not exist yet or may be empty;
  if so, there's no source material to draw from, so say that rather than
  fabricating cards

Course and topic come from the skill arguments (`<course> <topic>`); if not
supplied, ask.

Resolve `<vault>` via `python3 scripts/config.py VAULT_PATH` from the repo
root.

## What to do

1. Read `notes.md`.
2. Extract discrete, atomic facts, definitions, and relationships suitable
   for spaced repetition — one clear question per card, one clear answer.
   Avoid multi-part questions.
3. Format per `STYLEGUIDE.md`, one card per line:

```
[Easy/Medium/Hard] Question | Answer
```

4. Read the existing `flashcards.md` first and skip concepts already
   covered by a card with materially the same question, to avoid
   duplicates.
5. Append new cards to the end of `flashcards.md` (create it if it doesn't
   exist). Never delete or edit existing cards.

## Output

Write the updated content to `flashcards.md`.
