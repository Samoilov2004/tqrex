"""Cross-platform non-blocking raw keyboard input."""

from __future__ import annotations

import queue
import sys
import threading
from typing import TYPE_CHECKING

from playgress.models import InputEvent

if TYPE_CHECKING:
    pass  # future: import platform-specific types here

# Raw byte sequences → InputEvent mapping (ANSI escape codes + single chars).
_KEY_MAP: dict[bytes, InputEvent] = {
    b" ": InputEvent.JUMP,
    b"\x1b[A": InputEvent.JUMP,  # up-arrow (ANSI)
    b"\x00H": InputEvent.JUMP,  # up-arrow (Windows scan code)
    b"\x1b[B": InputEvent.DUCK_START,  # down-arrow (ANSI)
    b"\x00P": InputEvent.DUCK_START,  # down-arrow (Windows scan code)
    b"r": InputEvent.RESTART,
    b"R": InputEvent.RESTART,
    b"a": InputEvent.TOGGLE_AUTOPLAY,
    b"A": InputEvent.TOGGLE_AUTOPLAY,
    b"p": InputEvent.PAUSE,
    b"P": InputEvent.PAUSE,
    b"q": InputEvent.QUIT,
    b"Q": InputEvent.QUIT,
}


class InputHandler:
    """Reads keypresses in a background daemon thread and pushes InputEvents.

    Architecture:
        - POSIX: saves/restores terminal attributes via ``termios``; reads with
          ``select.select()`` so the thread never busy-waits.
        - Windows: polls ``msvcrt.kbhit()`` with a short sleep (1 ms) to avoid
          burning CPU.
        - Duck-release is synthesised: after DOWN is pressed, the handler posts
          a DUCK_END event on the next read that is *not* a down-arrow, or after
          a fixed timeout. (Implemented in Phase 2.)
    """

    def __init__(
        self,
        event_queue: queue.Queue[InputEvent],
        shutdown: threading.Event,
    ) -> None:
        self._queue = event_queue
        self._shutdown = shutdown

    def start(self) -> threading.Thread:
        """Spawn and return the daemon input thread."""
        t = threading.Thread(target=self._run, name="playgress-input", daemon=True)
        t.start()
        return t

    def _run(self) -> None:
        """Dispatch to the platform-appropriate implementation."""
        if sys.platform == "win32":
            self._run_windows()
        else:
            self._run_posix()

    def _run_posix(self) -> None:
        """POSIX: raw mode + select.select() for zero-latency, zero-spin reads."""
        # TODO(Phase 2): implement using termios / tty / select
        pass

    def _run_windows(self) -> None:
        """Windows: poll msvcrt.kbhit() at ~1 ms intervals."""
        # TODO(Phase 2): implement using msvcrt
        pass

    @staticmethod
    def _parse(raw: bytes) -> InputEvent | None:
        """Map a raw byte sequence to an InputEvent, returning None if unmapped."""
        return _KEY_MAP.get(raw)
