"""Study plan generator: spreads topics over the days left before an exam."""
from datetime import date, timedelta

from .validators import parse_date


def make_plan(topics, start, exam):
    """Spread topics over the days from `start` up to (not including) `exam`.

    Returns a list of (day, [topics]) for the days that have topics.
    When the topics don't divide evenly, the earlier days get one extra.
    """
    days = (exam - start).days
    if days < 1:
        raise ValueError("The exam date must be after today.")
    per_day, extra = divmod(len(topics), days)  # e.g. 5 topics, 3 days -> 1 each, 2 days get +1
    plan, position = [], 0
    for i in range(days):
        size = per_day + (1 if i < extra else 0)
        if size:
            plan.append((start + timedelta(days=i), topics[position:position + size]))
            position += size
    return plan


def plan_for_subject(subject, exam_text, today=None):
    """Plan the unfinished topics of one subject (a dict from progress.subject_progress)."""
    exam = parse_date(exam_text)
    pending = [t["title"] for t in subject["topics"] if not t["done"]]
    return make_plan(pending, today or date.today(), exam)
