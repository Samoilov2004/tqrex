from __future__ import annotations

import queue
import sys
import threading
import time

from tqrex.models import InputEvent

_KEY_MAP: dict[bytes, InputEvent] = {
    b" ": InputEvent.JUMP,
    b"\x1b[A": InputEvent.JUMP,
    b"\x00H": InputEvent.JUMP,
    b"\xe0H": InputEvent.JUMP,
    b"\x1b[B": InputEvent.DUCK_START,
    b"\x00P": InputEvent.DUCK_START,
    b"\xe0P": InputEvent.DUCK_START,
    b"r": InputEvent.RESTART,
    b"R": InputEvent.RESTART,
    b"q": InputEvent.QUIT,
    b"Q": InputEvent.QUIT,
    b"\x03": InputEvent.QUIT,
}


class InputHandler:
    def __init__(
        self,
        event_queue: queue.Queue[InputEvent],
        shutdown: threading.Event,
    ) -> None:
        self._queue = event_queue
        self._shutdown = shutdown

    def start(self) -> threading.Thread:
        t = threading.Thread(target=self._run, name="tqrex-input", daemon=True)
        t.start()
        return t

    def _run(self) -> None:
        if sys.platform == "win32":
            self._run_windows()
        else:
            self._run_posix()

    def _run_posix(self) -> None:
        import os as _os
        import select
        import termios
        import tty

        fd = sys.stdin.fileno()
        old_attrs = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while not self._shutdown.is_set():
                ready, _, _ = select.select([fd], [], [], 0.04)
                if not ready:
                    continue
                ch = _os.read(fd, 1)
                if ch == b"\x1b":
                    r2, _, _ = select.select([fd], [], [], 0.02)
                    if r2:
                        seq = _os.read(fd, 2)
                        event = _KEY_MAP.get(b"\x1b" + seq)
                    else:
                        event = None
                else:
                    event = _KEY_MAP.get(ch)
                self._dispatch(event)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_attrs)

    def _run_windows(self) -> None:
        import msvcrt  # type: ignore[import]

        while not self._shutdown.is_set():
            if not msvcrt.kbhit():
                time.sleep(0.008)
                continue
            ch = msvcrt.getch()
            if ch in (b"\xe0", b"\x00"):
                ext = msvcrt.getch() if msvcrt.kbhit() else b""
                event = _KEY_MAP.get(ch + ext)
            else:
                event = _KEY_MAP.get(ch)
            self._dispatch(event)

    def _dispatch(self, event: InputEvent | None) -> None:
        if event is None:
            return
        self._queue.put_nowait(event)
        if event is InputEvent.QUIT:
            self._shutdown.set()
