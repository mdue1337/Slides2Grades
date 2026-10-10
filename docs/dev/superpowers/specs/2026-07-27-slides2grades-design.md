# Slides2Grades Design

## Problem

Notes across the first two semesters were neglected, and that's showing up in grades. The goal is a set of AI-assisted tools that turn lecture materials (slides, recordings, live notes) into high-quality, reviewable Obsidian notes with minimal manual effort, plus generated practice questions and flashcards for exam prep.

## Architecture

Two separate repos, linked by config — not merged:

- **`Slides2Grades`** (this repo): the tooling. Claude Code skills, the local transcription script, `STYLEGUIDE.md`, and `config.yaml`. Generic and config-driven — no personal data or hardcoded paths, so it stays shareable later without extra work now.
- **`note-vault`** (existing, separate GitHub repo): the actual Obsidian vault — pure content. Backed by the Obsidian Git plugin for automatic commits, independent of this tooling repo.

`config.yaml` (gitignored, with a `config.example.yaml` checked in) holds:
- Local filesystem path to the `note-vault` checkout
- Whisper settings: model size (default `large-v3`), device (`cuda`)

Every skill and script reads this config to locate the vault rather than assuming a fixed path or the current working directory.

## Vault Structure & Scaffolding

Per `STYLEGUIDE.md`, unchanged:
- Level 1: Course
- Level 2: Topic
- Level 3: `notes.md`, `exercises.md`, `exam_questions.md`, `flashcards.md`, plus `transcript_raw.md` (see below)

`scripts/makenotes.sh` replaces the current `makenotes`:
- Prompts for **course name** and **topic name** (the original script only asked for topic, so folders would collide/nest incorrectly across courses)
- Resolves the vault path from `config.yaml` instead of operating on the current directory
- Seeds each `.md` file with a `# <Topic>` header instead of leaving them empty

`transcript_raw.md` is the raw whisper output per topic. It's added to `note-vault/.gitignore` — useful locally for re-running a skill without re-transcribing, but not synced, since `notes.md` (produced by Lecture-Enhance) is the durable, polished artifact.

## Transcription Pipeline

`scripts/transcribe.py` — standalone script, not a Claude Code skill (no LLM call, no token cost, so it doesn't belong inside the skill layer):

- Input: path to a recording, plus course/topic to know where to write output
- Runs [faster-whisper](https://github.com/SYSTRAN/faster-whisper) locally on GPU (CUDA), model size from `config.yaml`
- Output: `transcript_raw.md` in the matching `note-vault/<Course>/<Topic>/` folder
- Run manually whenever a recording is available — no auto-trigger, no chaining into other skills

Failure mode: if CUDA/GPU is unavailable, the script errors out with the underlying error rather than silently falling back to CPU — a silent CPU fallback would be slow enough to defeat the purpose, and the failure should be visible so it gets fixed.

## LLM Skills

Five Claude Code project skills under `.claude/skills/<name>/SKILL.md`, so cloning this repo and opening Claude Code makes them available. Each skill reads `STYLEGUIDE.md` for formatting/content rules and writes into the vault path resolved from `config.yaml`. All are run manually, one at a time — no auto-chaining pipeline.

| Skill | Reads | Writes to | When |
|---|---|---|---|
| **Lecture-Enhance** | `transcript_raw.md` + existing `notes.md` | `notes.md` (appends `[FROM LECTURE]` sections, preserves existing structure) | After transcribing a recording |
| **Slides-Enhance** | Slide deck (PDF/PPTX) + `notes.md` | `notes.md` (adds visual concepts missed by text notes, flags contradictions/updates with `[UPDATE]`/`[CAUTION]`) | After slides are posted |
| **Grill-Notes** | `notes.md` | `exercises.md` (comprehension Q&A, ranges from easy to hard, answers require synthesizing multiple concepts) | Soon after a topic is written up, to self-check understanding |
| **Review-Notes** | `notes.md` + `exercises.md` | `exam_questions.md` (varied formats: definition/application/synthesis, difficulty + `#tags`, calibrated to performance) | Closer to exam time |
| **Flashcards-Make** | `notes.md` | `flashcards.md` (`[Difficulty] Question \| Answer`, one per line) | Any time, for spaced repetition |

Skill interface choice: Claude Code skills rather than a standalone API-calling CLI, because Claude Code is already running under a Pro/Max subscription — using it for these skills incurs no extra per-token cost, and skills get file I/O, Bash (for invoking scripts, git), and interactive review for free instead of reimplementing that plumbing.

### Error Handling

- No existing `notes.md` content: skill creates fresh content rather than erroring.
- Slides-Enhance finds a contradiction with existing notes: flagged inline with `[UPDATE]`/`[CAUTION]` per `STYLEGUIDE.md`, never silently overwritten.

## Git Automation (note-vault)

Configured directly in `note-vault` via the **Obsidian Git** community plugin — not code in this repo, since it's vault-side configuration rather than tooling logic:
- Auto-commit on an interval (e.g. every 10–30 minutes) and/or on file change
- Auto-push, so the vault backs up automatically whether changes come from typing in Obsidian or a skill writing files

## Testing

- **Skills**: no automated test suite. Verified by running each skill against a real or sample topic folder and manually checking output against `STYLEGUIDE.md` formatting rules and factual soundness — this is generative/content tooling, not logic with deterministic correctness to assert on.
- **`scripts/makenotes.sh`**: smoke test that it creates the right course/topic folder structure with seeded files.
- **`scripts/transcribe.py`**: smoke test against a short sample audio clip, asserting a non-empty transcript is produced.

## Out of Scope (for this design)

- Packaging/distributing Slides2Grades for other students (installers, onboarding docs, setup wizard) — deferred until the tool is validated on personal use. The config-driven design keeps this option open without paying for it now.
- Auto-chained pipelines (e.g. one command from recording → fully updated notes) — starting manual/step-by-step; can revisit once individual skills are proven.
- Migrating existing vault content — `note-vault` is currently empty, so no migration is needed.

## Implementation Phases

1. Vault scaffolding + config: `config.yaml`, `scripts/makenotes.sh`, `note-vault/.gitignore` entry for `transcript_raw.md`, Obsidian Git plugin setup instructions.
2. Transcription pipeline: `scripts/transcribe.py`.
3. LLM skills: Lecture-Enhance, Slides-Enhance, Grill-Notes, Review-Notes, Flashcards-Make.
