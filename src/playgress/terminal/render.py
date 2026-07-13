"""Double-buffered terminal renderer — redraws only changed rows."""

from __future__ import annotations

from playgress.config import GAME_COLS, GAME_ROWS, Theme
from playgress.models import GameState, ProgressState

# ANSI escape sequences used for cursor control.
_CURSOR_UP = "\x1b[{}A"  # move up N rows
_CURSOR_COL0 = "\x1b[0G"  # move to column 0
_ERASE_LINE = "\x1b[2K"  # erase current line
_HIDE_CURSOR = "\x1b[?25l"
_SHOW_CURSOR = "\x1b[?25h"


class Renderer:
    """Maintains a string frame-buffer and flushes only dirty lines.

    Screen layout (rows, 0-indexed within the game area):
        0       score line + autoplay toggle
        1       blank separator
        2–7     game play area  (6 rows)
        8       ground line  (▀▀▀▀…)
        9       progress bar  (████░░░ 73%)
        10      ETA / description label
    """

    def __init__(self, theme: Theme, cols: int = GAME_COLS) -> None:
        self._theme = theme
        self._cols = cols
        self._prev_frame: list[str] = []
        self._first_render: bool = True

    def render(self, game: GameState, progress: ProgressState) -> None:
        """Compose a new frame and write only the rows that changed."""
        # TODO(Phase 4): implement
        pass

    def clear(self) -> None:
        """Erase the entire game area on graceful shutdown."""
        # TODO(Phase 4): implement
        pass

    # ── Private helpers ────────────────────────────────────────────────────────

    def _build_frame(self, game: GameState, progress: ProgressState) -> list[str]:
        """Return a list of strings (one per row) representing the full frame."""
        # TODO(Phase 4): compose score, game area, ground, progress bar, ETA
        return ["" for _ in range(GAME_ROWS + 1)]

    def _flush_diff(self, new_frame: list[str]) -> None:
        """Move the cursor and overwrite only rows that differ from last frame."""
        # TODO(Phase 4): implement diff-write using ANSI escape sequences
        pass

    @staticmethod
    def _progress_bar(fraction: float, width: int = 40) -> str:
        """Render a simple block progress bar string."""
        filled = round(fraction * width)
        pct = f"{fraction * 100:5.1f}%"
        return "█" * filled + "░" * (width - filled) + f" {pct}"

    @staticmethod
    def _eta_label(progress: ProgressState) -> str:
        """Format the ETA / elapsed label line."""
        eta = progress.eta
        if eta is None:
            return f"{progress.description}  elapsed: {progress.elapsed:.0f}s"
        return f"{progress.description}  ETA: {eta:.0f}s"
