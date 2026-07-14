from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto

from tqrex.config import GROUND, INITIAL_SPEED, ObstacleType  # noqa: F401 (re-export)


class InputEvent(Enum):
    JUMP = auto()
    DUCK_START = auto()
    RESTART = auto()
    QUIT = auto()


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


@dataclass
class Obstacle:
    type: ObstacleType
    position: Vector2D
    width: int = 2
    height: int = 3


@dataclass
class DinoState:
    y: float = float(GROUND)
    vy: float = 0.0
    on_ground: bool = True
    ducking: bool = False
    duck_frames: int = 0
    fast_drop: bool = False
    hang_frames: int = 0
    dead: bool = False
    anim_frame: int = 0
    anim_counter: int = 0
    position: Vector2D = field(default_factory=lambda: Vector2D(0.0, 0.0))


@dataclass
class ObstacleData:
    type: ObstacleType
    x: float
    top_row: int
    width: int
    height: int
    anim_frame: int = 0
    anim_counter: int = 0


@dataclass
class CloudData:
    x: float
    row: int
    kind: int
    speed: float


@dataclass
class GameState:
    dino: DinoState = field(default_factory=DinoState)
    obstacles: list[ObstacleData] = field(default_factory=list)
    clouds: list[CloudData] = field(default_factory=list)
    score: float = 0.0
    hi_score: float = 0.0
    speed: float = INITIAL_SPEED
    scroll: float = 0.0
    frame: int = 0
    is_dead: bool = False
    is_done: bool = False


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
