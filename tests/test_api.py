"""Tests for the public track() and Progress APIs."""

from __future__ import annotations

import pytest

from playgress import Progress, track
from playgress.config import Theme


def test_track_yields_all_items() -> None:
    items = list(range(10))
    result = list(track(items, disable=True))
    assert result == items


def test_track_empty_iterable() -> None:
    result = list(track([], disable=True))
    assert result == []


def test_track_infers_total_from_len() -> None:
    items = [1, 2, 3]
    collected = []
    for item in track(items, disable=True):
        collected.append(item)
    assert len(collected) == 3


def test_track_accepts_generator() -> None:
    gen = (x * 2 for x in range(5))
    result = list(track(gen, total=5, disable=True))
    assert result == [0, 2, 4, 6, 8]


def test_progress_context_manager() -> None:
    with Progress(total=3, description="test") as p:
        p.update(1)
        p.update(1)
        p.update(1)


def test_progress_clamps_at_total() -> None:
    with Progress(total=2) as p:
        p.update(99)
        assert p._state.completed == 2


@pytest.mark.parametrize("theme", [Theme.ASCII_BLOCK, Theme.EMOJI, Theme.AUTO])
def test_track_accepts_all_themes(theme: Theme) -> None:
    result = list(track([1, 2, 3], theme=theme, disable=True))
    assert len(result) == 3
