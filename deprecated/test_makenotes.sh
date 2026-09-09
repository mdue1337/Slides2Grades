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

fail() { echo "FAIL: $1"; exit 1; }

# Course names in the real vault contain spaces, so the script must quote.
printf 'Test Course\nTest Topic\n' | bash "$REPO_ROOT/deprecated/makenotes.sh"

course_dir="$vault_dir/Test Course"
topic_dir="$course_dir/Test Topic"

for dir in "$topic_dir" "$course_dir/Literature" "$course_dir/Images"; do
    [ -d "$dir" ] || fail "expected directory $dir to exist"
done

begreber="$course_dir/begreber.md"
[ -f "$begreber" ] || fail "expected $begreber to exist"
grep -q "^# Begreber — Test Course$" "$begreber" \
    || fail "expected $begreber to start with '# Begreber — Test Course'"

# Folder structure only: note files are the template's and the skills' job.
for file in notes.md exercises.md exam_questions.md flashcards.md; do
    [ -e "$topic_dir/$file" ] && fail "$file should not be created by makenotes.sh"
done

# A second topic in the same course must not clobber an edited begreber.md.
printf '**Kryds** — appended by hand\n' >> "$begreber"
printf 'Test Course\nSecond Topic\n' | bash "$REPO_ROOT/deprecated/makenotes.sh"

[ -d "$course_dir/Second Topic" ] || fail "expected second topic directory to exist"
grep -q "appended by hand" "$begreber" \
    || fail "second run overwrote existing begreber.md content"

# Empty input is rejected rather than creating a directory at the vault root.
if printf '\n\n' | bash "$REPO_ROOT/deprecated/makenotes.sh" 2>/dev/null; then
    fail "expected empty course/topic input to exit non-zero"
fi

echo "PASS: test_makenotes.sh"
