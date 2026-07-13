"""Shared dataclasses and enums used across all playgress modules."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto

# ── Enumerations ───────────────────────────────────────────────────────────────


class ObstacleType(Enum):
    CACTUS_SMALL = auto()
    CACTUS_LARGE = auto()
    CACTUS_GROUP = auto()  # two small cacti side-by-side
    PTERODACTYL = auto()


class InputEvent(Enum):
    JUMP = auto()
    DUCK_START = auto()
    DUCK_END = auto()
    RESTART = auto()
    TOGGLE_AUTOPLAY = auto()
    PAUSE = auto()
    QUIT = auto()


# ── Geometry ───────────────────────────────────────────────────────────────────


@dataclass
class Vector2D:
    x: float
    y: float

    def __add__(self, other: Vector2D) -> Vector2D:
        return Vector2D(self.x + other.x, self.y + other.y)

    def __iadd__(self, other: Vector2D) -> Vector2D:
        self.x += other.x
        self.y += other.y
        return self

    def __mul__(self, scalar: float) -> Vector2D:
        return Vector2D(self.x * scalar, self.y * scalar)


@dataclass
class AABB:
    """Axis-Aligned Bounding Box — the canonical hitbox primitive."""

    x: float
    y: float
    width: float
    height: float

    def intersects(self, other: AABB) -> bool:
        return (
            self.x < other.x + other.width
            and self.x + self.width > other.x
            and self.y < other.y + other.height
            and self.y + self.height > other.y
        )


# ── Game objects ───────────────────────────────────────────────────────────────


@dataclass
class DinoState:
    position: Vector2D = field(default_factory=lambda: Vector2D(10.0, 0.0))
    velocity: Vector2D = field(default_factory=lambda: Vector2D(0.0, 0.0))
    is_jumping: bool = False
    is_ducking: bool = False
    is_dead: bool = False
    animation_frame: int = 0


@dataclass
class Obstacle:
    type: ObstacleType
    position: Vector2D
    width: int = 2
    height: int = 3


@dataclass
class GameState:
    dino: DinoState = field(default_factory=DinoState)
    obstacles: list[Obstacle] = field(default_factory=list)
    score: float = 0.0
    speed: float = 10.0  # columns per second
    is_paused: bool = False
    is_game_over: bool = False
    autoplay: bool = False
    frame: int = 0


# ── Progress tracking ──────────────────────────────────────────────────────────


@dataclass
class ProgressState:
    total: int
    completed: int = 0
    description: str = "Processing..."
    start_time: float = field(default_factory=time.monotonic)
    is_complete: bool = False

    @property
    def fraction(self) -> float:
        return 1.0 if self.total == 0 else min(self.completed / self.total, 1.0)

    @property
    def elapsed(self) -> float:
        return time.monotonic() - self.start_time

    @property
    def eta(self) -> float | None:
        f = self.fraction
        if f <= 0.0:
            return None
        return self.elapsed / f - self.elapsed
