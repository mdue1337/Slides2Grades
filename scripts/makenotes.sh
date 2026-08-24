#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_PATH="$(python3 "$SCRIPT_DIR/config.py" VAULT_PATH)"

read -p "Enter course name: " course
read -p "Enter topic name: " topic

if [ -z "$course" ] || [ -z "$topic" ]; then
    echo "Course and topic are both required." >&2
    exit 1
fi

course_dir="$VAULT_PATH/$course"
topic_dir="$course_dir/$topic"

# Folder structure only. Note bodies come from the vault's Obsidian template
# (_templates/topic-note.md), and every skill creates its own output file on
# first run, so nothing here writes notes.md/exercises.md/exam_questions.md/
# flashcards.md.
mkdir -p "$course_dir/Literature" "$course_dir/Images" "$topic_dir"

# begreber.md is course-level, not topic-level: one glossary per course is what
# makes it reviewable as a set before an exam.
begreber="$course_dir/begreber.md"
if [ ! -f "$begreber" ]; then
    printf '# Begreber — %s\n' "$course" > "$begreber"
fi

echo "Created $topic_dir"
echo "Course scaffold: $course_dir/{Literature,Images}, $begreber"
