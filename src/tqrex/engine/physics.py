from __future__ import annotations

from tqrex.config import (
    ANIM_PERIOD,
    DINO_COL,
    DINO_H,
    DINO_H_DUCK,
    DINO_W,
    DUCK_FRAMES,
    FAST_DROP_V,
    GRAVITY,
    GROUND,
    HANG_FRAMES,
    JUMP_VELOCITY,
)
from tqrex.models import AABB, DinoState, ObstacleData


def apply_physics(dino: DinoState) -> None:
    if dino.on_ground:
        if dino.duck_frames > 0:
            dino.duck_frames -= 1
            if dino.duck_frames == 0:
                dino.ducking = False
        return

    if dino.fast_drop:
        dino.vy = FAST_DROP_V
    elif dino.hang_frames > 0:
        dino.hang_frames -= 1
    else:
        new_vy = dino.vy + GRAVITY
        if dino.vy < 0.0 <= new_vy:
            dino.hang_frames = HANG_FRAMES
            dino.vy = 0.0
        else:
            dino.vy = new_vy

    dino.y += dino.vy

    if dino.y >= float(GROUND):
        dino.y = float(GROUND)
        dino.vy = 0.0
        dino.on_ground = True
        if dino.fast_drop:
            dino.ducking = True
            dino.duck_frames = DUCK_FRAMES // 2
        dino.fast_drop = False


def try_jump(dino: DinoState) -> bool:
    if not dino.on_ground:
        return False
    dino.vy = JUMP_VELOCITY
    dino.on_ground = False
    dino.hang_frames = 0
    dino.ducking = False
    dino.duck_frames = 0
    dino.fast_drop = False
    return True


def start_duck(dino: DinoState) -> None:
    if dino.on_ground:
        dino.ducking = True
        dino.duck_frames = DUCK_FRAMES
    else:
        dino.fast_drop = True
        dino.hang_frames = 0


def advance_anim(dino: DinoState) -> None:
    dino.anim_counter += 1
    if dino.anim_counter >= ANIM_PERIOD:
        dino.anim_counter = 0
        dino.anim_frame += 1


def check_collision(dino: DinoState, obstacles: list[ObstacleData]) -> bool:
    if not obstacles:
        return False
    dbot = int(round(dino.y))
    dh = DINO_H_DUCK if dino.ducking else DINO_H
    dtop = dbot - dh + 1
    dhx1 = DINO_COL + 2
    dhx2 = DINO_COL + DINO_W - 2
    for obs in obstacles:
        obot = obs.top_row + obs.height - 1
        ohx1 = int(obs.x) + 1
        ohx2 = int(obs.x) + obs.width - 2
        if dhx1 <= ohx2 and dhx2 >= ohx1 and dtop <= obot and dbot >= obs.top_row:
            return True
    return False


def get_dino_hitbox(dino: DinoState) -> AABB:
    dh = DINO_H_DUCK if dino.ducking else DINO_H
    return AABB(
        x=float(DINO_COL + 2),
        y=float(int(round(dino.y)) - dh + 1),
        width=float(DINO_W - 4),
        height=float(dh),
    )
