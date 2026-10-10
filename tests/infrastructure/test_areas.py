"""Tests for area addressing: nearest ancestor with docs/records/, qualified refs `<rel>:<id>`."""
from __future__ import annotations

import pytest

from ai_mem.infrastructure.areas import (
    Area,
    AreaRefResolver,
    area_for_key,
    area_records_dir,
    discover_areas,
    find_area,
    parse_ref,
    qualify,
    resolve_ref,
)


def _make_area(path):
    (path / "docs" / "records").mkdir(parents=True)
    return Area(path.resolve(), (path / "docs" / "records").resolve())


@pytest.fixture
def workspace(tmp_path):
    """ws/ (no area), ws/proj (area) with nested ws/proj/sub (area), ws/other (area), ws/home/coll (area)."""
    ws = tmp_path / "ws"
    areas = {name: _make_area(ws / rel) for name, rel in
             {"proj": "proj", "sub": "proj/sub", "other": "other", "coll": "home/coll"}.items()}
    return ws, areas


def test_find_area_is_the_nearest_ancestor_with_records(workspace):
    ws, areas = workspace
    (ws / "proj" / "src" / "deep").mkdir(parents=True)

    assert find_area(ws / "proj" / "src" / "deep") == areas["proj"]
    assert find_area(ws / "proj") == areas["proj"]
    assert find_area(ws / "proj" / "sub") == areas["sub"]
    assert find_area(ws) is None


def test_find_area_inside_the_records_dir_is_its_owner(workspace):
    ws, areas = workspace
    topic = ws / "proj" / "docs" / "records" / "arch" / "decisions"
    topic.mkdir(parents=True)
    (topic / "domain_x.md").write_text("id: domain_x\n")

    assert find_area(topic) == areas["proj"]
    assert find_area(topic / "domain_x.md") == areas["proj"]
    assert find_area(ws / "proj" / "docs" / "records") == areas["proj"]


def test_find_area_maps_a_worktree_copy_to_the_main_checkout(workspace):
    ws, areas = workspace
    worktree = ws / "proj" / ".claude" / "worktrees" / "agent-abc"
    _make_area(worktree)
    (worktree / "src").mkdir()

    assert find_area(worktree / "src") == areas["proj"]


def test_discover_areas_finds_nested_and_skips_hidden_dirs(workspace):
    ws, areas = workspace
    _make_area(ws / "proj" / ".claude" / "worktrees" / "agent-abc")
    _make_area(ws / "proj" / "node_modules" / "pkg")
    _make_area(ws / ".hidden")

    assert discover_areas(ws) == sorted(areas.values(), key=lambda area: str(area.root))
    assert discover_areas(ws, max_depth=1) == [areas["other"], areas["proj"]]


def test_qualify_and_resolve_round_trip(workspace):
    _, areas = workspace
    cases = {
        ("proj", "other"): "../other:learning_x",
        ("proj", "sub"): "./sub:learning_x",
        ("sub", "proj"): "..:learning_x",
        ("sub", "coll"): "../../home/coll:learning_x",
        ("proj", "proj"): "learning_x",
    }
    for (source, target), ref in cases.items():
        assert qualify(areas[source], areas[target], "learning_x") == ref
        assert resolve_ref(areas[source], ref) == (areas[target], "learning_x")


def test_parse_ref_splits_at_the_last_colon():
    assert parse_ref("learning_x") == (None, "learning_x")
    assert parse_ref("../a/b:learning_x") == ("../a/b", "learning_x")
    assert parse_ref("./a:learning_x") == ("./a", "learning_x")


@pytest.mark.parametrize("ref", [
    "/etc:x", "~/x:y", "~:y", "a/b:x", "other:x", ":x", "../a//b:x", "../a/:x", "./../a:x",
    "../a/../b:x", "../a/./b:x", "../a\\b:x", "../a\0:x", "../a/~b:x", "../a/*:x",
    "..:*", "..:../x", "..:a/b", "..:", "..:INDEX", "x/y", "*", "",
])
def test_hostile_refs_are_rejected(workspace, ref):
    _, areas = workspace

    with pytest.raises(ValueError):
        parse_ref(ref)
    assert resolve_ref(areas["proj"], ref) is None


def test_resolve_ref_needs_an_area_at_the_target(workspace):
    _, areas = workspace

    assert resolve_ref(areas["sub"], "../../..:x") is None  # ws/ has no docs/records
    assert resolve_ref(areas["proj"], "../missing:x") is None
    assert resolve_ref(areas["proj"], "./docs:x") is None  # proj/docs is not an area root


def test_area_keys_are_absolute_normalised_area_roots(workspace):
    ws, areas = workspace

    assert area_for_key(str(areas["proj"].root)) == areas["proj"]
    assert area_records_dir(str(areas["proj"].root)) == areas["proj"].records_dir
    for key in ("", "proj", "repo.example", f"{areas['sub'].root}/..", f"{areas['proj'].root}\0",
                str(ws.resolve())):
        assert area_for_key(key) is None
        assert area_records_dir(key) is None


def test_area_ref_resolver_works_on_area_keys(workspace):
    _, areas = workspace
    resolver = AreaRefResolver()

    assert resolver.resolve(str(areas["proj"].root), "../other:x") == (str(areas["other"].root), "x")
    assert resolver.resolve(str(areas["proj"].root), "/etc:x") is None
    assert resolver.resolve("repo.example", "../other:x") is None
