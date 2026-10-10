import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from progress import scan_topics
from transcribe import find_note, main, transcribe_audio, write_transcript


def _write_note(vault_path, semester, course, week, topic):
    week_dir = vault_path / semester / course / week
    week_dir.mkdir(parents=True, exist_ok=True)
    note_path = week_dir / f"{topic}.md"
    note_path.write_text("note body", encoding="utf-8")
    return note_path


def test_find_note_globs_week_folders(tmp_path):
    note_path = _write_note(tmp_path, "3. Semester", "Course", "Week 2", "03 - Topic")

    assert find_note(tmp_path, "3. Semester", "Course", "03 - Topic") == note_path


def test_find_note_raises_when_no_note_matches(tmp_path):
    _write_note(tmp_path, "3. Semester", "Course", "Week 1", "01 - Other")

    with pytest.raises(FileNotFoundError, match="03 - Topic.md"):
        find_note(tmp_path, "3. Semester", "Course", "03 - Topic")


def test_find_note_raises_when_more_than_one_note_matches(tmp_path):
    _write_note(tmp_path, "3. Semester", "Course", "Week 1", "03 - Topic")
    _write_note(tmp_path, "3. Semester", "Course", "Week 2", "03 - Topic")

    with pytest.raises(ValueError, match="more than one"):
        find_note(tmp_path, "3. Semester", "Course", "03 - Topic")


def test_write_transcript_writes_to_note_sibling_folder(tmp_path):
    note_path = _write_note(tmp_path, "3. Semester", "Course", "Week 2", "03 - Topic")

    output_path = write_transcript(note_path, "hello world")

    assert output_path == tmp_path / "3. Semester" / "Course" / "Week 2" / "03 - Topic" / "transcript_raw.md"
    assert output_path.read_text() == "# 03 - Topic - Raw Transcript\n\nhello world\n"


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


def test_transcribe_audio_passes_language_when_given(monkeypatch, tmp_path):
    fake_model = MagicMock()
    fake_model.transcribe.return_value = ([], None)

    fake_whisper_module = MagicMock()
    fake_whisper_module.WhisperModel.return_value = fake_model
    monkeypatch.setitem(sys.modules, "faster_whisper", fake_whisper_module)

    audio_path = tmp_path / "lecture.wav"
    audio_path.write_bytes(b"")

    transcribe_audio(audio_path, "large-v3", "cuda", language="da")

    fake_model.transcribe.assert_called_once_with(str(audio_path), language="da")


def test_main_writes_transcript_using_config(monkeypatch, tmp_path, capsys):
    vault_path = tmp_path / "vault"
    _write_note(vault_path, "3. Semester", "TestCourse", "Week 1", "01 - TestTopic")
    config_file = tmp_path / "config.env"
    config_file.write_text(f"VAULT_PATH={vault_path}\nSEMESTER=3. Semester\nWHISPER_MODEL_SIZE=tiny\nWHISPER_DEVICE=cpu\n")
    monkeypatch.setenv("CONFIG_PATH", str(config_file))

    def fake_transcribe_audio(audio_path, model_size, device, language):
        assert model_size == "tiny"
        assert device == "cpu"
        return "mocked transcript"

    monkeypatch.setattr("transcribe.transcribe_audio", fake_transcribe_audio)

    audio_path = tmp_path / "lecture.wav"
    audio_path.write_bytes(b"")

    main([str(audio_path), "TestCourse", "01 - TestTopic"])

    output_path = vault_path / "3. Semester" / "TestCourse" / "Week 1" / "01 - TestTopic" / "transcript_raw.md"
    assert output_path.read_text() == "# 01 - TestTopic - Raw Transcript\n\nmocked transcript\n"
    assert "Wrote transcript to" in capsys.readouterr().out
    # The transcript lands where progress.py (and lecture-enhance) look for it.
    assert scan_topics(vault_path, "3. Semester")[0].transcribed is True


