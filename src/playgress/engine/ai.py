from __future__ import annotations

from playgress.config import (
    BIRD_ROW_HIGH,
    DINO_COL,
    DINO_W,
    ObstacleType,
)
from playgress.models import DinoState, InputEvent, ObstacleData

_DINO_HITBOX_RIGHT: float = float(DINO_COL + DINO_W - 2)

_BASE_DIST: float = 12.0
_SPEED_MULT: float = 16.0


def decide(
    dino: DinoState,
    obstacles: list[ObstacleData],
    is_dead: bool,
    speed: float,
) -> InputEvent | None:
    if is_dead:
        return InputEvent.RESTART

    nearest = _nearest(obstacles)
    if nearest is None:
        return None

    dist = nearest.x - DINO_COL
    jump_threshold = _BASE_DIST + speed * _SPEED_MULT

    if dist > jump_threshold:
        return None

    if not dino.on_ground:
        return None

    if nearest.type in (ObstacleType.BIRD_SMALL, ObstacleType.BIRD_BIG):
        if nearest.top_row <= BIRD_ROW_HIGH:
            return InputEvent.DUCK_START
        return InputEvent.JUMP

    return InputEvent.JUMP


def _nearest(obstacles: list[ObstacleData]) -> ObstacleData | None:
    ahead = [o for o in obstacles if o.x + o.width > _DINO_HITBOX_RIGHT]
    return min(ahead, key=lambda o: o.x) if ahead else None
