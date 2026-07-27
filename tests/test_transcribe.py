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
