"""Quiz loading from CSV, random quiz picking, scoring, and saving results."""
import csv
import random
from datetime import date


def load_questions(path):
    """Read questions from a CSV (subject,quiz,question,a,b,c,d,answer). Raise ValueError if bad."""
    try:
        # utf-8-sig also reads files saved by Excel, which add an invisible marker at the start
        with open(path, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
    except FileNotFoundError:
        raise ValueError("Quiz file not found.") from None
    questions = []
    for i, row in enumerate(rows):
        subject = (row.get("subject") or "").strip()
        quiz_name = (row.get("quiz") or "").strip()
        text = (row.get("question") or "").strip()
        options = [(row.get(k) or "").strip() for k in "abcd"]
        answer = (row.get("answer") or "").strip().lower()
        if not (subject and quiz_name and text) or not all(options) or answer not in list("abcd"):
            raise ValueError(f"Quiz file has a bad row at line {i + 2}.")
        questions.append({"id": i, "subject": subject, "quiz": quiz_name, "question": text,
                          "options": options, "answer": "abcd".index(answer)})
    return questions


def list_subjects(questions):
    """Sorted names of all subjects that have questions."""
    return sorted({q["subject"] for q in questions})


def quiz_names(questions, subject):
    """Sorted names of the quizzes that belong to one subject."""
    return sorted({q["quiz"] for q in questions if q["subject"] == subject})


def get_quiz(questions, subject, quiz_name):
    """The questions of one quiz, in file order (empty list if it does not exist)."""
    return [q for q in questions if q["subject"] == subject and q["quiz"] == quiz_name]


def pick_random_quiz(questions, subject, rng=random):
    """Pick one of the subject's quizzes at random and shuffle its questions.

    Returns (quiz_name, shuffled_questions). `rng` can be a seeded random.Random in tests.
    """
    names = quiz_names(questions, subject)
    if not names:
        raise ValueError("No quizzes found for that subject.")
    name = rng.choice(names)
    chosen = get_quiz(questions, subject, name)  # a new list, so the original order is untouched
    rng.shuffle(chosen)
    return name, chosen


def score_quiz(questions, answers):
    """Return (score, total). answers maps question id -> chosen option index.
    Missing or invalid answers simply count as wrong."""
    score = 0
    for q in questions:
        try:
            score += int(answers.get(str(q["id"]))) == q["answer"]
        except (TypeError, ValueError):
            pass
    return score, len(questions)


def save_result(conn, score, total):
    if not 0 <= score <= total:
        raise ValueError("Score must be between 0 and the total.")
    conn.execute("INSERT INTO quiz_results (score, total, taken_at) VALUES (?, ?, ?)",
                 (score, total, date.today().isoformat()))
    conn.commit()


def last_result(conn):
    """Most recent quiz result, or None if no quiz was taken yet."""
    return conn.execute("SELECT * FROM quiz_results ORDER BY id DESC LIMIT 1").fetchone()