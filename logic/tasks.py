"""To-do and deadline logic. Every function takes an open sqlite3 connection."""
from datetime import date

from .validators import clean_text, parse_date


def add_task(conn, title, due_date):
    """Validate and save a new task."""
    title = clean_text(title, "Title")
    due = parse_date(due_date)
    conn.execute("INSERT INTO tasks (title, due_date) VALUES (?, ?)", (title, due.isoformat()))
    conn.commit()


def is_overdue(due_date, done, today=None):
    """A task is overdue only if it is not done and its due date has passed."""
    today = today or date.today()
    return not done and date.fromisoformat(due_date) < today


def list_tasks(conn, today=None):
    """All tasks, pending first, each sorted by due date, with an 'overdue' flag."""
    rows = conn.execute("SELECT * FROM tasks ORDER BY done, due_date").fetchall()
    return [dict(r, overdue=is_overdue(r["due_date"], r["done"], today)) for r in rows]


def toggle_task(conn, task_id):
    """Flip a task between pending and done."""
    conn.execute("UPDATE tasks SET done = 1 - done WHERE id = ?", (task_id,))
    conn.commit()


def delete_task(conn, task_id):
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()


def pending_count(conn):
    return conn.execute("SELECT COUNT(*) FROM tasks WHERE done = 0").fetchone()[0]
