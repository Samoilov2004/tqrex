from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum, auto
from typing import TypeAlias

SpriteFrame: TypeAlias = list[str]


class Theme(Enum):
    AUTO = auto()
    ASCII_BLOCK = auto()
    EMOJI = auto()


class ObstacleType(Enum):
    CACTUS_SINGLE = auto()
    CACTUS_SHORT = auto()
    CACTUS_GROUP = auto()
    BIRD_SMALL = auto()
    BIRD_BIG = auto()


@dataclass(frozen=True)
class Sprite:
    frames: tuple[SpriteFrame, ...]
    width: int
    height: int


RST: str = "\x1b[0m"
GREEN: str = "\x1b[32m"
RED: str = "\x1b[31m"
YEL: str = "\x1b[33m"
MAG: str = "\x1b[35m"
GRAY: str = "\x1b[90m"
BOLD: str = "\x1b[1m"
HIDE_CURSOR: str = "\x1b[?25l"
SHOW_CURSOR: str = "\x1b[?25h"


def ansi_at(row: int, col: int = 1) -> str:
    return f"\x1b[{row};{col}H"


def ansi_eol() -> str:
    return "\x1b[K"


GAME_H: int = 13
GROUND: int = GAME_H - 1

T_SCORE: int = 1
T_GAME: int = 2
T_GNDLN: int = T_GAME + GAME_H
T_GNDEC: int = T_GNDLN + 1
T_BAR: int = T_GNDEC + 1
T_DESC: int = T_BAR + 1
TOTAL_ROWS: int = T_DESC

DINO_COL: int = 4
DINO_W: int = 12
DINO_H: int = 5
DINO_H_DUCK: int = 4

FPS: int = 60
TARGET_FPS: int = FPS
FRAME_DURATION: float = 1.0 / FPS

_JH: int = 5
_JD: int = FPS // 4
GRAVITY: float = 2.0 * _JH / (_JD * _JD)
JUMP_VELOCITY: float = -(2.0 * _JH / _JD)
FAST_DROP_V: float = abs(JUMP_VELOCITY) * 0.8
HANG_FRAMES: int = 2
DUCK_FRAMES: int = FPS // 2 + 1
ANIM_PERIOD: int = FPS // 12

_SF: float = 24.0 / FPS
CLOUD_SPEED_SCALE: float = _SF
INITIAL_SPEED: float = 1.4 * _SF
MAX_SPEED: float = 3.5 * _SF

SPEED_STAGES: list[tuple[int, float]] = [
    (0, 1.4 * _SF),
    (100, 1.8 * _SF),
    (300, 2.2 * _SF),
    (500, 2.8 * _SF),
    (1000, 3.0 * _SF),
    (2500, 3.2 * _SF),
    (3000, 3.3 * _SF),
    (6000, 3.5 * _SF),
]

BIRD_UNLOCK_SCORE: int = 300
SCORE_PER_FRAME: float = 0.5

CACT_SINGLE_TOP: int = GROUND - 3 + 1
CACT_SHORT_TOP: int = GROUND - 2 + 1
CACT_GROUP_TOP: int = GROUND - 3 + 1
BIRD_ROW_LOW: int = GROUND - 2
BIRD_ROW_HIGH: int = GROUND - 6
BIG_BIRD_ROW: int = GROUND - 7

DINO_RUN = Sprite(
    frames=(
        [
            "       ++++ ",
            "++    ++Q+++",
            " + +++++_ww ",
            "  ++++++    ",
            "   |   |    ",
        ],
        [
            "       ++++ ",
            " +    ++Q+++",
            " + +++++_ww ",
            "  ++++++    ",
            "   /   /    ",
        ],
    ),
    width=DINO_W,
    height=DINO_H,
)

DINO_DUCK = Sprite(
    frames=(
        [
            "       ++++ ",
            " -    ++@+++",
            "  ++++++__w ",
            "   :   :    ",
        ],
        [
            "       ++++ ",
            " +    ++@+++",
            "  ++++++__w ",
            "   ;   ;    ",
        ],
    ),
    width=DINO_W,
    height=DINO_H_DUCK,
)

DINO_DEAD = Sprite(
    frames=(
        [
            "       ++++ ",
            "++    ++X+++",
            " + +++++_ww ",
            "  ++++++    ",
            "   |   |    ",
        ],
    ),
    width=DINO_W,
    height=DINO_H,
)

CACTUS_SINGLE = Sprite(
    frames=([" | ", "/|\\", " | "],),
    width=3,
    height=3,
)

CACTUS_SHORT = Sprite(
    frames=(["/:\\/:\\", " | |"],),
    width=6,
    height=2,
)

CACTUS_GROUP = Sprite(
    frames=(["    |  ", "/|\\/|\\", " |  |"],),
    width=7,
    height=3,
)

BIRD_SMALL = Sprite(
    frames=(
        [" |   ", "<o=- ", " |   "],
        [" /   ", "<O=- ", " \\   "],
    ),
    width=5,
    height=3,
)

BIRD_BIG = Sprite(
    frames=(
        ["  /\\    ", " /  \\   ", "<ooo=-- ", " \\__/   "],
        ["  /\\    ", " /  \\   ", "<OOO=-- ", " \\__/   "],
    ),
    width=8,
    height=4,
)

CLOUD_SPRITES: tuple[SpriteFrame, ...] = (
    ["   .--.    ", " .(    ).  ", "(___.__)   "],
    ["  .-.      ", " (   ).    ", "(___(__)   "],
    ["    .--.   ", ".-(    )-. ", "(________)  "],
)
CLOUD_W: int = 11
CLOUD_H: int = 3

OBSTACLE_SPRITE: dict[ObstacleType, Sprite] = {
    ObstacleType.CACTUS_SINGLE: CACTUS_SINGLE,
    ObstacleType.CACTUS_SHORT: CACTUS_SHORT,
    ObstacleType.CACTUS_GROUP: CACTUS_GROUP,
    ObstacleType.BIRD_SMALL: BIRD_SMALL,
    ObstacleType.BIRD_BIG: BIRD_BIG,
}

OBSTACLE_COLOR: dict[ObstacleType, str] = {
    ObstacleType.CACTUS_SINGLE: RED,
    ObstacleType.CACTUS_SHORT: RED,
    ObstacleType.CACTUS_GROUP: RED,
    ObstacleType.BIRD_SMALL: YEL,
    ObstacleType.BIRD_BIG: MAG,
}

_ground_rng: random.Random = random.Random(42)
GROUND_LINE: str = "".join(_ground_rng.choice("_" * 8 + "=~-^") for _ in range(800))
GROUND_DECO: str = "".join(_ground_rng.choice(" " * 6 + ".,',`-") for _ in range(800))
