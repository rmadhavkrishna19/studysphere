import sqlite3
from pathlib import Path


def make_db():
    """A fresh in-memory database that uses the project's real schema."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript((Path(__file__).parent.parent / "schema.sql").read_text())
    return conn
