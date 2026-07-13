"""All tuneable constants and sprite definitions for both themes."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import TypeAlias

# A single sprite frame: one string per rendered row (top → bottom).
SpriteFrame: TypeAlias = list[str]


# ── Theme ──────────────────────────────────────────────────────────────────────


class Theme(Enum):
    AUTO = auto()  # detect terminal capabilities at runtime
    ASCII_BLOCK = auto()  # block characters: █ ▄ ▀ ▌ ▐
    EMOJI = auto()  # emoji fallback: 🦖 🌵 🦅


# ── Sprite container ───────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Sprite:
    """Visual representation of a game object.

    *frames* contains one or more animation frames; the renderer cycles through
    them based on the game tick counter. Every frame must have the same
    ``width`` × ``height`` bounding box.
    """

    frames: tuple[SpriteFrame, ...]
    width: int  # character columns
    height: int  # terminal rows


# ── Terminal / Game geometry ───────────────────────────────────────────────────

GAME_COLS: int = 80  # usable display width in character columns
GAME_ROWS: int = 12  # total rows the game occupies (incl. progress bar)
GROUND_ROW: int = 8  # 0-indexed row of the ground line within the game area


# ── Physics ────────────────────────────────────────────────────────────────────

GRAVITY: float = 0.55  # added to y-velocity each frame
JUMP_VELOCITY: float = -4.2  # negative = upward
INITIAL_SPEED: float = 10.0  # obstacle scroll speed (cols/sec) at game start
SPEED_INCREMENT: float = 0.0015  # added to speed each frame


# ── Scoring ────────────────────────────────────────────────────────────────────

SCORE_PER_FRAME: float = 0.1
PTERODACTYL_UNLOCK_SCORE: int = 300  # pterodactyls only spawn above this score


# ── FPS ────────────────────────────────────────────────────────────────────────

TARGET_FPS: int = 30
FRAME_DURATION: float = 1.0 / TARGET_FPS  # ~33.3 ms


# ── Obstacle generation ────────────────────────────────────────────────────────

MIN_OBSTACLE_GAP: int = 25  # columns between obstacle right-edge and next spawn
MAX_OBSTACLE_GAP: int = 65


# ─────────────────────────────────────────────────────────────────────────────
# Sprite definitions
#
# ASCII_BLOCK theme uses Unicode block elements. Each string in a frame is
# exactly ``width`` characters wide (pad with spaces where needed).
# EMOJI theme falls back to single emoji per object; the renderer scales the
# hitbox to match.
#
# NOTE: exact pixel-art tuning happens in Phase 3. Values here are placeholder
# geometry stubs that establish the sprite API contract.
# ─────────────────────────────────────────────────────────────────────────────

# ── Dino (ASCII) ──────────────────────────────────────────────────────────────

DINO_RUN_ASCII = Sprite(
    frames=(
        # frame 0 — left leg forward
        [
            "  ██  ",
            " ████ ",
            "██████",
            "  ██  ",
            "  ██  ",
            " █  █ ",
        ],
        # frame 1 — right leg forward
        [
            "  ██  ",
            " ████ ",
            "██████",
            "  ██  ",
            "  ██  ",
            "  █ █ ",
        ],
    ),
    width=6,
    height=6,
)

DINO_DUCK_ASCII = Sprite(
    frames=(
        [
            "        ",
            " ██████ ",
            "████████",
            " ██  ██ ",
        ],
        [
            "        ",
            " ██████ ",
            "████████",
            "  ██ ██ ",
        ],
    ),
    width=8,
    height=4,
)

DINO_DEAD_ASCII = Sprite(
    frames=(
        [
            "  ██  ",
            " ▄██▄ ",
            "██████",
            "  ██  ",
            "  ██  ",
            " █  █ ",
        ],
    ),
    width=6,
    height=6,
)

# ── Cacti (ASCII) ─────────────────────────────────────────────────────────────

CACTUS_SMALL_ASCII = Sprite(
    frames=(
        [
            " █ ",
            "███",
            " █ ",
            " █ ",
        ],
    ),
    width=3,
    height=4,
)

CACTUS_LARGE_ASCII = Sprite(
    frames=(
        [
            "  █  ",
            "█████",
            "  █  ",
            "  █  ",
            "  █  ",
        ],
    ),
    width=5,
    height=5,
)

CACTUS_GROUP_ASCII = Sprite(
    frames=(
        [
            " █  █ ",
            "██████",
            " █  █ ",
            " █  █ ",
        ],
    ),
    width=6,
    height=4,
)

# ── Pterodactyl (ASCII) ───────────────────────────────────────────────────────

PTERO_ASCII = Sprite(
    frames=(
        # wings up
        [
            "▄█▄",
            "███",
            " █ ",
        ],
        # wings down
        [
            " █ ",
            "███",
            "▀█▀",
        ],
    ),
    width=3,
    height=3,
)

# ── Emoji theme ───────────────────────────────────────────────────────────────
# Emoji are double-width in most terminals. width=2 reflects that.

DINO_RUN_EMOJI = Sprite(frames=(["🦖"], ["🦖"]), width=2, height=1)
DINO_DUCK_EMOJI = Sprite(frames=(["🦖"], ["🦖"]), width=2, height=1)
DINO_DEAD_EMOJI = Sprite(frames=(["💀"],), width=2, height=1)

CACTUS_SMALL_EMOJI = Sprite(frames=(["🌵"],), width=2, height=1)
CACTUS_LARGE_EMOJI = Sprite(frames=(["🌵"],), width=2, height=1)
CACTUS_GROUP_EMOJI = Sprite(frames=(["🌵🌵"],), width=4, height=1)

PTERO_EMOJI = Sprite(frames=(["🦅"], ["🦅"]), width=2, height=1)


# ── Sprite registry ────────────────────────────────────────────────────────────
# Keyed by (ObstacleType | "dino_run" | "dino_duck" | "dino_dead", Theme).
# Populated lazily at runtime via get_sprite() to avoid import-time side-effects.

from playgress.models import ObstacleType  # noqa: E402 — circular-safe at module level

_SPRITE_MAP: dict[tuple[str, Theme], Sprite] = {
    ("dino_run", Theme.ASCII_BLOCK): DINO_RUN_ASCII,
    ("dino_duck", Theme.ASCII_BLOCK): DINO_DUCK_ASCII,
    ("dino_dead", Theme.ASCII_BLOCK): DINO_DEAD_ASCII,
    (ObstacleType.CACTUS_SMALL.name, Theme.ASCII_BLOCK): CACTUS_SMALL_ASCII,
    (ObstacleType.CACTUS_LARGE.name, Theme.ASCII_BLOCK): CACTUS_LARGE_ASCII,
    (ObstacleType.CACTUS_GROUP.name, Theme.ASCII_BLOCK): CACTUS_GROUP_ASCII,
    (ObstacleType.PTERODACTYL.name, Theme.ASCII_BLOCK): PTERO_ASCII,
    ("dino_run", Theme.EMOJI): DINO_RUN_EMOJI,
    ("dino_duck", Theme.EMOJI): DINO_DUCK_EMOJI,
    ("dino_dead", Theme.EMOJI): DINO_DEAD_EMOJI,
    (ObstacleType.CACTUS_SMALL.name, Theme.EMOJI): CACTUS_SMALL_EMOJI,
    (ObstacleType.CACTUS_LARGE.name, Theme.EMOJI): CACTUS_LARGE_EMOJI,
    (ObstacleType.CACTUS_GROUP.name, Theme.EMOJI): CACTUS_GROUP_EMOJI,
    (ObstacleType.PTERODACTYL.name, Theme.EMOJI): PTERO_EMOJI,
}


def get_sprite(key: str, theme: Theme) -> Sprite:
    """Retrieve a sprite by key and theme, falling back to EMOJI if missing."""
    sprite = _SPRITE_MAP.get((key, theme))
    if sprite is None:
        sprite = _SPRITE_MAP[(key, Theme.EMOJI)]
    return sprite
