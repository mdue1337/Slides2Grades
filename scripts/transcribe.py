import argparse
import sys
from pathlib import Path

from config import load_config


def transcribe_audio(audio_path: Path, model_size: str, device: str, language: str | None = None) -> str:
    from faster_whisper import WhisperModel  # lazy import: only needed at real transcription time

    model = WhisperModel(model_size, device=device)
    kwargs = {"language": language} if language else {}
    segments, _ = model.transcribe(str(audio_path), **kwargs)
    return "\n".join(segment.text.strip() for segment in segments)


def find_note(vault_path: Path, semester: str, course: str, topic: str) -> Path:
    """Locate <vault>/<semester>/<course>/Week */<topic>.md — the note whose
    sibling folder the transcript belongs in."""
    course_dir = vault_path / semester / course
    matches = sorted(week / f"{topic}.md" for week in course_dir.glob("Week */") if (week / f"{topic}.md").is_file())
    if not matches:
        raise FileNotFoundError(f"No note '{topic}.md' found in any Week folder under {course_dir}")
    if len(matches) > 1:
        raise ValueError(f"'{topic}.md' found in more than one Week folder: " + ", ".join(str(m) for m in matches))
    return matches[0]


def write_transcript(note_path: Path, text: str) -> Path:
    topic = note_path.stem
    topic_dir = note_path.parent / topic
    topic_dir.mkdir(exist_ok=True)
    output_path = topic_dir / "transcript_raw.md"
    output_path.write_text(f"# {topic} - Raw Transcript\n\n{text}\n", encoding="utf-8")
    return output_path


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Transcribe a lecture recording with faster-whisper")
    parser.add_argument("audio_path", type=Path)
    parser.add_argument("course")
    parser.add_argument("topic", help='Note filename without .md, e.g. "05 - Diskrete stokastiske variabler og PMF"')
    parser.add_argument("--semester", help="Semester folder under the vault; defaults to config SEMESTER")
    parser.add_argument("--language", help="Override the source language (e.g. 'da'); defaults to config WHISPER_LANGUAGE or auto-detect")
    args = parser.parse_args(argv)

    try:
        config = load_config()
        vault_path = Path(config["VAULT_PATH"])
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except KeyError:
        print("Missing config key: VAULT_PATH", file=sys.stderr)
        sys.exit(1)

    model_size = config.get("WHISPER_MODEL_SIZE", "large-v3")
    device = config.get("WHISPER_DEVICE", "cuda")
    language = args.language or config.get("WHISPER_LANGUAGE")

    if not args.audio_path.exists():
        print(f"Audio file not found: {args.audio_path}", file=sys.stderr)
        sys.exit(1)

    semester = args.semester or config.get("SEMESTER")
    if not semester:
        print("No semester given: pass --semester or set SEMESTER in config.env", file=sys.stderr)
        sys.exit(1)

    # Resolve the note before transcribing, so a typo fails fast instead of after a long run.
    try:
        note_path = find_note(vault_path, semester, args.course, args.topic)
    except (FileNotFoundError, ValueError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    text = transcribe_audio(args.audio_path, model_size, device, language)
    output_path = write_transcript(note_path, text)
    print(f"Wrote transcript to {output_path}")


if __name__ == "__main__":
    main()
