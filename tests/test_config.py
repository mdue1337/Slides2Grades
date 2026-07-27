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


def test_cli_missing_config_file_handles_gracefully(tmp_path):
    missing_config_file = tmp_path / "does_not_exist.env"

    script = Path(__file__).resolve().parent.parent / "scripts" / "config.py"
    result = subprocess.run(
        [sys.executable, str(script), "VAULT_PATH"],
        capture_output=True,
        text=True,
        env={**os.environ, "CONFIG_PATH": str(missing_config_file)},
    )

    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    assert "Config file not found at" in result.stderr
