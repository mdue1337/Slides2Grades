# Slides2Grades

Tooling to turn lecture slides, recordings, and your own notes into a well-organized
Obsidian vault, plus generated practice questions and flashcards. This repo holds the
tooling only — your actual notes live in a separate Obsidian vault repo (e.g.
`note-vault`), never in here.

See `docs/superpowers/specs/2026-07-27-slides2grades-design.md` for the full design.

## Setup

1. Copy the config template and point it at your vault:

   ```bash
   cp config.example.env config.env
   ```

   Edit `config.env`:

   ```
   VAULT_PATH=/path/to/your/note-vault
   WHISPER_MODEL_SIZE=large-v3
   WHISPER_DEVICE=cuda
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt        # faster-whisper, for transcription
   pip install -r requirements-dev.txt     # pytest, for running the test suite
   ```

3. Set up automatic git backups for your vault — see
   `docs/note-vault-git-setup.md` for Obsidian Git plugin configuration, and
   `docs/note-vault-transcript-gitignore.md` for keeping raw transcripts out of
   version control.

## Workflow: which tool, when

| Step | Tool | What it does |
|---|---|---|
| New topic | (by hand) | Create `<Course>/Week N/` and the `<NN - Title>.md` note in Obsidian |
| After a lecture recording | `scripts/transcribe.py <audio> <course> <topic>` | Runs faster-whisper locally, writes `transcript_raw.md` |
| After transcribing | `lecture-enhance` skill | Merges the transcript into the note, marked `[FROM LECTURE]` |
| After slides are posted | `slides-enhance` skill | Adds what slides cover that notes miss, flags contradictions |
| When a note has got long | `cleanup` skill | Rewrites the note down to note level and rebuilds its glossary section. Destructive; git is the undo |
| To refresh only the glossary | `begreber-extract` skill | Rebuilds a topic's section of `<Course>/Begreber.md` |
| Closer to exam time | `review-notes` skill | Generates exam-style questions into `exam_questions.md` |
| Any time | `flashcards-make` skill | Generates spaced-repetition cards into `flashcards.md` |

All skills are run manually, one at a time, from within Claude Code — there's no
auto-chaining pipeline.

## Running tests

```bash
python3 -m pytest -v
bash deprecated/test_makenotes.sh   # deprecated tool, kept working
```
