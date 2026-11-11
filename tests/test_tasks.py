from datetime import date

import pytest

from logic import tasks
from tests import make_db


def test_tasks_are_sorted_by_due_date():
    db = make_db()
    tasks.add_task(db, "Later", "2026-12-01")
    tasks.add_task(db, "Sooner", "2026-11-20")
    assert [t["title"] for t in tasks.list_tasks(db)] == ["Sooner", "Later"]


def test_invalid_task_is_rejected_and_not_saved():
    db = make_db()
    with pytest.raises(ValueError):
        tasks.add_task(db, "", "2026-11-20")
    with pytest.raises(ValueError):
        tasks.add_task(db, "Study", "not-a-date")
    assert tasks.list_tasks(db) == []


def test_overdue_boundaries():
    today = date(2026, 11, 11)
    assert tasks.is_overdue("2026-11-10", 0, today)
    assert not tasks.is_overdue("2026-11-11", 0, today)  # due today is not overdue
    assert not tasks.is_overdue("2026-11-10", 1, today)  # finished tasks are never overdue


def test_list_marks_overdue():
    db = make_db()
    tasks.add_task(db, "Old", "2026-11-01")
    assert tasks.list_tasks(db, today=date(2026, 11, 11))[0]["overdue"] is True


def test_toggle_changes_pending_count():
    db = make_db()
    tasks.add_task(db, "A", "2026-11-20")
    assert tasks.pending_count(db) == 1
    tasks.toggle_task(db, 1)
    assert tasks.pending_count(db) == 0
    tasks.toggle_task(db, 1)
    assert tasks.pending_count(db) == 1


def test_delete_task():
    db = make_db()
    tasks.add_task(db, "A", "2026-11-20")
    tasks.delete_task(db, 1)
    assert tasks.list_tasks(db) == []
