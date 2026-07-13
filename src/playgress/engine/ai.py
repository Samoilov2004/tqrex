"""Deterministic autoplay controller — no ML, pure look-ahead geometry."""

from __future__ import annotations

from playgress.models import GameState, InputEvent, Obstacle

# How many frames ahead to project the dino's jump arc when checking clearance.
_LOOKAHEAD_FRAMES: int = 45

# Minimum horizontal distance to nearest obstacle before the AI reacts.
# Tuned in Phase 5; placeholder keeps the interface stable.
_REACT_DISTANCE: float = 20.0


def decide(state: GameState) -> InputEvent | None:
    """Return the next action the autoplay AI should take, or None to do nothing.

    Called once per game frame from GameLoop._process_input().
    The controller is intentionally stateless — it derives intent solely from
    the current GameState snapshot, making it deterministic and testable.
    """
    if state.is_game_over:
        return InputEvent.RESTART
    if state.is_paused or state.dino.is_dead:
        return None

    nearest = _nearest_obstacle(state)
    if nearest is None:
        return None

    # TODO(Phase 5): implement full jump/duck decision logic
    return None


def _nearest_obstacle(state: GameState) -> Obstacle | None:
    """Return the closest obstacle ahead of the dino, or None."""
    dino_x = state.dino.position.x
    ahead = [obs for obs in state.obstacles if obs.position.x + obs.width > dino_x]
    if not ahead:
        return None
    return min(ahead, key=lambda o: o.position.x)


def _time_to_reach(dino_x: float, obstacle: Obstacle, speed: float) -> float:
    """Seconds until the dino's leading edge reaches the obstacle's leading edge."""
    distance = obstacle.position.x - dino_x
    if distance <= 0 or speed <= 0:
        return 0.0
    return distance / speed
