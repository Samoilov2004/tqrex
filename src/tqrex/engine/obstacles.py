from __future__ import annotations

import random

from tqrex.config import (
    ANIM_PERIOD,
    BIG_BIRD_ROW,
    BIRD_ROW_HIGH,
    BIRD_ROW_LOW,
    BIRD_UNLOCK_SCORE,
    CACT_GROUP_TOP,
    CACT_SHORT_TOP,
    CACT_SINGLE_TOP,
    OBSTACLE_SPRITE,
    ObstacleType,
)
from tqrex.models import ObstacleData


def spawn_obstacle(score: float, speed: float, cols: int) -> ObstacleData:
    birds_ok = score >= BIRD_UNLOCK_SCORE
    r = random.random()

    if not birds_ok or r < 0.75:
        t = random.random()
        if t < 0.50:
            otype, top_row = ObstacleType.CACTUS_SINGLE, CACT_SINGLE_TOP
        elif t < 0.75:
            otype, top_row = ObstacleType.CACTUS_SHORT, CACT_SHORT_TOP
        else:
            otype, top_row = ObstacleType.CACTUS_GROUP, CACT_GROUP_TOP
    else:
        t = random.random()
        if t < 0.15:
            otype, top_row = ObstacleType.BIRD_BIG, BIG_BIRD_ROW
        elif t < 0.55:
            otype, top_row = ObstacleType.BIRD_SMALL, BIRD_ROW_LOW
        else:
            otype, top_row = ObstacleType.BIRD_SMALL, BIRD_ROW_HIGH

    sprite = OBSTACLE_SPRITE[otype]
    return ObstacleData(
        type=otype,
        x=float(cols),
        top_row=top_row,
        width=sprite.width,
        height=sprite.height,
    )


def advance_obstacles(obstacles: list[ObstacleData], speed: float) -> list[ObstacleData]:
    alive: list[ObstacleData] = []
    for obs in obstacles:
        obs.x -= speed
        obs.anim_counter += 1
        if obs.anim_counter >= ANIM_PERIOD:
            obs.anim_counter = 0
            n_frames = len(OBSTACLE_SPRITE[obs.type].frames)
            obs.anim_frame = (obs.anim_frame + 1) % n_frames
        if obs.x + obs.width > 0:
            alive.append(obs)
    return alive


def should_spawn(obstacles: list[ObstacleData], speed: float, cols: int) -> bool:
    if not obstacles:
        return True
    rightmost = max(obs.x + obs.width for obs in obstacles)
    min_gap = max(30, int(48 - speed * 8))
    max_gap = max(45, int(65 - speed * 8))
    return rightmost < cols - random.randint(min_gap, max_gap)
