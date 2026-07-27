# Slides2Grades Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Slides2Grades tooling repo: vault scaffolding, a config-driven local whisper transcription script, and five Claude Code skills that turn lecture materials into Obsidian notes, practice questions, and flashcards.

**Architecture:** A tooling repo (this one) that never stores vault content itself. A gitignored `config.env` points scripts and skills at the separately-managed `note-vault` Obsidian repo. `scripts/config.py` is the single source of truth for reading that config from both Python and bash. `scripts/makenotes.sh` scaffolds new topic folders; `scripts/transcribe.py` runs faster-whisper locally; five `.claude/skills/*/SKILL.md` files do the LLM-driven note enhancement, question generation, and flashcard generation, each reading `STYLEGUIDE.md` for formatting rules.

**Tech Stack:** Bash, Python 3.10+, pytest, faster-whisper, Claude Code project skills.

## Global Constraints

- No hardcoded personal paths or vault content in this repo — everything vault-specific comes from `config.env` (gitignored), matching the config-driven, not-yet-productized approach from the design doc.
- All LLM skills run manually, one at a time — no auto-chaining pipeline between skills.
- Automatic git commits for the vault are handled by the Obsidian Git plugin inside `note-vault`, not by code in this repo.
- Generated vault content must follow `STYLEGUIDE.md`: markdown headers, **bold** key terms, bullet points, code blocks for formulas/code, no inline HTML, UTF-8 encoding, Obsidian `[[wikilinks]]` for cross-topic references.
- Skills never delete or silently overwrite existing vault content — Lecture-Enhance/Slides-Enhance append/annotate; Grill-Notes/Review-Notes/Flashcards-Make append new items and never renumber or remove existing ones.
- `transcript_raw.md` is gitignored inside `note-vault` (documented in Task 2) — it's a working artifact, not durable content.

---

## Task 1: Config loader

**Files:**
- Create: `scripts/config.py`
- Create: `config.example.env`
- Create: `.gitignore`
- Create: `conftest.py`
- Create: `requirements-dev.txt`
- Test: `tests/test_config.py`

**Interfaces:**
- Produces: `load_config(path: Path | None = None) -> dict[str, str]` — raises `FileNotFoundError` if the resolved config file doesn't exist. Path resolution order: explicit `path` arg, then `CONFIG_PATH` env var, then `<repo root>/config.env`.
- Produces: CLI `python3 scripts/config.py KEY` — prints the value of `KEY` to stdout and exits 0, or prints an error to stderr and exits 1 if missing.
- Consumed by: Task 2 (`scripts/makenotes.sh` calls the CLI), Task 4 (`scripts/transcribe.py` imports `load_config`).

- [ ] **Step 1: Install pytest**

```bash
pip3 install --user pytest
```

- [ ] **Step 2: Create `requirements-dev.txt`**

```
pytest
```

- [ ] **Step 3: Create `.gitignore`**

```
config.env
__pycache__/
*.pyc
.pytest_cache/
```

- [ ] **Step 4: Create `config.example.env`**

```
VAULT_PATH=/home/youruser/path/to/note-vault
WHISPER_MODEL_SIZE=large-v3
WHISPER_DEVICE=cuda
```

- [ ] **Step 5: Create `conftest.py`** (repo root, so tests can `import config` / `import transcribe` without packaging)

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
```

- [ ] **Step 6: Write the failing tests**

Create `tests/test_config.py`:

```python
import os
import subprocess
import sys
from pathlib import Path

import pytest

from config import load_config


def test_load_config_parses_key_value_pairs(tmp_path):
    config_file = tmp_path / "config.env"
    config_file.write_text(
        "VAULT_PATH=/tmp/note-vault\n"
        "WHISPER_MODEL_SIZE=large-v3\n"
        "# a comment\n"
        "\n"
        "WHISPER_DEVICE=cuda\n"
    )

    config = load_config(config_file)

    assert config == {
        "VAULT_PATH": "/tmp/note-vault",
        "WHISPER_MODEL_SIZE": "large-v3",
        "WHISPER_DEVICE": "cuda",
    }


