from datetime import date
import pytest
from logic.planner import make_plan, plan_for_subject
TOPICS = ["A", "B", "C", "D"]
def test_even_split():
    plan = make_plan(TOPICS, date(2026, 11, 20), date(2026, 11, 22))
    assert plan == [(date(2026, 11, 20), ["A", "B"]), (date(2026, 11, 21), ["C", "D"])]
def test_uneven_split_gives_earlier_days_more():
    plan = make_plan(list("ABCDE"), date(2026, 11, 20), date(2026, 11, 23))
    assert [len(day) for _, day in plan] == [2, 2, 1]
def test_fewer_topics_than_days_skips_empty_days():
    plan = make_plan(["A", "B"], date(2026, 11, 20), date(2026, 11, 25))
    assert plan == [(date(2026, 11, 20), ["A"]), (date(2026, 11, 21), ["B"])]
def test_no_topics_gives_empty_plan():
    assert make_plan([], date(2026, 11, 20), date(2026, 11, 25)) == []
@pytest.mark.parametrize("exam", [date(2026, 11, 20), date(2026, 11, 19)])
def test_exam_must_be_after_start(exam):
    with pytest.raises(ValueError):
        make_plan(TOPICS, date(2026, 11, 20), exam)
def test_every_topic_appears_once_in_order():
    topics = [f"T{i}" for i in range(11)]
    plan = make_plan(topics, date(2026, 11, 1), date(2026, 11, 5))
    assert [t for _, day in plan for t in day] == topics
