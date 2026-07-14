"""Tests for physics helpers and collision detection."""

from __future__ import annotations

import pytest

from tqrex.engine.physics import (
    check_collision,
)
from tqrex.models import AABB, DinoState, Obstacle, ObstacleType, Vector2D

# ── AABB.intersects ────────────────────────────────────────────────────────────


def test_aabb_overlap() -> None:
    a = AABB(0, 0, 4, 4)
    b = AABB(2, 2, 4, 4)
    assert a.intersects(b)
    assert b.intersects(a)


def test_aabb_touching_edge_no_overlap() -> None:
    a = AABB(0, 0, 4, 4)
    b = AABB(4, 0, 4, 4)
    assert not a.intersects(b)


def test_aabb_no_overlap() -> None:
    a = AABB(0, 0, 2, 2)
    b = AABB(10, 10, 2, 2)
    assert not a.intersects(b)


# ── check_collision ────────────────────────────────────────────────────────────


def _make_dino(x: float, y: float) -> DinoState:
    return DinoState(position=Vector2D(x, y))


def _make_cactus(x: float, y: float) -> Obstacle:
    return Obstacle(
        type=ObstacleType.CACTUS_SMALL,
        position=Vector2D(x, y),
        width=3,
        height=4,
    )


def test_no_obstacles_no_collision() -> None:
    dino = _make_dino(10.0, 4.0)
    assert not check_collision(dino, [])


# NOTE: full collision tests are enabled in Phase 3 once physics coordinates
# are finalised. Placeholder below documents the expected contract.


@pytest.mark.skip(reason="physics coordinates finalised in Phase 3")
def test_direct_overlap_is_collision() -> None:
    dino = _make_dino(10.0, 4.0)
    cactus = _make_cactus(10.5, 4.0)
    assert check_collision(dino, [cactus])


@pytest.mark.skip(reason="physics coordinates finalised in Phase 3")
def test_obstacle_far_away_no_collision() -> None:
    dino = _make_dino(10.0, 4.0)
    cactus = _make_cactus(50.0, 4.0)
    assert not check_collision(dino, [cactus])
