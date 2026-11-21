import pytest

from logic import progress
from tests import make_db


@pytest.mark.parametrize("done,total,expected",
                         [(0, 0, 0), (0, 4, 0), (1, 3, 33), (2, 3, 67), (4, 4, 100)])
def test_percent(done, total, expected):
    assert progress.percent(done, total) == expected


@pytest.mark.parametrize("done,total", [(5, 4), (-1, 4), (1, -1)])
def test_percent_rejects_impossible_counts(done, total):
    with pytest.raises(ValueError):
        progress.percent(done, total)


def test_subject_without_topics_is_zero_percent():
    db = make_db()
    progress.add_subject(db, "Maths")
    assert progress.subject_progress(db)[0]["percent"] == 0


def test_subject_and_overall_progress():
    db = make_db()
    sid = progress.add_subject(db, "Maths")
    first = progress.add_topic(db, sid, "Limits")
    progress.add_topic(db, sid, "Derivatives")
    progress.toggle_topic(db, first)
    assert progress.subject_progress(db)[0]["percent"] == 50
    assert progress.overall_percent(db) == 50


def test_overall_percent_with_no_topics():
    assert progress.overall_percent(make_db()) == 0


def test_all_topics_done_is_100_percent():
    db = make_db()
    sid = progress.add_subject(db, "Maths")
    progress.toggle_topic(db, progress.add_topic(db, sid, "Limits"))
    assert progress.overall_percent(db) == 100


def test_invalid_subjects_and_topics():
    db = make_db()
    progress.add_subject(db, "Maths")
    with pytest.raises(ValueError):
        progress.add_subject(db, "Maths")  # duplicate
    with pytest.raises(ValueError):
        progress.add_subject(db, "   ")  # empty
    with pytest.raises(ValueError):
        progress.add_topic(db, 99, "Orphan")  # subject does not exist
    with pytest.raises(ValueError):
        progress.add_topic(db, 1, "")  # empty title
        
def test_delete_topic_changes_percent():
    db = make_db()
    sid = progress.add_subject(db, "Maths")
    done = progress.add_topic(db, sid, "Limits")
    other = progress.add_topic(db, sid, "Derivatives")
    progress.toggle_topic(db, done)
    progress.delete_topic(db, other)
    assert progress.subject_progress(db)[0]["percent"] == 100


def test_delete_subject_removes_its_topics_only():
    db = make_db()
    maths = progress.add_subject(db, "Maths")
    progress.add_topic(db, maths, "Limits")
    physics = progress.add_subject(db, "Physics")
    progress.add_topic(db, physics, "Ohm's law")
    progress.delete_subject(db, maths)
    assert [s["name"] for s in progress.subject_progress(db)] == ["Physics"]
    assert db.execute("SELECT COUNT(*) FROM topics").fetchone()[0] == 1


def test_deleting_unknown_ids_does_nothing():
    db = make_db()
    progress.delete_subject(db, 99)
    progress.delete_topic(db, 99)
    assert progress.overall_percent(db) == 0
