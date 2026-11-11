"""Subjects, topics and completion percentages."""
import sqlite3

from .validators import clean_text


def percent(done, total):
    """Whole-number completion percentage. No topics at all counts as 0%."""
    if total < 0 or done < 0 or done > total:
        raise ValueError("Invalid topic counts.")
    return round(100 * done / total) if total else 0


def add_subject(conn, name):
    """Save a subject and return its id."""
    name = clean_text(name, "Subject name", 50)
    try:
        cur = conn.execute("INSERT INTO subjects (name) VALUES (?)", (name,))
    except sqlite3.IntegrityError:
        raise ValueError("That subject already exists.") from None
    conn.commit()
    return cur.lastrowid


def add_topic(conn, subject_id, title):
    """Save a topic under an existing subject and return its id."""
    title = clean_text(title, "Topic title")
    if not conn.execute("SELECT 1 FROM subjects WHERE id = ?", (subject_id,)).fetchone():
        raise ValueError("Subject not found.")
    cur = conn.execute("INSERT INTO topics (subject_id, title) VALUES (?, ?)", (subject_id, title))
    conn.commit()
    return cur.lastrowid


def toggle_topic(conn, topic_id):
    """Flip a topic between not studied and studied."""
    conn.execute("UPDATE topics SET done = 1 - done WHERE id = ?", (topic_id,))
    conn.commit()


def subject_progress(conn):
    """Every subject with its topics and completion percentage."""
    result = []
    for s in conn.execute("SELECT * FROM subjects ORDER BY name").fetchall():
        topics = [dict(t) for t in conn.execute(
            "SELECT * FROM topics WHERE subject_id = ? ORDER BY id", (s["id"],))]
        done = sum(t["done"] for t in topics)
        result.append({"id": s["id"], "name": s["name"], "topics": topics,
                       "percent": percent(done, len(topics))})
    return result


def overall_percent(conn):
    """Completion percentage across all topics of all subjects."""
    done, total = conn.execute("SELECT COALESCE(SUM(done), 0), COUNT(*) FROM topics").fetchone()
    return percent(done, total)
