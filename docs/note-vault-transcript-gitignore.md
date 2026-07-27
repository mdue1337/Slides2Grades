# note-vault: ignore raw transcripts

`scripts/transcribe.py` writes a `transcript_raw.md` file into each topic
folder it processes. This is a working artifact superseded by `notes.md`
once the `lecture-enhance` skill runs, so it should not be committed.

Add this line to `note-vault/.gitignore` (create the file if it doesn't
exist):

```
transcript_raw.md
```
