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
