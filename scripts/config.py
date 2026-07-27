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
    try:
        config = load_config()
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    if key not in config:
        print(f"Missing config key: {key}", file=sys.stderr)
        sys.exit(1)

    print(config[key])


if __name__ == "__main__":
    main()
