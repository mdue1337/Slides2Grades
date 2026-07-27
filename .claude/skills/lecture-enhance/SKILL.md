---
name: lecture-enhance
description: Merge a raw lecture transcript into a topic's notes.md, extracting high-density facts and linking to existing notes. Use after scripts/transcribe.py has produced a transcript_raw.md for a topic.
---

# Lecture-Enhance

Enhances `notes.md` for one topic using the raw transcript produced by
`scripts/transcribe.py`.

## Inputs

- `<vault>/<Course>/<Topic>/transcript_raw.md` — raw lecture transcript
- `<vault>/<Course>/<Topic>/notes.md` — existing notes for the topic (may be
  empty or not yet exist; if it doesn't exist, treat it as having no
  existing content)

Course and topic come from the skill arguments (`<course> <topic>`); if not
supplied, ask.

Resolve `<vault>` by running `python3 scripts/config.py VAULT_PATH` from the
repo root.

## What to do

1. Read `transcript_raw.md` and `notes.md`.
2. Extract high-density statements: facts, definitions, and key
   relationships. Ignore filler, repetition, and side comments.
3. Where a transcript statement clearly extends or clarifies something
   already in `notes.md`, add it near the relevant existing section. Use an
   Obsidian wikilink (`[[Topic Name]]`) if it references another topic.
4. Where content doesn't fit an existing section, append it under a new
   `## From Lecture` heading.
5. Mark every new bullet added from the transcript with `[FROM LECTURE]` so
   it's distinguishable from hand-written notes.
6. Preserve all existing structure and content in `notes.md` — this is an
   append/merge, never a rewrite.
7. Follow all formatting rules in `STYLEGUIDE.md` at the repo root
   (headers, bold key terms, bullet points, code blocks for formulas, UTF-8,
   wikilinks, no inline HTML).

## Output

Write the updated content back to `notes.md`.
