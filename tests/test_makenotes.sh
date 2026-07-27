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
