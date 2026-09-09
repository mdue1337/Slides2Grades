---
name: begreber-extract
description: Rebuild a topic's section of the course-level Begreber.md glossary from its note, as one dense line per term. Rewrites; git is the undo. Cleanup performs this same step itself as its Phase 2 without invoking this skill — use this standalone to refresh the glossary without touching notes.
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
- `<vault>/<Course>/Begreber.md` — the target, created if absent, per
  `STYLEGUIDE.md`.

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
