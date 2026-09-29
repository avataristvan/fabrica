"""Tests for ai_mem.infrastructure.adr_markdown: pure serialize()/parse() text transform."""
from __future__ import annotations

import pytest

from ai_mem.infrastructure.adr_markdown import ParsedAdr, parse, serialize


def test_roundtrip_id_type_text():
    text = "Decision: use X.\nWhy: Y.\nScope: Z."
    md = serialize("domain_foo", "domain", text, metadata={})
    parsed = parse(md)

    assert parsed.id == "domain_foo"
    assert parsed.type == "domain"
    assert parsed.text == text


def test_roundtrip_superseded_by_and_edges():
    metadata = {
        "superseded_by": "domain_newer",
        "edges": [{"target_id": "domain_other", "edge_type": "related"}],
    }
    md = serialize("domain_foo", "domain", "some text", metadata)
    parsed = parse(md)

    assert parsed.superseded_by == "domain_newer"
    assert parsed.edges == [{"target_id": "domain_other", "edge_type": "related"}]


def test_roundtrip_created_at_and_valid_until():
    metadata = {"created_at": 1700000000.0, "valid_until": 1800000000.0}
    md = serialize("pattern_foo", "pattern", "body", metadata)
    parsed = parse(md)

    assert parsed.created_at == 1700000000.0
    assert parsed.valid_until == 1800000000.0


def test_volatile_fields_excluded_from_output():
    metadata = {
        "confidence": 0.9,
        "access_count": 42,
        "boost_count": 3,
        "last_accessed_at": 1700000000.0,
        "cue": "some cue text",
    }
    md = serialize("domain_foo", "domain", "body text", metadata)

    frontmatter = md.split("\n---\n\n", 1)[0]
    for volatile_key in ("confidence", "access_count", "boost_count", "last_accessed_at", "cue"):
        assert volatile_key not in frontmatter


def test_deterministic_field_order_ignores_dict_insertion_order():
    metadata_a = {
        "created_at": 1700000000.0,
        "superseded_by": "domain_newer",
        "valid_until": 1800000000.0,
        "edges": [{"target_id": "t1", "edge_type": "related"}],
    }
    # Same content, different insertion order.
    metadata_b = {
        "edges": [{"target_id": "t1", "edge_type": "related"}],
        "valid_until": 1800000000.0,
        "superseded_by": "domain_newer",
        "created_at": 1700000000.0,
    }

    md_a = serialize("domain_foo", "domain", "body", metadata_a)
    md_b = serialize("domain_foo", "domain", "body", metadata_b)

    assert md_a == md_b


def test_edges_serialized_as_single_line_json():
    metadata = {"edges": [{"target_id": "t1", "edge_type": "related"}, {"target_id": "t2", "edge_type": "fixes"}]}
    md = serialize("domain_foo", "domain", "body", metadata)

    frontmatter = md.split("\n---\n\n", 1)[0]
    edges_lines = [line for line in frontmatter.splitlines() if line.startswith("edges:")]
    assert len(edges_lines) == 1

    parsed = parse(md)
    assert parsed.edges == [
        {"target_id": "t1", "edge_type": "related"},
        {"target_id": "t2", "edge_type": "fixes"},
    ]


def test_edges_accepts_chroma_style_json_string_metadata():
    """metadata['edges'] as it actually lives in Chroma today: a JSON-encoded string, not a list."""
    metadata = {"edges": '[{"target_id": "t1", "edge_type": "causes"}]'}
    md = serialize("domain_foo", "domain", "body", metadata)
    parsed = parse(md)

    assert parsed.edges == [{"target_id": "t1", "edge_type": "causes"}]


def test_serialize_omits_absent_optional_fields():
    md = serialize("domain_foo", "domain", "body", metadata={})

    frontmatter = md.split("\n---\n\n", 1)[0]
    assert frontmatter == "id: domain_foo\ntype: domain\narea: general"


def test_parse_missing_separator_raises():
    with pytest.raises(ValueError):
        parse("id: domain_foo\ntype: domain\n\nno separator here")


def test_parse_missing_required_fields_raises():
    with pytest.raises(ValueError):
        parse("type: domain\n---\n\nbody text")


def test_parse_malformed_frontmatter_line_raises():
    with pytest.raises(ValueError):
        parse("id: domain_foo\nnot a key value line\n---\n\nbody")


def test_parse_invalid_edges_json_raises():
    with pytest.raises(ValueError):
        parse("id: domain_foo\ntype: domain\nedges: not json\n---\n\nbody")


def test_parse_invalid_created_value_raises():
    with pytest.raises(ValueError):
        parse("id: domain_foo\ntype: domain\ncreated: not-a-float\n---\n\nbody")


def test_parsed_adr_is_dataclass_with_expected_fields():
    parsed = ParsedAdr(
        id="x", type="domain", text="t", created_at=None, superseded_by=None, valid_until=None, edges=[]
    )
    assert parsed.id == "x"
    assert parsed.edges == []


def test_cleared_valid_until_is_omitted_and_roundtrips():
    # "" is the documented un-supersede value; it must not produce an unparseable file.
    md = serialize("domain_x", "domain", "body", {"superseded_by": "", "valid_until": ""})
    assert "valid_until" not in md
    assert "superseded_by" not in md
    parsed = parse(md)
    assert parsed.valid_until is None
    assert parsed.superseded_by is None


def test_frontmatter_order_puts_area_after_type():
    md = serialize(
        "domain_x",
        "domain",
        "body",
        {"area": "hooks", "created_at": 1.0, "superseded_by": "domain_y", "valid_until": 2.0, "edges": [{"target_id": "t", "edge_type": "confirms"}]},
    )
    keys = [line.split(":")[0] for line in md.split("\n---\n")[0].splitlines()]
    assert keys == ["id", "type", "area", "created", "superseded_by", "valid_until", "edges"]
    assert parse(md).area == "hooks"


def test_legacy_file_without_area_parses_as_general():
    parsed = parse("id: domain_old\ntype: domain\ncreated: 1.0\n\n---\n\nbody")
    assert parsed.area == "general"


def test_roundtrip_default_area_is_byte_identical():
    md = serialize("domain_x", "domain", "body", {"created_at": 1.0})
    assert "area: general\n" in md
    parsed = parse(md)
    again = serialize(
        parsed.id, parsed.type, parsed.text,
        {"area": parsed.area, "created_at": parsed.created_at, "superseded_by": parsed.superseded_by,
         "valid_until": parsed.valid_until, "edges": parsed.edges},
    )
    assert again == md


def test_learning_type_roundtrips_with_area():
    md = serialize("learning_x", "learning", "Observed: a\nCause: unknown\nEvidence: b", {"area": "search"})
    parsed = parse(md)
    assert (parsed.type, parsed.area) == ("learning", "search")
