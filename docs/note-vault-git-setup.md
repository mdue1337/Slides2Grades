# Setting Up Automatic Git Saves for note-vault

Slides2Grades does not automate git commits for your Obsidian vault. Instead,
`note-vault` auto-saves itself using the Obsidian Git community plugin,
configured directly in Obsidian.

## Setup

1. In Obsidian, open **Settings → Community plugins → Browse**, search for
   "Obsidian Git", and install it.
2. Enable the plugin.
3. Open **Settings → Obsidian Git** and configure:
   - **Vault backup interval (minutes)**: `15`
   - **Auto pull interval (minutes)**: `15`
   - **Commit message**: `vault backup: {{date}}`
   - **Auto backup after file change**: enabled, with a short debounce so it
     doesn't commit on every keystroke
   - **Push on backup**: enabled, so commits are also pushed to GitHub
     automatically
4. Confirm `note-vault` has a configured remote (`git remote -v` inside the
   vault folder) and that git credentials (SSH key or a GitHub PAT via the
   credential helper) are already set up on this machine — the plugin pushes
   using your existing git config, it doesn't manage credentials itself.
5. Make a small test edit in any note, then either wait for the configured
   interval or run the plugin's "Backup and push" command from Obsidian's
   command palette. Confirm the commit shows up by running `git log -1`
   inside `note-vault`.
