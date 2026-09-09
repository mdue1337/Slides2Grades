# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Slides2Grades is tooling only — it holds scripts and Claude Code skills, never the
user's actual notes. Notes live in a separate Obsidian vault repo (`note-vault`),
whose local path is read from `config.env` (gitignored; template is
`config.example.env`). Never assume vault content lives in this repo, and never
write vault content into this repo.

## Commands

```bash
# Setup
cp config.example.env config.env   # then edit VAULT_PATH to point at the local note-vault checkout
pip install -r requirements.txt        # faster-whisper (real transcription)
pip install -r requirements-dev.txt     # pytest

# Tests
python3 -m pytest -v                    # all Python tests
python3 -m pytest tests/test_config.py -v          # single file
python3 scripts/progress.py "3. Semester"          # regenerate the semester progress tracker
python3 -m pytest tests/test_config.py::test_name -v  # single test
bash deprecated/test_makenotes.sh       # deprecated tool, kept working (not pytest-collected)
```

## Architecture

**The config seam.** `scripts/config.py`'s `load_config()` is the single source of
truth for finding the vault: resolution order is explicit path arg → `CONFIG_PATH`
env var → `<repo root>/config.env`. Every other script and skill goes through this
seam rather than reading `config.env` directly — `scripts/transcribe.py` imports
`load_config` directly, and skills shell out to `python3 scripts/config.py
VAULT_PATH`. When adding a new script or skill that needs the vault
path, follow this same pattern instead of re-parsing `config.env`.

**`scripts/progress.py` regenerates `<Semester>/Progress.md`.** It walks every
`<Course>/Week N/<NN - Title>.md` under the given semester folder and derives
pipeline status from what's actually on disk — a sibling `transcript_raw.md`
means transcribed, a `[FROM LECTURE]`/`[FROM SLIDES]` marker still in the note
means enhanced-but-not-cleaned, no marker (with a transcript present) means
cleaned. `Enhanced` and `Slides-enhanced` are cumulative with `Cleaned`,
because `cleanup` erases the marker that would otherwise prove enhancement
happened — a topic that's been cleaned always reads as enhanced too, even
though the literal marker is gone. The output is fully regenerated each run,
same "derived, not accumulated" principle as `Begreber.md` — never hand-edit
`Progress.md`, rerun the script instead.

**Scripts vs. skills — different invocation models.** `scripts/*` are plain files
with no PATH/symlink install — they only run via explicit path (relative, from the
repo root, or absolute). The six `.claude/skills/*/SKILL.md` files are Claude Code
*project* skills: auto-discovered only when Claude Code's working directory is
inside this repo. They are not available when Claude Code is opened in `note-vault`
or elsewhere.

**`makenotes.sh` is deprecated.** It lives in `deprecated/` and is not part
of any workflow. Course and week folders are created by hand, and note
content comes from the vault's Obsidian template at
`<vault>/_templates/topic-note.md`. Don't reintroduce scaffolding into the
active scripts.

**`Begreber.md` is course-level.** Every other skill reads and writes the
topic note itself, `<Course>/Week N/<NN - Title>.md` (with its sibling
`<NN - Title>/` folder holding `transcript_raw.md`); `begreber-extract` is the
one that writes one level up, to `<Course>/Begreber.md`. That is intentional —
a glossary fragmented across topic folders can't be reviewed as a set before
an exam. Preserve this if you touch path resolution in that skill.

**`faster-whisper` is imported lazily** inside `transcribe_audio()` in
`scripts/transcribe.py`, not at module level. This is deliberate: it lets the test
suite mock `sys.modules["faster_whisper"]` and run without the real package (or a
GPU) installed. Don't move this import to module scope.

**No silent CPU fallback.** `transcribe_audio` has no try/except around model
construction — if CUDA is unavailable, the underlying error should surface as-is
rather than silently falling back to CPU (which would be too slow to be useful).
Preserve this when touching transcription error handling.

**Skill content flow** (all run manually, one at a time, no auto-chaining):

| Skill | Reads | Writes |
|---|---|---|
| `lecture-enhance` | sibling `transcript_raw.md` + topic note | topic note (appends `[FROM LECTURE]` sections under `## From Lecture`) |
| `slides-enhance` | slide deck + topic note | topic note (appends under `## From Slides`; flags conflicts with Obsidian callouts: `> [!CAUTION]` for contradictions, `> [!INFO]` for updates) |
| `cleanup` | topic note + `Begreber.md` | topic note (rewritten to note level) + `<Course>/Begreber.md` (topic's section rebuilt) |
| `review-notes` | topic note + `exercises.md` | `exam_questions.md` (exam-format questions weighted toward concepts `exercises.md` under-covers; never deletes existing questions) |
| `flashcards-make` | topic note | `flashcards.md` (`[Difficulty] Question \| Answer`, skips near-duplicates of existing cards, never deletes existing cards) |
| `begreber-extract` | topic note | `<Course>/Begreber.md` (topic's section rebuilt, one line per term) |

Every skill resolves the vault via `python3 scripts/config.py VAULT_PATH` from the
repo root, and every skill must follow `STYLEGUIDE.md`'s formatting rules (bold key
terms, bullet points, no inline HTML, UTF-8, `[[wikilinks]]`) — the authoritative
formatting source is `STYLEGUIDE.md`, not restated per-skill; skills point to it
rather than duplicating its rules. `lecture-enhance`, `slides-enhance`, `review-notes`
and `flashcards-make` only ever append or annotate — never a rewrite of existing
content. That is a hard rule for those four.

`cleanup` and `begreber-extract` are the deliberate exceptions: they rewrite
by design, because the append-only skills are what turn a note into a
textbook and something has to subtract. The vault is a git repo, so `git
diff` reviews the change and `git checkout` reverts it.

**`tests/fixtures/sample_topic/`** holds shared fixture data (a binary-search-tree
example: `notes.md`, `notes_bloated.md` — a deliberately over-written note the
`cleanup` walk-through verifies against, `Begreber_legacy.md` — a glossary
holding both an old-format topic section and a hand-written theme-organised
area, for walking `cleanup`'s Phase 2 rewrite against, `transcript_raw.md`,
`slides.md`, `exercises.md`) used to
manually verify skill behavior — Claude Code's Skill tool can fail to discover
project skills created or modified mid-session (a session-caching limitation), so
skill changes are verified by manually walking through the SKILL.md's own
instructions against this fixture data rather than relying on a live Skill tool
invocation.

**`conftest.py`** puts `scripts/` on `sys.path` so tests can `import config` /
`import transcribe` directly without packaging.
