---
name: begreber-extract
description: Extract key terms from a topic's notes.md into the course-level begreber.md glossary, rewritten in the user's own words with a wikilink back to the topic. Use when a topic's notes are finished, so the course has one reviewable glossary before the exam.
---

# Begreber-Extract

Pulls the key terms out of one topic's `notes.md` and appends them to the
**course-level** `begreber.md`.

The point of `begreber.md` is that it is *one* file per course: a glossary
scattered across topic folders can't be reviewed as a set, which is the only
thing a glossary is for. So this skill always writes up one level from the
topic.

## Inputs

- `<vault>/<Course>/<Topic>/notes.md` — may not exist yet or may be empty;
  if so, there is nothing to extract, so say that rather than inventing terms
- `<vault>/<Course>/begreber.md` — the target; create it with a
  `# Begreber — <Course>` header first if it doesn't exist

Course and topic come from the skill arguments (`<course> <topic>`); if not
supplied, ask.

Resolve `<vault>` via `python3 scripts/config.py VAULT_PATH` from the repo
root.

## What to do

1. Read `notes.md`.
2. Collect candidate terms. Prefer, in order:
   - terms already bolded in the notes (`**concept**`) — the user marked
     these deliberately
   - named theorems, laws, principles, models, and patterns
   - terms defined by the notes but not bolded
   Skip terms that are common knowledge in the field rather than course
   vocabulary, and skip anything the notes merely mention without defining.
3. Read the existing `begreber.md` and skip any term already present, in any
   topic section. Near-duplicates count as duplicates — do not add a second
   entry for the same concept under a different heading.
4. Write each definition **in plain own-words prose, not the textbook's
   phrasing**. If the notes only contain a verbatim quote from the source,
   rewrite it. A definition that could be replaced by a page reference to the
   literature adds nothing.
5. Group entries by topic so provenance survives, and so appending is always
   additive:

```
## <Topic>

### <Term>
**Definition**: <own words, one or two sentences>
**Why it matters**: <what it's used for in this course; omit if genuinely nothing to say>
**Source**: [[<Topic>]]
```

6. Append. If a `## <Topic>` section already exists, append the new terms
   inside it; otherwise add a new `## <Topic>` section at the end of the file.
   Never delete, reorder, or reword existing entries — including ones the user
   edited by hand.
7. Follow all formatting rules in `STYLEGUIDE.md` at the repo root (bold key
   terms, bullet points, no inline HTML, UTF-8, `[[wikilinks]]`).

## Output

Write the updated content to `<vault>/<Course>/begreber.md`. Report which
terms were added and which were skipped as already present.