def test_main_semester_flag_overrides_config(monkeypatch, tmp_path):
    vault_path = tmp_path / "vault"
    _write_note(vault_path, "4. Semester", "TestCourse", "Week 1", "01 - TestTopic")
    config_file = tmp_path / "config.env"
    config_file.write_text(f"VAULT_PATH={vault_path}\nSEMESTER=3. Semester\n")
    monkeypatch.setenv("CONFIG_PATH", str(config_file))
    monkeypatch.setattr("transcribe.transcribe_audio", lambda *args: "mocked transcript")

    audio_path = tmp_path / "lecture.wav"
    audio_path.write_bytes(b"")

    main([str(audio_path), "TestCourse", "01 - TestTopic", "--semester", "4. Semester"])

    assert (vault_path / "4. Semester" / "TestCourse" / "Week 1" / "01 - TestTopic" / "transcript_raw.md").exists()


def test_main_missing_semester_exits_cleanly(monkeypatch, tmp_path, capsys):
    config_file = tmp_path / "config.env"
    config_file.write_text(f"VAULT_PATH={tmp_path / 'vault'}\n")
    monkeypatch.setenv("CONFIG_PATH", str(config_file))

    audio_path = tmp_path / "lecture.wav"
    audio_path.write_bytes(b"")

    with pytest.raises(SystemExit) as e:
        main([str(audio_path), "TestCourse", "01 - TestTopic"])

    assert e.value.code == 1
    assert "SEMESTER" in capsys.readouterr().err


def test_main_unknown_note_exits_without_calling_transcribe(monkeypatch, tmp_path, capsys):
    config_file = tmp_path / "config.env"
    config_file.write_text(f"VAULT_PATH={tmp_path / 'vault'}\nSEMESTER=3. Semester\n")
    monkeypatch.setenv("CONFIG_PATH", str(config_file))

    def fail_if_called(*args, **kwargs):
        raise AssertionError("transcribe_audio should not run when the note can't be found")

    monkeypatch.setattr("transcribe.transcribe_audio", fail_if_called)

    audio_path = tmp_path / "lecture.wav"
    audio_path.write_bytes(b"")

    with pytest.raises(SystemExit) as e:
        main([str(audio_path), "TestCourse", "01 - TestTopic"])

    assert e.value.code == 1
    assert "01 - TestTopic.md" in capsys.readouterr().err


def test_cli_missing_config_file_handles_gracefully(tmp_path):
    missing_config_file = tmp_path / "does_not_exist.env"
    audio_path = tmp_path / "lecture.wav"
    audio_path.write_bytes(b"")

    script = Path(__file__).resolve().parent.parent / "scripts" / "transcribe.py"
    result = subprocess.run(
        [sys.executable, str(script), str(audio_path), "TestCourse", "TestTopic"],
        capture_output=True,
        text=True,
        env={**os.environ, "CONFIG_PATH": str(missing_config_file)},
    )

    assert result.returncode == 1
    assert "Traceback" not in result.stderr


def test_main_missing_audio_file_exits_cleanly_without_calling_transcribe(monkeypatch, tmp_path, capsys):
    vault_path = tmp_path / "vault"
    config_file = tmp_path / "config.env"
    config_file.write_text(f"VAULT_PATH={vault_path}\n")
    monkeypatch.setenv("CONFIG_PATH", str(config_file))

    def fail_if_called(*args, **kwargs):
        raise AssertionError("transcribe_audio should not be called for a missing audio file")

    monkeypatch.setattr("transcribe.transcribe_audio", fail_if_called)

    missing_audio_path = tmp_path / "does_not_exist.wav"

    try:
        main([str(missing_audio_path), "TestCourse", "TestTopic"])
        raised = False
    except SystemExit as e:
        raised = True
        assert e.code == 1

    assert raised
    assert "Audio file not found" in capsys.readouterr().err
