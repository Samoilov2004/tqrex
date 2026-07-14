from __future__ import annotations

import os
import queue
import sys
import threading
from collections.abc import Generator, Iterable
from typing import TypeVar

from playgress.config import Theme
from playgress.engine.game import GameLoop
from playgress.models import InputEvent, ProgressState
from playgress.terminal.input import InputHandler
from playgress.terminal.render import Renderer

T = TypeVar("T")


def _get_cols() -> int:
    try:
        cols, _ = os.get_terminal_size(sys.stdout.fileno())
    except (OSError, AttributeError):
        cols = 80
    return min(max(cols, 40), 200)


def _is_interactive() -> bool:
    try:
        return sys.stdin.isatty() and sys.stdout.isatty()
    except AttributeError:
        return False


def track(
    iterable: Iterable[T],
    *,
    description: str = "Processing...",
    total: int | None = None,
    theme: Theme = Theme.AUTO,
    fps: int = 60,
    disable: bool = False,
) -> Generator[T, None, None]:
    if total is None:
        try:
            total = len(iterable)  # type: ignore[arg-type]
        except TypeError:
            total = 0

    if disable or not _is_interactive():
        yield from iterable
        return

    cols = _get_cols()
    state = ProgressState(total=total, description=description)
    lock = threading.Lock()
    input_queue: queue.Queue[InputEvent] = queue.Queue()
    shutdown = threading.Event()

    renderer = Renderer(cols=cols)
    game = GameLoop(
        progress=state,
        progress_lock=lock,
        input_queue=input_queue,
        shutdown=shutdown,
        renderer=renderer,
        cols=cols,
    )
    input_handler = InputHandler(event_queue=input_queue, shutdown=shutdown)

    renderer.setup()
    input_handler.start()
    game.start()

    try:
        for item in iterable:
            yield item
            with lock:
                state.completed += 1
    finally:
        with lock:
            state.is_complete = True
        shutdown.wait()

    renderer.teardown()
    sys.stdout.write("\n")
    sys.stdout.flush()


class Progress:

    def __init__(
        self,
        total: int,
        description: str = "Processing...",
        theme: Theme = Theme.AUTO,
        fps: int = 60,
    ) -> None:
        self._state = ProgressState(total=total, description=description)
        self._theme = theme
        self._lock = threading.Lock()
        self._shutdown = threading.Event()
        self._tty = _is_interactive()
        self._renderer: Renderer | None = None

    @property
    def fraction(self) -> float:
        return self._state.fraction

    def update(self, n: int = 1) -> None:
        with self._lock:
            self._state.completed = min(
                self._state.completed + n, self._state.total
            )

    def set_description(self, text: str) -> None:
        with self._lock:
            self._state.description = text

    def __enter__(self) -> Progress:
        if self._tty:
            cols = _get_cols()
            input_queue: queue.Queue[InputEvent] = queue.Queue()
            self._renderer = Renderer(cols=cols)
            self._game = GameLoop(
                progress=self._state,
                progress_lock=self._lock,
                input_queue=input_queue,
                shutdown=self._shutdown,
                renderer=self._renderer,
                cols=cols,
            )
            self._input = InputHandler(
                event_queue=input_queue, shutdown=self._shutdown
            )
            self._renderer.setup()
            self._input.start()
            self._game.start()
        return self

    def __exit__(self, *_: object) -> None:
        with self._lock:
            self._state.is_complete = True
        if self._tty:
            self._shutdown.wait()
            if self._renderer is not None:
                self._renderer.teardown()
            sys.stdout.write("\n")
            sys.stdout.flush()
