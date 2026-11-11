import pytest

from logic import quiz
from tests import make_db

HEADER = "question,a,b,c,d,answer\n"
QUESTIONS = [
    {"id": 0, "question": "q1", "options": list("wxyz"), "answer": 1},
    {"id": 1, "question": "q2", "options": list("wxyz"), "answer": 2},
]


def write_csv(tmp_path, body):
    path = tmp_path / "quiz.csv"
    path.write_text(HEADER + body)
    return path


def test_load_questions(tmp_path):
    loaded = quiz.load_questions(write_csv(tmp_path, "2+2?,3,4,5,6,B\n"))
    assert loaded == [{"id": 0, "question": "2+2?", "options": ["3", "4", "5", "6"], "answer": 1}]


@pytest.mark.parametrize("row", ["2+2?,3,4,5,6,E\n",  # answer not a-d
                                 ",3,4,5,6,A\n",       # empty question
                                 "2+2?,3,,5,6,A\n",    # empty option
                                 "2+2?,3,4\n"])        # row too short
def test_load_rejects_bad_rows(tmp_path, row):
    with pytest.raises(ValueError):
        quiz.load_questions(write_csv(tmp_path, row))


def test_load_missing_file(tmp_path):
    with pytest.raises(ValueError):
        quiz.load_questions(tmp_path / "missing.csv")


def test_score_all_correct():
    assert quiz.score_quiz(QUESTIONS, {"0": "1", "1": "2"}) == (2, 2)


def test_score_wrong_missing_and_invalid_answers():
    assert quiz.score_quiz(QUESTIONS, {"0": "3", "1": "abc"}) == (0, 2)
    assert quiz.score_quiz(QUESTIONS, {"0": None}) == (0, 2)
    assert quiz.score_quiz(QUESTIONS, {}) == (0, 2)


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
