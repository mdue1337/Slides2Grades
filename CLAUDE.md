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
python3 -m pytest tests/test_config.py::test_name -v  # single test
bash tests/test_makenotes.sh            # bash test for makenotes.sh (not pytest-collected)
```

## Architecture

**The config seam.** `scripts/config.py`'s `load_config()` is the single source of
truth for finding the vault: resolution order is explicit path arg → `CONFIG_PATH`
env var → `<repo root>/config.env`. Every other script and skill goes through this
seam rather than reading `config.env` directly — `scripts/makenotes.sh` shells out
to `python3 scripts/config.py VAULT_PATH`, and `scripts/transcribe.py` imports
`load_config` directly. When adding a new script or skill that needs the vault
path, follow this same pattern instead of re-parsing `config.env`.

**Scripts vs. skills — different invocation models.** `scripts/*` are plain files
with no PATH/symlink install — they only run via explicit path (relative, from the
repo root, or absolute). The five `.claude/skills/*/SKILL.md` files are Claude Code
*project* skills: auto-discovered only when Claude Code's working directory is
inside this repo. They are not available when Claude Code is opened in `note-vault`
or elsewhere.

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
| `lecture-enhance` | `transcript_raw.md` + `notes.md` | `notes.md` (appends `[FROM LECTURE]` sections under `## From Lecture`) |
| `slides-enhance` | slide deck + `notes.md` | `notes.md` (appends under `## From Slides`; flags conflicts with Obsidian callouts: `> [!CAUTION]` for contradictions, `> [!INFO]` for updates) |
| `grill-notes` | `notes.md` | `exercises.md` (comprehension Q&A, continues numbering, never renumbers/deletes existing questions) |
| `review-notes` | `notes.md` + `exercises.md` | `exam_questions.md` (exam-format questions weighted toward concepts `exercises.md` under-covers; never deletes existing questions) |
| `flashcards-make` | `notes.md` | `flashcards.md` (`[Difficulty] Question \| Answer`, skips near-duplicates of existing cards, never deletes existing cards) |

Every skill resolves the vault via `python3 scripts/config.py VAULT_PATH` from the
repo root, and every skill must follow `STYLEGUIDE.md`'s formatting rules (bold key
terms, bullet points, no inline HTML, UTF-8, `[[wikilinks]]`) — the authoritative
formatting source is `STYLEGUIDE.md`, not restated per-skill; skills point to it
rather than duplicating its rules. All writes are append/annotate, never a rewrite
of existing content — this is a hard rule across all five skills.

**`tests/fixtures/sample_topic/`** holds shared fixture data (a binary-search-tree
example: `notes.md`, `transcript_raw.md`, `slides.md`, `exercises.md`) used to
manually verify skill behavior — Claude Code's Skill tool can fail to discover
project skills created or modified mid-session (a session-caching limitation), so
skill changes are verified by manually walking through the SKILL.md's own
instructions against this fixture data rather than relying on a live Skill tool
invocation.

**`conftest.py`** puts `scripts/` on `sys.path` so tests can `import config` /
`import transcribe` directly without packaging.
