"""Tests for model dataclasses."""

from __future__ import annotations

import time

from tqrex.models import ProgressState, Vector2D


def test_vector2d_add() -> None:
    a = Vector2D(1.0, 2.0)
    b = Vector2D(3.0, 4.0)
    c = a + b
    assert c.x == pytest.approx(4.0)
    assert c.y == pytest.approx(6.0)


def test_vector2d_mul() -> None:
    v = Vector2D(2.0, 3.0)
    r = v * 2.0
    assert r.x == pytest.approx(4.0)
    assert r.y == pytest.approx(6.0)


def test_progress_state_fraction_zero_total() -> None:
    p = ProgressState(total=0)
    assert p.fraction == 1.0


def test_progress_state_fraction_clamps_at_one() -> None:
    p = ProgressState(total=10, completed=15)
    assert p.fraction == 1.0


def test_progress_state_eta_none_when_no_progress() -> None:
    p = ProgressState(total=100, completed=0)
    assert p.eta is None


def test_progress_state_elapsed_increases() -> None:
    p = ProgressState(total=10)
    time.sleep(0.01)
    assert p.elapsed >= 0.01


import pytest  # noqa: E402 — keep at bottom to not confuse the test runner
