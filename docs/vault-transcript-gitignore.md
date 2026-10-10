# Vault: ignore raw transcripts

`scripts/transcribe.py` writes a `transcript_raw.md` file into the topic
note's sibling folder. This is a working artifact superseded by the topic
note once the `lecture-enhance` skill runs, so it should not be committed.

Add this line to the `.gitignore` at your vault root (create the file if it doesn't
exist):

```
transcript_raw.md
```
