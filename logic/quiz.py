"""Quiz loading from CSV, scoring, and saving results."""
import csv
from datetime import date


def load_questions(path):
    """Read questions from a CSV (question,a,b,c,d,answer). Raise ValueError if bad."""
    try:
        with open(path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    except FileNotFoundError:
        raise ValueError("Quiz file not found.") from None
    questions = []
    for i, row in enumerate(rows):
        text = (row.get("question") or "").strip()
        options = [(row.get(k) or "").strip() for k in "abcd"]
        answer = (row.get("answer") or "").strip().lower()
        if not text or not all(options) or answer not in list("abcd"):
            raise ValueError(f"Quiz file has a bad row at line {i + 2}.")
        questions.append({"id": i, "question": text, "options": options,
                          "answer": "abcd".index(answer)})
    return questions


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
