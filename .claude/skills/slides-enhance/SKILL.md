---
name: slides-enhance
description: Compare a slide deck against a topic's notes.md, adding visual concepts the notes miss and flagging contradictions. Use after new lecture slides are posted for a topic.
---

# Slides-Enhance

Compares slides against `notes.md` for one topic and enhances the notes with
what the slides add.

## Inputs

- The slide deck for the topic (PDF, PPTX, or any readable text), read
  directly with the Read tool
- `<vault>/<Course>/<Topic>/notes.md`

Resolve `<vault>` via `python3 scripts/config.py VAULT_PATH`.

## What to do

1. Read the slide deck and `notes.md`.
2. Identify concepts, diagrams, or relationships present in the slides but
   missing or under-explained in `notes.md` — add them, following
   `STYLEGUIDE.md` formatting.
3. If a slide contradicts or updates something already written in
   `notes.md` (e.g. a formula, a definition, a complexity claim), do not
   silently overwrite it. Insert a callout directly above the conflicting
   content:
   - `> [!CAUTION] Slides contradict this: <what the slide says>` for
     direct contradictions
   - `> [!UPDATE] Slides add/clarify: <what changed>` for clarifications or
     extensions
4. Preserve all existing structure — this is an append/annotate operation,
   never a rewrite of existing sections.

## Output

Write the updated content back to `notes.md`.
