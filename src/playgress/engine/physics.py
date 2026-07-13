"""Gravity, jump impulse, ducking, and AABB collision detection."""

from __future__ import annotations

from playgress.models import AABB, DinoState, Obstacle

# Standing hitbox is narrower than the sprite to give a fair margin.
_DINO_STAND_W = 4.0
_DINO_STAND_H = 5.0
_DINO_DUCK_W = 6.0
_DINO_DUCK_H = 2.5
_DINO_X_OFFSET = 1.0  # horizontal inset from sprite left edge


def apply_gravity(dino: DinoState) -> None:
    """Mutate *dino* velocity and position by one frame of gravity."""
    # TODO(Phase 3): implement
    pass


def try_jump(dino: DinoState) -> bool:
    """Apply jump impulse when dino is grounded. Returns True if the jump fired."""
    # TODO(Phase 3): implement
    return False


def set_ducking(dino: DinoState, *, ducking: bool) -> None:
    """Toggle ducking state; adjust position so the dino stays on the ground."""
    # TODO(Phase 3): implement
    pass


def get_dino_hitbox(dino: DinoState) -> AABB:
    """Return the current AABB for the dino (smaller while ducking)."""
    # TODO(Phase 3): implement with proper offsets
    w = _DINO_DUCK_W if dino.is_ducking else _DINO_STAND_W
    h = _DINO_DUCK_H if dino.is_ducking else _DINO_STAND_H
    return AABB(dino.position.x + _DINO_X_OFFSET, dino.position.y, w, h)


def get_obstacle_hitbox(obstacle: Obstacle) -> AABB:
    """Return the AABB for an obstacle (inset slightly for fairness)."""
    # TODO(Phase 3): per-type inset values
    return AABB(
        obstacle.position.x + 0.5,
        obstacle.position.y,
        obstacle.width - 1.0,
        obstacle.height,
    )


def check_collision(dino: DinoState, obstacles: list[Obstacle]) -> bool:
    """Return True if the dino's hitbox intersects any obstacle hitbox."""
    dino_box = get_dino_hitbox(dino)
    return any(dino_box.intersects(get_obstacle_hitbox(obs)) for obs in obstacles)
