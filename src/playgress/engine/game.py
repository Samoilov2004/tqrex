"""Core game loop: orchestrates physics, obstacles, rendering, and input."""

from __future__ import annotations

import queue
import threading
import time

from playgress.config import FRAME_DURATION
from playgress.models import GameState, InputEvent, ProgressState


class GameLoop:
    """Runs the T-Rex game at ~TARGET_FPS in a daemon thread.

    Thread ownership model:
        - This object *owns* all mutable GameState; no other thread touches it.
        - The main thread writes to ProgressState under *progress_lock*.
        - The input thread pushes InputEvent into *input_queue* (non-blocking).
        - The shutdown Event tells this loop to exit cleanly.
    """

    def __init__(
        self,
        progress: ProgressState,
        progress_lock: threading.Lock,
        input_queue: queue.Queue[InputEvent],
        shutdown: threading.Event,
        autoplay: bool = False,
    ) -> None:
        self._state = GameState(autoplay=autoplay)
        self._progress = progress
        self._progress_lock = progress_lock
        self._input_queue = input_queue
        self._shutdown = shutdown

    def start(self) -> threading.Thread:
        """Spawn and return the daemon thread."""
        t = threading.Thread(target=self.run, name="playgress-game", daemon=True)
        t.start()
        return t

    def run(self) -> None:
        """Main loop — call from a daemon Thread."""
        # TODO(Phase 3): implement physics + obstacle integration
        # TODO(Phase 4): integrate Renderer
        while not self._shutdown.is_set():
            frame_start = time.monotonic()
            self._process_input()
            self._update()
            self._render()
            sleep_for = FRAME_DURATION - (time.monotonic() - frame_start)
            if sleep_for > 0.0:
                time.sleep(sleep_for)

    def _process_input(self) -> None:
        """Drain *input_queue* and apply events to game state."""
        # TODO(Phase 3): implement
        try:
            while True:
                _event = self._input_queue.get_nowait()
        except queue.Empty:
            pass

    def _update(self) -> None:
        """Advance physics, obstacles, score, and speed by one frame."""
        # TODO(Phase 3): implement
        self._state.frame += 1

    def _render(self) -> None:
        """Hand the current state to the Renderer."""
        # TODO(Phase 4): implement
        pass
