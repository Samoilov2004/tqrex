"""Procedural obstacle generation: cacti variants and pterodactyls."""

from __future__ import annotations

import random

from playgress.config import (
    GAME_COLS,
    GROUND_ROW,
    MAX_OBSTACLE_GAP,
    MIN_OBSTACLE_GAP,
    PTERODACTYL_UNLOCK_SCORE,
)
from playgress.models import Obstacle, ObstacleType, Vector2D

# Pterodactyl can fly at three heights relative to the ground row.
_PTERO_ROW_OFFSETS: tuple[int, ...] = (-1, -2, -3)

# Pixel dimensions per obstacle type (width, height) in character cells.
_OBSTACLE_DIMS: dict[ObstacleType, tuple[int, int]] = {
    ObstacleType.CACTUS_SMALL: (3, 4),
    ObstacleType.CACTUS_LARGE: (5, 5),
    ObstacleType.CACTUS_GROUP: (6, 4),
    ObstacleType.PTERODACTYL: (3, 3),
}


def next_obstacle(score: float, rng: random.Random | None = None) -> Obstacle:
    """Generate the next obstacle, placed just off the right edge of the screen.

    Pterodactyls are only included once *score* passes the unlock threshold.
    """
    # TODO(Phase 3): implement weighted random selection and gap logic
    r = rng or random
    pool = [ObstacleType.CACTUS_SMALL, ObstacleType.CACTUS_LARGE, ObstacleType.CACTUS_GROUP]
    if score >= PTERODACTYL_UNLOCK_SCORE:
        pool.append(ObstacleType.PTERODACTYL)

    otype = r.choice(pool)
    w, h = _OBSTACLE_DIMS[otype]
    x = float(GAME_COLS)
    y = float(GROUND_ROW - h + 1)
    if otype is ObstacleType.PTERODACTYL:
        y += r.choice(_PTERO_ROW_OFFSETS)

    return Obstacle(type=otype, position=Vector2D(x, y), width=w, height=h)


def advance(obstacles: list[Obstacle], speed: float, dt: float) -> list[Obstacle]:
    """Scroll obstacles left by *speed* × *dt* columns; prune off-screen ones."""
    # TODO(Phase 3): implement
    dx = speed * dt
    result: list[Obstacle] = []
    for obs in obstacles:
        obs.position.x -= dx
        if obs.position.x + obs.width > 0:
            result.append(obs)
    return result


def should_spawn(obstacles: list[Obstacle], rng: random.Random | None = None) -> bool:
    """Return True when it is time to spawn the next obstacle."""
    # TODO(Phase 3): implement with gap randomisation
    r = rng or random
    if not obstacles:
        return True
    rightmost_x = max(obs.position.x for obs in obstacles)
    gap = r.randint(MIN_OBSTACLE_GAP, MAX_OBSTACLE_GAP)
    return rightmost_x < GAME_COLS - gap
