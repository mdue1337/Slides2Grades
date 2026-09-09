from pathlib import Path

from progress import main, render_report, scan_topics


def _write_topic(vault_path, course, week, topic, note_text, transcript=False, flashcards=False, exam=False):
    week_dir = vault_path / course / week
    week_dir.mkdir(parents=True, exist_ok=True)
    (week_dir / f"{topic}.md").write_text(note_text, encoding="utf-8")

    sibling_dir = week_dir / topic
    if transcript or flashcards or exam:
        sibling_dir.mkdir(parents=True, exist_ok=True)
    if transcript:
        (sibling_dir / "transcript_raw.md").write_text("raw", encoding="utf-8")
    if flashcards:
        (sibling_dir / "flashcards.md").write_text("cards", encoding="utf-8")
    if exam:
        (sibling_dir / "exam_questions.md").write_text("questions", encoding="utf-8")


def test_scan_topics_not_transcribed_when_no_sibling_folder(tmp_path):
    vault_path = tmp_path / "vault"
    _write_topic(vault_path, "Course", "Week 1", "01 - Topic", "note body")

    rows = scan_topics(vault_path, "Course")

    assert rows == []  # semester glob is Course/Week */..., not vault-root/Course


def test_scan_topics_covers_all_three_pipeline_states(tmp_path):
    vault_path = tmp_path / "vault"
    semester = "3. Semester"
    _write_topic(vault_path / semester, "Course", "Week 1", "01 - No transcript", "note body")
    _write_topic(
        vault_path / semester,
        "Course",
        "Week 1",
        "02 - Enhanced not cleaned",
        "note body\n[FROM LECTURE] some fact",
        transcript=True,
    )
    _write_topic(
        vault_path / semester,
        "Course",
        "Week 1",
        "03 - Cleaned",
        "note body, no markers left",
        transcript=True,
    )

    rows = scan_topics(vault_path, semester)
    by_topic = {r.topic: r for r in rows}

    not_transcribed = by_topic["01 - No transcript"]
    assert (not_transcribed.transcribed, not_transcribed.enhanced, not_transcribed.cleaned) == (False, False, False)

    enhanced_only = by_topic["02 - Enhanced not cleaned"]
    assert (enhanced_only.transcribed, enhanced_only.enhanced, enhanced_only.cleaned) == (True, True, False)

    cleaned = by_topic["03 - Cleaned"]
    assert (cleaned.transcribed, cleaned.enhanced, cleaned.cleaned) == (True, True, True)


def test_scan_topics_detects_flashcards_and_exam_questions(tmp_path):
    vault_path = tmp_path / "vault"
    semester = "3. Semester"
    _write_topic(
        vault_path / semester,
        "Course",
        "Week 1",
        "01 - Topic",
        "note body",
        transcript=True,
        flashcards=True,
        exam=True,
    )

    rows = scan_topics(vault_path, semester)

    assert rows[0].has_flashcards is True
    assert rows[0].has_exam_questions is True


def test_scan_topics_sorts_by_course_then_week_then_topic(tmp_path):
    vault_path = tmp_path / "vault"
    semester = "3. Semester"
    _write_topic(vault_path / semester, "B Course", "Week 1", "01 - X", "note")
    _write_topic(vault_path / semester, "A Course", "Week 10", "02 - Y", "note")
    _write_topic(vault_path / semester, "A Course", "Week 2", "01 - Z", "note")

    rows = scan_topics(vault_path, semester)

    assert [(r.course, r.week, r.topic) for r in rows] == [
        ("A Course", 2, "01 - Z"),
        ("A Course", 10, "02 - Y"),
        ("B Course", 1, "01 - X"),
    ]


def test_render_report_marks_cleaned_topic_and_hides_exam_table_in_callout(tmp_path):
    vault_path = tmp_path / "vault"
    semester = "3. Semester"
    _write_topic(vault_path / semester, "Course", "Week 1", "01 - Topic", "note body", transcript=True, exam=True)
    rows = scan_topics(vault_path, semester)

    report = render_report(rows, semester)

    assert "# Progress — 3. Semester" in report
    assert "## Core pipeline" in report
    assert "## Enrichment (reminders)" in report
    assert "> [!NOTE]- Exam prep" in report
    assert "| Course | Week | Topic | Transcribed | Enhanced | Cleaned |" in report
    assert "| Course | 1 | 01 - Topic | ✅ | ✅ | ✅ |" in report
    assert "> | Course | 1 | 01 - Topic | ✅ |" in report


def test_main_writes_progress_file_using_config(monkeypatch, tmp_path, capsys):
    vault_path = tmp_path / "vault"
    config_file = tmp_path / "config.env"
    config_file.write_text(f"VAULT_PATH={vault_path}\n")
    monkeypatch.setenv("CONFIG_PATH", str(config_file))

    semester = "3. Semester"
    _write_topic(vault_path / semester, "Course", "Week 1", "01 - Topic", "note body", transcript=True)

    main([semester])

    output_path = vault_path / semester / "Progress.md"
    assert output_path.exists()
    assert "01 - Topic" in output_path.read_text(encoding="utf-8")
    assert "Wrote" in capsys.readouterr().out


def test_main_no_topics_found_exits_cleanly(monkeypatch, tmp_path, capsys):
    vault_path = tmp_path / "vault"
    config_file = tmp_path / "config.env"
    config_file.write_text(f"VAULT_PATH={vault_path}\n")
    monkeypatch.setenv("CONFIG_PATH", str(config_file))

    (vault_path / "3. Semester").mkdir(parents=True)

    try:
        main(["3. Semester"])
        raised = False
    except SystemExit as e:
        raised = True
        assert e.code == 1

    assert raised
    assert "No topic notes found" in capsys.readouterr().err
