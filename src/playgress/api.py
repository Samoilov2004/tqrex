"""Public API: the track() generator and the Progress context manager."""

from __future__ import annotations

from collections.abc import Generator, Iterable
from typing import TypeVar

from playgress.config import TARGET_FPS, Theme
from playgress.models import ProgressState

T = TypeVar("T")


def track(
    iterable: Iterable[T],
    *,
    description: str = "Processing...",
    total: int | None = None,
    theme: Theme = Theme.AUTO,
    fps: int = TARGET_FPS,
    autoplay: bool = False,
    disable: bool = False,
) -> Generator[T, None, None]:
    """Iterate over *iterable* while the T-Rex game runs as a progress bar.

    Drop-in replacement for ``tqdm.tqdm``.

    Args:
        iterable:    Any iterable to consume.
        description: Label shown beside the progress bar.
        total:       Item count. Inferred from ``len()`` when omitted.
        theme:       Sprite theme — AUTO, ASCII_BLOCK, or EMOJI.
        fps:         Target render frame rate (default 30).
        autoplay:    Start with the AI autoplay controller enabled.
        disable:     Bypass the game; yield items with no terminal output.

    Yields:
        Items from *iterable*, unchanged.
    """
    if total is None:
        try:
            total = len(iterable)  # type: ignore[arg-type]
        except TypeError:
            total = 0

    if disable:
        yield from iterable
        return

    state = ProgressState(total=total, description=description)

    # TODO(Phase 4): instantiate Renderer + GameLoop + InputHandler,
    #                launch daemon threads, pass *state* and a shared Lock.

    try:
        for item in iterable:
            yield item
            state.completed += 1
    finally:
        state.is_complete = True
        # TODO(Phase 4): signal shutdown Event; join render thread.


class Progress:
    """Context manager for manual (non-iterable) progress control.

    Example::

        with Progress(total=len(files), description="Uploading") as p:
            for f in files:
                upload(f)
                p.update(1)
    """

    def __init__(
        self,
        total: int,
        description: str = "Processing...",
        theme: Theme = Theme.AUTO,
        fps: int = TARGET_FPS,
        autoplay: bool = False,
    ) -> None:
        self._state = ProgressState(total=total, description=description)
        self._theme = theme
        self._fps = fps
        self._autoplay = autoplay
        # TODO(Phase 4): store thread handles

    def update(self, n: int = 1) -> None:
        """Advance the progress counter by *n* steps (thread-safe in Phase 4)."""
        self._state.completed = min(self._state.completed + n, self._state.total)

    def __enter__(self) -> Progress:
        # TODO(Phase 4): start daemon threads
        return self

    def __exit__(self, *_: object) -> None:
        self._state.is_complete = True
        # TODO(Phase 4): signal shutdown; join threads
