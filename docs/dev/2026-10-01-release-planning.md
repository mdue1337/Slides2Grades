# Release planning (discuss later)

Rough notes from a conversation on 2026-10-01, for picking back up — nothing here
is decided.

## Context

Notes2Knowledge shipped (companion read-only quiz tool, see its README). Idle
thought afterward: how would Slides2Grades + Notes2Knowledge ever get released
for other people to use, not just this one vault?

## Recommendation discussed: dogfood before packaging

Run both tools against the real vault for a few weeks first — confirm quiz
quality, the written/oral exam_type split, and whether struggle-tracking
actually gives useful signal — before locking any public API. Notes2Knowledge's
own design spec already marks "packaging/distribution" out of scope for v1,
which lines up with this.

## Release path options (lightest to heaviest)

1. **Public repo + good README (mostly already done).** Mark both repos as
   GitHub template repos ("Use this template" button) so others clone straight
   into their own vault setup. No packaging work.
2. **Document the vault convention as a contract.** Right now `Week N/`
   folders, `.courseinfo.yaml`, `Begreber.md`, etc. are just "whatever this
   vault happens to do." Releasing means writing that convention down as
   something other people's vaults must follow, not implicit tribal knowledge.
3. **pip-installable CLI + versioned skill bundle.** Only worth it if the goal
   is PyPI-style installs instead of git-clone-and-configure. More work, more
   surface to maintain compatibility on.

## Open gap

No LICENSE file in either repo yet — needed before any real release regardless
of which path above gets picked.
