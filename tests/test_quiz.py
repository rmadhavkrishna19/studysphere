import random

import pytest

from logic import quiz
from tests import make_db

HEADER = "subject,quiz,question,a,b,c,d,answer\n"


def make_q(i, subject, name, answer=1):
    """Build a question dict like load_questions does."""
    return {"id": i, "subject": subject, "quiz": name, "question": f"q{i}",
            "options": list("wxyz"), "answer": answer}


QUESTIONS = [make_q(0, "Py", "Set 1"), make_q(1, "Py", "Set 1", 2),
             make_q(2, "Py", "Set 2"), make_q(3, "Git", "Set 1")]


def write_csv(tmp_path, body):
    path = tmp_path / "quiz.csv"
    path.write_text(HEADER + body)
    return path


def test_load_questions(tmp_path):
    loaded = quiz.load_questions(write_csv(tmp_path, "Py,Set 1,2+2?,3,4,5,6,B\n"))
    assert loaded == [{"id": 0, "subject": "Py", "quiz": "Set 1", "question": "2+2?",
                       "options": ["3", "4", "5", "6"], "answer": 1}]


@pytest.mark.parametrize("row", ["Py,Set 1,2+2?,3,4,5,6,E\n",   # answer not a-d
                                 ",Set 1,2+2?,3,4,5,6,A\n",     # empty subject
                                 "Py,,2+2?,3,4,5,6,A\n",        # empty quiz name
                                 "Py,Set 1,,3,4,5,6,A\n",       # empty question
                                 "Py,Set 1,2+2?,3,,5,6,A\n",    # empty option
                                 "Py,Set 1,2+2?,3,4\n"])        # row too short
def test_load_rejects_bad_rows(tmp_path, row):
    with pytest.raises(ValueError):
        quiz.load_questions(write_csv(tmp_path, row))


def test_load_missing_file(tmp_path):
    with pytest.raises(ValueError):
        quiz.load_questions(tmp_path / "missing.csv")


def test_list_subjects_and_quiz_names():
    assert quiz.list_subjects(QUESTIONS) == ["Git", "Py"]
    assert quiz.quiz_names(QUESTIONS, "Py") == ["Set 1", "Set 2"]
    assert quiz.quiz_names(QUESTIONS, "Nope") == []


def test_get_quiz():
    assert [q["id"] for q in quiz.get_quiz(QUESTIONS, "Py", "Set 1")] == [0, 1]
    assert quiz.get_quiz(QUESTIONS, "Py", "Nope") == []


def test_pick_random_quiz_returns_questions_of_that_quiz():
    name, chosen = quiz.pick_random_quiz(QUESTIONS, "Py", random.Random(0))
    assert name in ("Set 1", "Set 2")
    assert all(q["subject"] == "Py" and q["quiz"] == name for q in chosen)


def test_pick_random_quiz_uses_every_quiz_eventually():
    rng = random.Random(1)
    names = {quiz.pick_random_quiz(QUESTIONS, "Py", rng)[0] for _ in range(50)}
    assert names == {"Set 1", "Set 2"}


def test_pick_random_quiz_shuffles_without_changing_the_original():
    many = [make_q(i, "Py", "Set 1") for i in range(10)]
    _, chosen = quiz.pick_random_quiz(many, "Py", random.Random(0))
    assert sorted(q["id"] for q in chosen) == list(range(10))   # same questions
    assert [q["id"] for q in chosen] != list(range(10))         # different order
    assert [q["id"] for q in many] == list(range(10))           # original untouched


def test_pick_random_quiz_unknown_subject():
    with pytest.raises(ValueError):
        quiz.pick_random_quiz(QUESTIONS, "Nope")


def test_score_all_correct():
    assert quiz.score_quiz(QUESTIONS[:2], {"0": "1", "1": "2"}) == (2, 2)


def test_score_wrong_missing_and_invalid_answers():
    assert quiz.score_quiz(QUESTIONS[:2], {"0": "3", "1": "abc"}) == (0, 2)
    assert quiz.score_quiz(QUESTIONS[:2], {"0": None}) == (0, 2)
    assert quiz.score_quiz(QUESTIONS[:2], {}) == (0, 2)


def test_score_empty_quiz():
    assert quiz.score_quiz([], {}) == (0, 0)


def test_save_and_read_last_result():
    db = make_db()
    assert quiz.last_result(db) is None
    quiz.save_result(db, 2, 3)
    last = quiz.last_result(db)
    assert (last["score"], last["total"]) == (2, 3)


def test_save_result_rejects_impossible_score():
    with pytest.raises(ValueError):
        quiz.save_result(make_db(), 4, 3)
