"""StudySphere - Flask routes only. All real logic lives in the logic/ package."""
import os
import sqlite3
from datetime import date, timedelta

from flask import Flask, flash, g, redirect, render_template, request, url_for

from logic import progress, quiz, tasks

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "studysphere.db")
QUIZ_PATH = os.path.join(BASE, "data", "quiz_data.csv")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-secret")

# Sample data, added once when the database is first created.
SAMPLE_TOPICS = {
    "Mathematics": ["Limits", "Derivatives"],
    "Physics": ["Ohm's law", "Kirchhoff's laws"],
    "Python": ["Functions", "Git basics"],
}
SAMPLE_TASKS = [("Finish maths worksheet", -1), ("Read physics chapter 2", 2),
                ("Submit Python project", 13)]


def init_db():
    """Create tables and sample data, but only if the database file is new."""
    if os.path.exists(DB_PATH):
        return
    db = sqlite3.connect(DB_PATH)
    with open(os.path.join(BASE, "schema.sql"), encoding="utf-8") as f:
        db.executescript(f.read())
    for subject, topics in SAMPLE_TOPICS.items():
        subject_id = progress.add_subject(db, subject)
        for title in topics:
            progress.add_topic(db, subject_id, title)
    progress.toggle_topic(db, 1)  # mark one topic as studied so progress is visible
    for title, days in SAMPLE_TASKS:
        tasks.add_task(db, title, (date.today() + timedelta(days=days)).isoformat())
    db.close()


def get_db():
    """One database connection per request."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def run(action, *args):
    """Call a logic function; show its validation error to the user instead of crashing."""
    try:
        action(*args)
    except ValueError as error:
        flash(str(error), "danger")


init_db()


@app.route("/")
def index():
    db = get_db()
    overdue = sum(t["overdue"] for t in tasks.list_tasks(db))
    return render_template("index.html", pending=tasks.pending_count(db), overdue=overdue,
                           overall=progress.overall_percent(db),
                           subjects=progress.subject_progress(db), last=quiz.last_result(db))


@app.route("/tasks", methods=["GET", "POST"])
def tasks_page():
    db = get_db()
    if request.method == "POST":
        run(tasks.add_task, db, request.form.get("title"), request.form.get("due_date"))
        return redirect(url_for("tasks_page"))
    return render_template("tasks.html", tasks=tasks.list_tasks(db))


@app.post("/tasks/<int:task_id>/toggle")
def task_toggle(task_id):
    tasks.toggle_task(get_db(), task_id)
    return redirect(url_for("tasks_page"))


@app.post("/tasks/<int:task_id>/delete")
def task_delete(task_id):
    tasks.delete_task(get_db(), task_id)
    return redirect(url_for("tasks_page"))


@app.get("/progress")
def progress_page():
    return render_template("progress.html", subjects=progress.subject_progress(get_db()))


@app.post("/progress/subject")
def subject_add():
    run(progress.add_subject, get_db(), request.form.get("name"))
    return redirect(url_for("progress_page"))


@app.post("/progress/topic")
def topic_add():
    run(progress.add_topic, get_db(), request.form.get("subject_id", type=int),
        request.form.get("title"))
    return redirect(url_for("progress_page"))


@app.post("/progress/topic/<int:topic_id>/toggle")
def topic_toggle(topic_id):
    progress.toggle_topic(get_db(), topic_id)
    return redirect(url_for("progress_page"))


@app.route("/quiz", methods=["GET", "POST"])
def quiz_page():
    questions, result = [], None
    try:
        questions = quiz.load_questions(QUIZ_PATH)
    except ValueError as error:
        flash(str(error), "danger")
    if request.method == "POST" and questions:
        result = quiz.score_quiz(questions, request.form)
        quiz.save_result(get_db(), *result)
    return render_template("quiz.html", questions=questions, result=result)


if __name__ == "__main__":
    app.run(debug=True)  # debug mode is for local use only
