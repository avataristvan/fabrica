"""DetectSplitHintsUseCase: split hint detection by text length or structure alone."""
from __future__ import annotations

from ai_mem.application.detect_split_hints import (
    DetectSplitHintsUseCase,
    SPLIT_MIN_TEXT_CHARS,
)
from ai_mem.domain.memory import QueryResult


def _result(id_: str = "x", text: str = "x") -> QueryResult:
    return QueryResult(
        rank=1,
        id=id_,
        score=0.9,
        text=text,
        metadata={},
    )


_LONG_TEXT = "a" * SPLIT_MIN_TEXT_CHARS
_SHORT_TEXT = "a" * (SPLIT_MIN_TEXT_CHARS - 1)

_MULTI_HEADER_TEXT = "## Section One\nsome content\n## Section Two\nmore content"
_MULTI_TRIED_TEXT = "Tried: approach A\nFailed because: X\nTried: approach B\nFailed because: Y"
_NUMBERED_4_TEXT = "1. Item one\n2. Item two\n3. Item three\n4. Item four"
_NUMBERED_3_TEXT = "1. Item one\n2. Item two\n3. Item three"


def test_no_hint_when_text_below_min_length_and_no_structure():
    uc = DetectSplitHintsUseCase()
    assert uc.execute([_result(text=_SHORT_TEXT)]) == []


def test_hint_generated_by_length():
    uc = DetectSplitHintsUseCase()
    hints = uc.execute([_result(id_="entry-1", text=_LONG_TEXT)])
    assert len(hints) == 1
    assert hints[0].id == "entry-1"


def test_hint_generated_by_multiple_headers():
    uc = DetectSplitHintsUseCase()
    hints = uc.execute([_result(id_="e", text=_MULTI_HEADER_TEXT)])
    assert len(hints) == 1
    assert hints[0].id == "e"


def test_hint_generated_by_multiple_tried_blocks():
    uc = DetectSplitHintsUseCase()
    hints = uc.execute([_result(id_="e", text=_MULTI_TRIED_TEXT)])
    assert len(hints) == 1


def test_hint_generated_by_four_numbered_items():
    uc = DetectSplitHintsUseCase()
    hints = uc.execute([_result(id_="e", text=_NUMBERED_4_TEXT)])
    assert len(hints) == 1


def test_no_hint_for_three_numbered_items():
    uc = DetectSplitHintsUseCase()
    hints = uc.execute([_result(text=_NUMBERED_3_TEXT)])
    assert hints == []


def test_multiple_candidates_produce_multiple_hints():
    uc = DetectSplitHintsUseCase()
    results = [
        _result(id_="a", text=_LONG_TEXT),
        _result(id_="b", text=_SHORT_TEXT),
        _result(id_="c", text=_MULTI_HEADER_TEXT),
    ]
    hints = uc.execute(results)
    assert len(hints) == 2
    assert {h.id for h in hints} == {"a", "c"}


def test_text_preview_truncated_at_80_chars():
    uc = DetectSplitHintsUseCase()
    hints = uc.execute([_result(text="b" * SPLIT_MIN_TEXT_CHARS)])
    assert hints[0].text_preview == "b" * 80


def test_empty_results_returns_empty_hints():
    assert DetectSplitHintsUseCase().execute([]) == []
