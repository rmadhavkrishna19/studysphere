"""Study garden: finished study sessions make the plant grow."""
from datetime import date, timedelta

# (minutes of study needed, stage name). The plant has 6 stages, 0 to 5.
STAGES = [(0, "Seed"), (25, "Sprout"), (75, "Seedling"),
          (150, "Young plant"), (300, "Little tree"), (500, "Blooming tree")]
MAX_SESSION = 180  # longest single session accepted, in minutes


def stage_for(total_minutes):
    """Index (0 to 5) of the growth stage reached after this many minutes of study."""
    if total_minutes < 0:
        raise ValueError("Minutes cannot be negative.")
    # Count how many thresholds were reached; the first one (0) is always reached.
    return sum(total_minutes >= needed for needed, _ in STAGES) - 1


def progress_to_next(total_minutes):
    """(percent, minutes_left) towards the next stage. A fully grown tree gives (100, 0)."""
    stage = stage_for(total_minutes)
    if stage == len(STAGES) - 1:
        return 100, 0
    start, end = STAGES[stage][0], STAGES[stage + 1][0]
    return round(100 * (total_minutes - start) / (end - start)), end - total_minutes


def add_session(conn, minutes, today=None):
    """Save a finished study session (1 to 180 whole minutes) and return its id."""
    try:
        minutes = int(minutes)
    except (TypeError, ValueError):
        raise ValueError("Minutes must be a whole number.") from None
    if not 1 <= minutes <= MAX_SESSION:
        raise ValueError(f"A session must be between 1 and {MAX_SESSION} minutes.")
    cur = conn.execute("INSERT INTO study_sessions (minutes, studied_on) VALUES (?, ?)",
                       (minutes, (today or date.today()).isoformat()))
    conn.commit()
    return cur.lastrowid


def total_minutes(conn):
    return conn.execute("SELECT COALESCE(SUM(minutes), 0) FROM study_sessions").fetchone()[0]


def minutes_today(conn, today=None):
    row = conn.execute("SELECT COALESCE(SUM(minutes), 0) FROM study_sessions WHERE studied_on = ?",
                       ((today or date.today()).isoformat(),)).fetchone()
    return row[0]


def streak_days(conn, today=None):
    """How many days in a row have a session. The streak stays alive until a day is missed,
    so if you have not studied yet today, yesterday still counts."""
    today = today or date.today()
    days = {date.fromisoformat(r[0]) for r in
            conn.execute("SELECT DISTINCT studied_on FROM study_sessions")}
    day = today if today in days else today - timedelta(days=1)
    count = 0
    while day in days:
        count += 1
        day -= timedelta(days=1)
    return count


def summary(conn, today=None):
    """Everything the garden page needs, as plain numbers and text."""
    total = total_minutes(conn)
    stage = stage_for(total)
    percent, left = progress_to_next(total)
    last = stage == len(STAGES) - 1
    return {"total": total, "stage": stage, "stage_name": STAGES[stage][1],
            "stage_start": STAGES[stage][0],
            "stage_end": None if last else STAGES[stage + 1][0],
            "next_name": None if last else STAGES[stage + 1][1],
            "percent": percent, "minutes_left": left,
            "today": minutes_today(conn, today), "streak": streak_days(conn, today)}
