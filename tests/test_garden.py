from datetime import date

import pytest

from logic import garden
from tests import make_db

TODAY = date(2026, 11, 20)


@pytest.mark.parametrize("minutes,stage", [(0, 0), (24, 0), (25, 1), (74, 1), (75, 2), (149, 2),
                                           (150, 3), (299, 3), (300, 4), (499, 4), (500, 5), (9999, 5)])
def test_stage_boundaries(minutes, stage):
    assert garden.stage_for(minutes) == stage


def test_negative_minutes_rejected():
    with pytest.raises(ValueError):
        garden.stage_for(-1)


def test_progress_to_next():
    assert garden.progress_to_next(0) == (0, 25)
    assert garden.progress_to_next(30) == (10, 45)
    assert garden.progress_to_next(500) == (100, 0)   # fully grown
    assert garden.progress_to_next(10000) == (100, 0)


def test_add_session_and_totals():
    db = make_db()
    garden.add_session(db, 25, TODAY)
    garden.add_session(db, "15", TODAY)               # text from a web form is accepted
    garden.add_session(db, 30, date(2026, 11, 19))
    assert garden.total_minutes(db) == 70
    assert garden.minutes_today(db, TODAY) == 40


@pytest.mark.parametrize("bad", [0, -5, 181, "abc", "2.5", None, ""])
def test_add_session_rejects_invalid_minutes(bad):
    db = make_db()
    with pytest.raises(ValueError):
        garden.add_session(db, bad)
    assert garden.total_minutes(db) == 0


def test_session_length_boundaries():
    db = make_db()
    garden.add_session(db, 1)
    garden.add_session(db, 180)
    assert garden.total_minutes(db) == 181


def streak_with(days):
    """Make a database with one session on each given day of November 2026."""
    db = make_db()
    for d in days:
        garden.add_session(db, 25, date(2026, 11, d))
    return garden.streak_days(db, TODAY)


def test_streak_cases():
    assert streak_with([]) == 0
    assert streak_with([18, 19, 20]) == 3
    assert streak_with([18, 19]) == 2        # nothing yet today, streak still alive
    assert streak_with([18, 20]) == 1        # a gap breaks the streak
    assert streak_with([17]) == 0            # last study day was two days ago


def test_summary():
    db = make_db()
    garden.add_session(db, 30, TODAY)
    info = garden.summary(db, TODAY)
    assert info["stage"] == 1 and info["stage_name"] == "Sprout"
    assert (info["stage_start"], info["stage_end"], info["next_name"]) == (25, 75, "Seedling")
    assert (info["minutes_left"], info["today"], info["streak"]) == (45, 30, 1)


def test_summary_of_fully_grown_plant():
    db = make_db()
    for _ in range(3):
        garden.add_session(db, 180)
    info = garden.summary(db, TODAY)
    assert info["stage"] == 5 and info["stage_end"] is None and info["next_name"] is None
