from ai_mem.domain.memory import title_of


def test_title_is_first_non_empty_line():
    assert title_of("\n  Decision: use Postgres.\nWhy: known.") == "Decision: use Postgres."


def test_heading_marker_is_dropped():
    assert title_of("# ai-mem architecture redesign\nbody") == "ai-mem architecture redesign"
    assert title_of("### Deep heading") == "Deep heading"


def test_heading_only_line_is_skipped():
    assert title_of("#\nReal title") == "Real title"


def test_title_is_truncated():
    assert title_of("x" * 100, max_len=10) == "x" * 10
