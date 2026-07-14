from __future__ import annotations

import os
import sys

from tqrex.config import (
    BOLD,
    CLOUD_H,
    CLOUD_SPRITES,
    DINO_COL,
    DINO_DEAD,
    DINO_DUCK,
    DINO_H,
    DINO_H_DUCK,
    DINO_RUN,
    GAME_H,
    GRAY,
    GREEN,
    GROUND_DECO,
    GROUND_LINE,
    HIDE_CURSOR,
    OBSTACLE_COLOR,
    OBSTACLE_SPRITE,
    RST,
    SHOW_CURSOR,
    T_BAR,
    T_DESC,
    T_GAME,
    T_GNDEC,
    T_GNDLN,
    T_SCORE,
    TOTAL_ROWS,
    ansi_at,
)
from tqrex.models import GameState


class Renderer:

    def __init__(self, cols: int) -> None:
        self._cols = cols

    def setup(self) -> None:
        if sys.platform == "win32":
            os.system("")
        sys.stdout.write(HIDE_CURSOR + "\x1b[2J\x1b[H")
        sys.stdout.flush()

    def teardown(self) -> None:
        sys.stdout.write(SHOW_CURSOR + ansi_at(TOTAL_ROWS + 2))
        sys.stdout.flush()

    def render(
        self,
        game: GameState,
        fraction: float,
        description: str,
        eta: float | None,
    ) -> None:
        frame = self._build_frame(game, fraction, description, eta)
        self._flush_overwrite(frame)

    def _build_frame(
        self,
        game: GameState,
        fraction: float,
        description: str,
        eta: float | None,
    ) -> list[str]:
        rows: list[str] = [""] * TOTAL_ROWS

        rows[T_SCORE - 1] = self._score_row(game)

        for gr in range(GAME_H):
            rows[T_GAME - 1 + gr] = self._game_row(game, gr)

        off = int(game.scroll) % len(GROUND_LINE)
        rows[T_GNDLN - 1] = RST + (GROUND_LINE * 2)[off: off + self._cols]
        rows[T_GNDEC - 1] = GRAY + (GROUND_DECO * 2)[off: off + self._cols] + RST

        rows[T_BAR - 1] = self._progress_row(fraction)
        rows[T_DESC - 1] = self._status_row(game, description, eta)

        return rows

    def _score_row(self, game: GameState) -> str:
        sc_raw = f"Score: {int(game.score):05d}"
        hi_raw = f"HI: {int(game.hi_score):05d}"
        pad = max(self._cols - len(sc_raw) - len(hi_raw), 2)
        return f"Score: {BOLD}{int(game.score):05d}{RST}" + " " * pad + hi_raw

    def _game_row(self, game: GameState, gr: int) -> str:
        chars: list[str] = [" "] * self._cols
        colors: list[str] = [""] * self._cols

        for cl in game.clouds:
            if cl.row <= gr <= cl.row + CLOUD_H - 1:
                spr = CLOUD_SPRITES[cl.kind]
                ri = gr - cl.row
                for ci, ch in enumerate(spr[ri]):
                    pos = int(cl.x) + ci
                    if ch != " " and 0 <= pos < self._cols:
                        chars[pos] = ch
                        colors[pos] = GRAY

        dbot = int(round(game.dino.y))
        dh = DINO_H_DUCK if game.dino.ducking else DINO_H
        dtop = dbot - dh + 1
        if dtop <= gr <= dbot:
            ri = gr - dtop
            if game.dino.dead:
                row_s = DINO_DEAD.frames[0][ri]
            elif game.dino.ducking:
                row_s = DINO_DUCK.frames[game.dino.anim_frame % 2][ri]
            else:
                row_s = DINO_RUN.frames[game.dino.anim_frame % 2][ri]
            for ci, ch in enumerate(row_s):
                pos = DINO_COL + ci
                if ch != " " and 0 <= pos < self._cols:
                    chars[pos] = ch
                    colors[pos] = GREEN

        for obs in game.obstacles:
            sprite = OBSTACLE_SPRITE[obs.type]
            spr_frame = sprite.frames[obs.anim_frame % len(sprite.frames)]
            if obs.top_row <= gr <= obs.top_row + obs.height - 1:
                ri = gr - obs.top_row
                if ri < len(spr_frame):
                    obs_color = OBSTACLE_COLOR[obs.type]
                    for ci, ch in enumerate(spr_frame[ri]):
                        pos = int(obs.x) + ci
                        if ch != " " and 0 <= pos < self._cols:
                            chars[pos] = ch
                            colors[pos] = obs_color

        return _encode_row(chars, colors)

    def _progress_row(self, fraction: float) -> str:
        bw = self._cols - 9
        fil = round(fraction * bw)
        return GREEN + "█" * fil + GRAY + "░" * (bw - fil) + RST + f" {fraction * 100:5.1f}%"

    def _status_row(self, game: GameState, description: str, eta: float | None) -> str:
        if game.dino.dead:
            msg = "  GAME OVER  ·  [R] Restart  ·  [Q] Quit"
        elif game.is_done:
            msg = f"  ✓ Done! Score: {int(game.score):05d}  ·  [R] Replay  ·  [Q] Quit"
        else:
            eta_str = f"  ETA: {eta:.0f}s" if eta is not None else ""
            msg = f"  [Space/↑] Jump  [↓] Duck  [R] Restart  [Q] Quit{eta_str}"
        return msg[: self._cols]

    def _flush_overwrite(self, frame: list[str]) -> None:
        buf: list[str] = ["\x1b[H"]
        last = len(frame) - 1
        for i, row in enumerate(frame):
            buf.append(row)
            buf.append("\x1b[K")
            if i < last:
                buf.append("\r\n")
        buf.append(ansi_at(TOTAL_ROWS + 1, 1))
        sys.stdout.write("".join(buf))
        sys.stdout.flush()


def _encode_row(chars: list[str], colors: list[str]) -> str:
    out: list[str] = []
    cur = ""
    for ch, clr in zip(chars, colors, strict=True):
        if clr != cur:
            out.append(clr if clr else RST)
            cur = clr
        out.append(ch)
    if cur:
        out.append(RST)
    return "".join(out)