def test_load_config_missing_file_raises(tmp_path):
    missing_path = tmp_path / "does_not_exist.env"

    with pytest.raises(FileNotFoundError):
        load_config(missing_path)


def test_load_config_uses_config_path_env_var(tmp_path, monkeypatch):
    config_file = tmp_path / "custom.env"
    config_file.write_text("VAULT_PATH=/tmp/from-env-var\n")
    monkeypatch.setenv("CONFIG_PATH", str(config_file))

    config = load_config()

    assert config == {"VAULT_PATH": "/tmp/from-env-var"}


def test_cli_prints_requested_value(tmp_path):
    config_file = tmp_path / "config.env"
    config_file.write_text("VAULT_PATH=/tmp/note-vault\n")

    script = Path(__file__).resolve().parent.parent / "scripts" / "config.py"
    result = subprocess.run(
        [sys.executable, str(script), "VAULT_PATH"],
        capture_output=True,
        text=True,
        env={**os.environ, "CONFIG_PATH": str(config_file)},
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "/tmp/note-vault"


def test_cli_missing_key_exits_nonzero(tmp_path):
    config_file = tmp_path / "config.env"
    config_file.write_text("VAULT_PATH=/tmp/note-vault\n")

    script = Path(__file__).resolve().parent.parent / "scripts" / "config.py"
    result = subprocess.run(
        [sys.executable, str(script), "MISSING_KEY"],
        capture_output=True,
        text=True,
        env={**os.environ, "CONFIG_PATH": str(config_file)},
    )

    assert result.returncode == 1
```

- [ ] **Step 7: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'config'` (the file doesn't exist yet).

- [ ] **Step 8: Write `scripts/config.py`**

```python
import os
import sys
from pathlib import Path


def load_config(path: Path | None = None) -> dict[str, str]:
    if path is None:
        env_override = os.environ.get("CONFIG_PATH")
        path = Path(env_override) if env_override else Path(__file__).resolve().parent.parent / "config.env"

    if not path.exists():
        raise FileNotFoundError(
            f"Config file not found at {path}. Copy config.example.env to config.env and fill in your values."
        )

    config: dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        config[key.strip()] = value.strip()
    return config


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: config.py KEY", file=sys.stderr)
        sys.exit(1)

    key = sys.argv[1]
    config = load_config()

    if key not in config:
        print(f"Missing config key: {key}", file=sys.stderr)
        sys.exit(1)

    print(config[key])


if __name__ == "__main__":
    main()
```

- [ ] **Step 9: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_config.py -v`
Expected: PASS (5 tests)

- [ ] **Step 10: Commit**

`STYLEGUIDE.md` already exists in the working tree from earlier project setup but has never been committed; every skill in this plan reads it, so it's included here as foundational content alongside the config loader.

```bash
git add scripts/config.py config.example.env .gitignore conftest.py requirements-dev.txt tests/test_config.py STYLEGUIDE.md
git commit -m "feat: add config.env loader for scripts and skills"
```

---

## Task 2: Vault scaffolding script

**Files:**
- Create: `scripts/makenotes.sh`
- Delete: `makenotes` (superseded by `scripts/makenotes.sh`)
- Create: `docs/note-vault-transcript-gitignore.md`
- Test: `tests/test_makenotes.sh`

**Interfaces:**
- Consumes: `scripts/config.py` CLI (`python3 scripts/config.py VAULT_PATH`) from Task 1.
- Produces: running `scripts/makenotes.sh` prompts for course and topic, then creates `<VAULT_PATH>/<course>/<topic>/{notes.md,exercises.md,exam_questions.md,flashcards.md}`, each seeded with `# <topic>` if not already present.

- [ ] **Step 1: Write the failing test**

Create `tests/test_makenotes.sh`:

```bash
#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

work_dir="$(mktemp -d)"
trap 'rm -rf "$work_dir"' EXIT

vault_dir="$work_dir/vault"
mkdir -p "$vault_dir"

config_file="$work_dir/config.env"
echo "VAULT_PATH=$vault_dir" > "$config_file"
export CONFIG_PATH="$config_file"

printf 'TestCourse\nTestTopic\n' | bash "$REPO_ROOT/scripts/makenotes.sh"

topic_dir="$vault_dir/TestCourse/TestTopic"

for file in notes.md exercises.md exam_questions.md flashcards.md; do
    filepath="$topic_dir/$file"
    if [ ! -f "$filepath" ]; then
        echo "FAIL: expected $filepath to exist"
        exit 1
    fi
    if ! grep -q "^# TestTopic$" "$filepath"; then
        echo "FAIL: expected $filepath to start with '# TestTopic'"
        exit 1
    fi
done

echo "PASS: test_makenotes.sh"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `chmod +x tests/test_makenotes.sh && bash tests/test_makenotes.sh`
Expected: FAIL — `scripts/makenotes.sh: No such file or directory`

- [ ] **Step 3: Write `scripts/makenotes.sh`**

```bash
#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_PATH="$(python3 "$SCRIPT_DIR/config.py" VAULT_PATH)"

read -p "Enter course name: " course
read -p "Enter topic name: " topic

target_dir="$VAULT_PATH/$course/$topic"
mkdir -p "$target_dir"

for file in notes.md exercises.md exam_questions.md flashcards.md; do
    filepath="$target_dir/$file"
    if [ ! -f "$filepath" ]; then
        printf '# %s\n' "$topic" > "$filepath"
    fi
done

echo "Created $target_dir"
```

- [ ] **Step 4: Make it executable and delete the old script**

The old `makenotes` file is untracked (never committed), so it's removed directly rather than with `git rm`.

```bash
chmod +x scripts/makenotes.sh
rm makenotes
```

- [ ] **Step 5: Run test to verify it passes**

Run: `bash tests/test_makenotes.sh`
Expected: `PASS: test_makenotes.sh`

- [ ] **Step 6: Document the `transcript_raw.md` gitignore requirement for `note-vault`**

Create `docs/note-vault-transcript-gitignore.md`:

```markdown
# note-vault: ignore raw transcripts

`scripts/transcribe.py` writes a `transcript_raw.md` file into each topic
folder it processes. This is a working artifact superseded by `notes.md`
once the `lecture-enhance` skill runs, so it should not be committed.

Add this line to `note-vault/.gitignore` (create the file if it doesn't
exist):

```
transcript_raw.md
```
```

- [ ] **Step 7: Commit**

```bash
git add scripts/makenotes.sh tests/test_makenotes.sh docs/note-vault-transcript-gitignore.md
git commit -m "feat: rewrite makenotes as config-driven scripts/makenotes.sh"
```

---

## Task 3: Obsidian Git plugin setup doc

**Files:**
- Create: `docs/note-vault-git-setup.md`

**Interfaces:**
- None — standalone documentation, no code dependencies.

- [ ] **Step 1: Write the setup doc**

Create `docs/note-vault-git-setup.md`:

```markdown
# Setting Up Automatic Git Saves for note-vault

Slides2Grades does not automate git commits for your Obsidian vault. Instead,
`note-vault` auto-saves itself using the Obsidian Git community plugin,
configured directly in Obsidian.

## Setup

1. In Obsidian, open **Settings → Community plugins → Browse**, search for
   "Obsidian Git", and install it.
2. Enable the plugin.
3. Open **Settings → Obsidian Git** and configure:
   - **Vault backup interval (minutes)**: `15`
   - **Auto pull interval (minutes)**: `15`
   - **Commit message**: `vault backup: {{date}}`
   - **Auto backup after file change**: enabled, with a short debounce so it
     doesn't commit on every keystroke
   - **Push on backup**: enabled, so commits are also pushed to GitHub
     automatically
4. Confirm `note-vault` has a configured remote (`git remote -v` inside the
   vault folder) and that git credentials (SSH key or a GitHub PAT via the
   credential helper) are already set up on this machine — the plugin pushes
   using your existing git config, it doesn't manage credentials itself.
5. Make a small test edit in any note, then either wait for the configured
   interval or run the plugin's "Backup and push" command from Obsidian's
   command palette. Confirm the commit shows up by running `git log -1`
   inside `note-vault`.
```

- [ ] **Step 2: Verify the doc covers the required settings**

Run: `grep -c "Push on backup" docs/note-vault-git-setup.md`
Expected: `1`

- [ ] **Step 3: Commit**

```bash
git add docs/note-vault-git-setup.md
git commit -m "docs: add Obsidian Git plugin setup instructions for note-vault"
```

---

## Task 4: Transcription script

**Files:**
- Create: `scripts/transcribe.py`
- Create: `requirements.txt`
- Test: `tests/test_transcribe.py`

**Interfaces:**
- Consumes: `load_config` from `scripts/config.py` (Task 1).
- Produces: `transcribe_audio(audio_path: Path, model_size: str, device: str) -> str` — joined transcript text.
- Produces: `write_transcript(vault_path: Path, course: str, topic: str, text: str) -> Path` — writes `<vault_path>/<course>/<topic>/transcript_raw.md` and returns its path.
- Produces: `main(argv: list[str] | None = None) -> None` — CLI entry point, args `audio_path course topic`.

`faster-whisper` is only imported lazily inside `transcribe_audio`, so the test suite doesn't need it installed (tests mock `sys.modules["faster_whisper"]`). It's still required at runtime on the machine actually doing transcription (the 4070 box).

- [ ] **Step 1: Add `requirements.txt`**

```
faster-whisper
```

- [ ] **Step 2: Write the failing tests**

Create `tests/test_transcribe.py`:

```python
import sys
from pathlib import Path
from unittest.mock import MagicMock

from transcribe import main, transcribe_audio, write_transcript


def test_write_transcript_creates_file_with_expected_content(tmp_path):
    vault_path = tmp_path / "vault"

    output_path = write_transcript(vault_path, "TestCourse", "TestTopic", "hello world")

    assert output_path == vault_path / "TestCourse" / "TestTopic" / "transcript_raw.md"
    assert output_path.read_text() == "# TestTopic - Raw Transcript\n\nhello world\n"


def test_transcribe_audio_joins_segment_text(monkeypatch, tmp_path):
    fake_segment_1 = MagicMock(text=" Hello ")
    fake_segment_2 = MagicMock(text=" world ")

    fake_model = MagicMock()
    fake_model.transcribe.return_value = ([fake_segment_1, fake_segment_2], None)

    fake_whisper_module = MagicMock()
    fake_whisper_module.WhisperModel.return_value = fake_model
    monkeypatch.setitem(sys.modules, "faster_whisper", fake_whisper_module)

    audio_path = tmp_path / "lecture.wav"
    audio_path.write_bytes(b"")

    result = transcribe_audio(audio_path, "large-v3", "cuda")

    assert result == "Hello\nworld"
    fake_whisper_module.WhisperModel.assert_called_once_with("large-v3", device="cuda")
    fake_model.transcribe.assert_called_once_with(str(audio_path))


def test_main_writes_transcript_using_config(monkeypatch, tmp_path, capsys):
    vault_path = tmp_path / "vault"
    config_file = tmp_path / "config.env"
    config_file.write_text(f"VAULT_PATH={vault_path}\nWHISPER_MODEL_SIZE=tiny\nWHISPER_DEVICE=cpu\n")
    monkeypatch.setenv("CONFIG_PATH", str(config_file))

    def fake_transcribe_audio(audio_path, model_size, device):
        assert model_size == "tiny"
        assert device == "cpu"
        return "mocked transcript"

    monkeypatch.setattr("transcribe.transcribe_audio", fake_transcribe_audio)

    audio_path = tmp_path / "lecture.wav"
    audio_path.write_bytes(b"")

    main([str(audio_path), "TestCourse", "TestTopic"])

    output_path = vault_path / "TestCourse" / "TestTopic" / "transcript_raw.md"
    assert output_path.read_text() == "# TestTopic - Raw Transcript\n\nmocked transcript\n"
    assert "Wrote transcript to" in capsys.readouterr().out
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_transcribe.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'transcribe'`

- [ ] **Step 4: Write `scripts/transcribe.py`**

```python
import argparse
from pathlib import Path

from config import load_config


def transcribe_audio(audio_path: Path, model_size: str, device: str) -> str:
    from faster_whisper import WhisperModel  # lazy import: only needed at real transcription time

    model = WhisperModel(model_size, device=device)
    segments, _ = model.transcribe(str(audio_path))
    return "\n".join(segment.text.strip() for segment in segments)


def write_transcript(vault_path: Path, course: str, topic: str, text: str) -> Path:
    topic_dir = vault_path / course / topic
    topic_dir.mkdir(parents=True, exist_ok=True)
    output_path = topic_dir / "transcript_raw.md"
    output_path.write_text(f"# {topic} - Raw Transcript\n\n{text}\n")
    return output_path


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Transcribe a lecture recording with faster-whisper")
    parser.add_argument("audio_path", type=Path)
    parser.add_argument("course")
    parser.add_argument("topic")
    args = parser.parse_args(argv)

    config = load_config()
    vault_path = Path(config["VAULT_PATH"])
    model_size = config.get("WHISPER_MODEL_SIZE", "large-v3")
    device = config.get("WHISPER_DEVICE", "cuda")

    text = transcribe_audio(args.audio_path, model_size, device)
    output_path = write_transcript(vault_path, args.course, args.topic, text)
    print(f"Wrote transcript to {output_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_transcribe.py -v`
Expected: PASS (3 tests)

- [ ] **Step 6: Commit**

```bash
git add scripts/transcribe.py requirements.txt tests/test_transcribe.py
git commit -m "feat: add faster-whisper transcription script"
```

---

## Task 5: Lecture-Enhance skill + shared fixtures

**Files:**
- Create: `.claude/skills/lecture-enhance/SKILL.md`
- Create: `tests/fixtures/sample_topic/notes.md`
- Create: `tests/fixtures/sample_topic/transcript_raw.md`
- Create: `tests/fixtures/sample_topic/slides.md`
- Create: `tests/fixtures/sample_topic/exercises.md`

**Interfaces:**
- Produces: shared fixtures under `tests/fixtures/sample_topic/`, consumed by Tasks 6-9.
- Produces: the `lecture-enhance` Claude Code skill, invoked with args `<course> <topic>`.

- [ ] **Step 1: Create the shared fixtures**

Create `tests/fixtures/sample_topic/notes.md`:

```markdown
# Binary Search Trees

## Definition
A **binary search tree (BST)** is a binary tree where each node's left
subtree contains only values less than the node, and the right subtree
contains only values greater than the node.

## Operations
- **Insert**: O(log n) average, O(n) worst case
- **Search**: O(log n) average, O(n) worst case
- **Delete**: O(log n) average, O(n) worst case

See also [[Balanced Trees]].
```

Create `tests/fixtures/sample_topic/transcript_raw.md`:

```markdown
# BST Lecture - Raw Transcript

so today we're going to talk about binary search trees um so a BST is
basically defined by the invariant that for every node the left subtree is
smaller and the right subtree is bigger okay um one thing i didn't put in
the slides is that if you insert values in sorted order into a BST it
degenerates into a linked list and your operations become O(n) instead of
O(log n), that's why we care about self-balancing trees like AVL and
red-black trees um yeah so that's the main gotcha with plain BSTs
```

Create `tests/fixtures/sample_topic/slides.md` (stand-in for a real PDF/PPTX slide deck — the skill reads actual slide files directly, this fixture just needs to be readable text for verification):

```markdown
# Slide 4: BST Complexity

- Search: O(log n) average
- Delete: O(log n) always (assumes self-balancing tree)
- Diagram: an unbalanced BST built from sorted input degenerates into a
  linked list
```

Create `tests/fixtures/sample_topic/exercises.md`:

```markdown
# Binary Search Trees

## Question 1 [Easy]
**Q**: What invariant defines a binary search tree?
**A**: For every node, all values in the left subtree are smaller than the
node's value, and all values in the right subtree are larger.
```

- [ ] **Step 2: Write `.claude/skills/lecture-enhance/SKILL.md`**

```markdown
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
  empty)

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
```

- [ ] **Step 3: Manually verify the skill**

```bash
mkdir -p /tmp/s2g-scratch-vault/DemoCourse/DemoTopic
cp tests/fixtures/sample_topic/notes.md tests/fixtures/sample_topic/transcript_raw.md \
   /tmp/s2g-scratch-vault/DemoCourse/DemoTopic/
printf 'VAULT_PATH=/tmp/s2g-scratch-vault\n' > config.env
```

Invoke the skill via the Skill tool: `skill="lecture-enhance"`, `args="DemoCourse DemoTopic"`.

Then verify:

```bash
grep -q "FROM LECTURE" /tmp/s2g-scratch-vault/DemoCourse/DemoTopic/notes.md && echo "PASS: has FROM LECTURE marker"
grep -qi "AVL\|red-black" /tmp/s2g-scratch-vault/DemoCourse/DemoTopic/notes.md && echo "PASS: captured self-balancing detail"
grep -q "binary search tree (BST)" /tmp/s2g-scratch-vault/DemoCourse/DemoTopic/notes.md && echo "PASS: original content preserved"
```

Expected: all three PASS lines print.

- [ ] **Step 4: Clean up scratch state**

```bash
rm -f config.env
rm -rf /tmp/s2g-scratch-vault
```

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/lecture-enhance/SKILL.md tests/fixtures/sample_topic/
git commit -m "feat: add lecture-enhance skill and shared vault fixtures"
```

---

## Task 6: Slides-Enhance skill

**Files:**
- Create: `.claude/skills/slides-enhance/SKILL.md`

**Interfaces:**
- Consumes: `tests/fixtures/sample_topic/{notes.md,slides.md}` from Task 5.
- Produces: the `slides-enhance` Claude Code skill, invoked with args `<course> <topic> <path to slides>`.

- [ ] **Step 1: Write `.claude/skills/slides-enhance/SKILL.md`**

```markdown
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
```

- [ ] **Step 2: Manually verify the skill**

```bash
mkdir -p /tmp/s2g-scratch-vault/DemoCourse/DemoTopic
cp tests/fixtures/sample_topic/notes.md tests/fixtures/sample_topic/slides.md \
   /tmp/s2g-scratch-vault/DemoCourse/DemoTopic/
printf 'VAULT_PATH=/tmp/s2g-scratch-vault\n' > config.env
```

Invoke the skill via the Skill tool: `skill="slides-enhance"`,
`args="DemoCourse DemoTopic /tmp/s2g-scratch-vault/DemoCourse/DemoTopic/slides.md"`.

The fixture notes.md says Delete is "O(log n) average, O(n) worst case";
the fixture slides.md says Delete is "O(log n) always (assumes
self-balancing tree)" — a deliberate contradiction to exercise the
`[!CAUTION]` path.

```bash
grep -q "\[!CAUTION\]" /tmp/s2g-scratch-vault/DemoCourse/DemoTopic/notes.md && echo "PASS: flagged the contradiction"
grep -q "binary search tree (BST)" /tmp/s2g-scratch-vault/DemoCourse/DemoTopic/notes.md && echo "PASS: original content preserved"
```

Expected: both PASS lines print.

- [ ] **Step 3: Clean up scratch state**

```bash
rm -f config.env
rm -rf /tmp/s2g-scratch-vault
```

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/slides-enhance/SKILL.md
git commit -m "feat: add slides-enhance skill"
```

---

## Task 7: Grill-Notes skill

**Files:**
- Create: `.claude/skills/grill-notes/SKILL.md`

**Interfaces:**
- Consumes: `tests/fixtures/sample_topic/notes.md` from Task 5.
- Produces: the `grill-notes` Claude Code skill, invoked with args `<course> <topic>`.

- [ ] **Step 1: Write `.claude/skills/grill-notes/SKILL.md`**

```markdown
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

5. Append new questions to the end of `exercises.md` (create it with a
   `# <Topic>` header first if it doesn't exist). Never delete or renumber
   existing questions — continue numbering from the highest existing
   question number.

## Output

Write the updated content to `exercises.md`.
```

- [ ] **Step 2: Manually verify the skill**

```bash
mkdir -p /tmp/s2g-scratch-vault/DemoCourse/DemoTopic
cp tests/fixtures/sample_topic/notes.md /tmp/s2g-scratch-vault/DemoCourse/DemoTopic/
printf 'VAULT_PATH=/tmp/s2g-scratch-vault\n' > config.env
```

Invoke the skill via the Skill tool: `skill="grill-notes"`,
`args="DemoCourse DemoTopic"`.

```bash
grep -q "## Question 1" /tmp/s2g-scratch-vault/DemoCourse/DemoTopic/exercises.md && echo "PASS: has question 1"
grep -qE "\[Easy\]|\[Medium\]|\[Hard\]" /tmp/s2g-scratch-vault/DemoCourse/DemoTopic/exercises.md && echo "PASS: has difficulty tags"
grep -q "\*\*A\*\*:" /tmp/s2g-scratch-vault/DemoCourse/DemoTopic/exercises.md && echo "PASS: has answers"
```

Expected: all three PASS lines print.

- [ ] **Step 3: Clean up scratch state**

```bash
rm -f config.env
rm -rf /tmp/s2g-scratch-vault
```

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/grill-notes/SKILL.md
git commit -m "feat: add grill-notes skill"
```

---

## Task 8: Review-Notes skill

**Files:**
- Create: `.claude/skills/review-notes/SKILL.md`

**Interfaces:**
- Consumes: `tests/fixtures/sample_topic/{notes.md,exercises.md}` from Task 5.
- Produces: the `review-notes` Claude Code skill, invoked with args `<course> <topic>`.

- [ ] **Step 1: Write `.claude/skills/review-notes/SKILL.md`**

```markdown
---
name: review-notes
description: Generate exam-style practice questions from a topic's notes.md and exercises.md into exam_questions.md, calibrated to past performance. Use closer to exam time for a topic.
---

# Review-Notes

Generates exam-format practice questions from `notes.md` and `exercises.md`
for one topic into `exam_questions.md`.

## Inputs

- `<vault>/<Course>/<Topic>/notes.md`
- `<vault>/<Course>/<Topic>/exercises.md` (if present) — treat questions
  here as already-covered material, not to be repeated verbatim

Resolve `<vault>` via `python3 scripts/config.py VAULT_PATH`.

## What to do

1. Read both input files.
2. Write exam-style questions varying in format: definition, application,
   and synthesis questions.
3. If `exercises.md` tests the same concept repeatedly, weight new
   questions toward concepts from `notes.md` that aren't well covered yet.
4. Format each question per `STYLEGUIDE.md`:

```
## Question [Difficulty] #tags
**Format**: [Multiple Choice / Short Answer / Essay]
**Q**: [Question]
**Suggested Answer**: [Answer]
```

5. Use topic-relevant `#tags` (e.g. `#binary-search-trees`) so questions
   are filterable in Obsidian.
6. Append to the end of `exam_questions.md` (create it with a `# <Topic>`
   header first if it doesn't exist). Never delete existing questions.

## Output

Write the updated content to `exam_questions.md`.
```

- [ ] **Step 2: Manually verify the skill**

```bash
mkdir -p /tmp/s2g-scratch-vault/DemoCourse/DemoTopic
cp tests/fixtures/sample_topic/notes.md tests/fixtures/sample_topic/exercises.md \
   /tmp/s2g-scratch-vault/DemoCourse/DemoTopic/
printf 'VAULT_PATH=/tmp/s2g-scratch-vault\n' > config.env
```

Invoke the skill via the Skill tool: `skill="review-notes"`,
`args="DemoCourse DemoTopic"`.

```bash
grep -q "\*\*Format\*\*:" /tmp/s2g-scratch-vault/DemoCourse/DemoTopic/exam_questions.md && echo "PASS: has format field"
grep -q "#" /tmp/s2g-scratch-vault/DemoCourse/DemoTopic/exam_questions.md && echo "PASS: has a tag"
grep -q "\*\*Suggested Answer\*\*:" /tmp/s2g-scratch-vault/DemoCourse/DemoTopic/exam_questions.md && echo "PASS: has suggested answers"
```

Expected: all three PASS lines print.

- [ ] **Step 3: Clean up scratch state**

```bash
rm -f config.env
rm -rf /tmp/s2g-scratch-vault
```

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/review-notes/SKILL.md
git commit -m "feat: add review-notes skill"
```

---

## Task 9: Flashcards-Make skill

**Files:**
- Create: `.claude/skills/flashcards-make/SKILL.md`

**Interfaces:**
- Consumes: `tests/fixtures/sample_topic/notes.md` from Task 5.
- Produces: the `flashcards-make` Claude Code skill, invoked with args `<course> <topic>`.

- [ ] **Step 1: Write `.claude/skills/flashcards-make/SKILL.md`**

```markdown
---
name: flashcards-make
description: Generate spaced-repetition flashcards from a topic's notes.md into flashcards.md. Use any time after notes.md has meaningful content for a topic.
---

# Flashcards-Make

Generates flashcards from `notes.md` for one topic into `flashcards.md`.

## Inputs

- `<vault>/<Course>/<Topic>/notes.md`

Resolve `<vault>` via `python3 scripts/config.py VAULT_PATH`.

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
   exist).

## Output

Write the updated content to `flashcards.md`.
```

- [ ] **Step 2: Manually verify the skill**

```bash
mkdir -p /tmp/s2g-scratch-vault/DemoCourse/DemoTopic
cp tests/fixtures/sample_topic/notes.md /tmp/s2g-scratch-vault/DemoCourse/DemoTopic/
printf 'VAULT_PATH=/tmp/s2g-scratch-vault\n' > config.env
```

Invoke the skill via the Skill tool: `skill="flashcards-make"`,
`args="DemoCourse DemoTopic"`.

```bash
grep -qE "\[Easy\]|\[Medium\]|\[Hard\]" /tmp/s2g-scratch-vault/DemoCourse/DemoTopic/flashcards.md && echo "PASS: has difficulty tags"
grep -q "|" /tmp/s2g-scratch-vault/DemoCourse/DemoTopic/flashcards.md && echo "PASS: uses Question | Answer format"
```

Expected: both PASS lines print.

- [ ] **Step 3: Clean up scratch state**

```bash
rm -f config.env
rm -rf /tmp/s2g-scratch-vault
```

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/flashcards-make/SKILL.md
git commit -m "feat: add flashcards-make skill"
```
