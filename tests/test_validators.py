from datetime import date

import pytest

from logic.validators import clean_text, parse_date


def test_clean_text_strips_spaces():
    assert clean_text("  hello  ") == "hello"


@pytest.mark.parametrize("bad", ["", "   ", None])
def test_clean_text_rejects_empty(bad):
    with pytest.raises(ValueError):
        clean_text(bad)


def test_clean_text_length_boundary():
    assert clean_text("x" * 100) == "x" * 100  # exactly the limit is fine
    with pytest.raises(ValueError):
        clean_text("x" * 101)


def test_parse_date_valid():
    assert parse_date("2026-11-24") == date(2026, 11, 24)


@pytest.mark.parametrize("bad", ["", None, "24-11-2026", "2026-02-30", "abc"])
def test_parse_date_rejects_invalid(bad):
    with pytest.raises(ValueError):
        parse_date(bad)
