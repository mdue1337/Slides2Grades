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
