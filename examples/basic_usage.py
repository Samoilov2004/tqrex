from __future__ import annotations

import sys
import time

from playgress import Progress, track
from playgress.config import Theme


def example_track() -> None:
    """Process 60 items while playing the T-Rex game.

    Keys during the game:
      SPACE / ↑   jump
      ↓           duck / fast-drop mid-air
      R           restart after game-over or after task completes
      Q           quit (unblocks the script)
    """
    files = [f"report_{i:04d}.csv" for i in range(60)]
    for _f in track(files, description="Crunching reports"):
        time.sleep(0.12)  # simulate I/O work

def example_range() -> None:
    """Iterate over range(100) — total is inferred automatically."""
    for _i in track(range(100), description="Training epochs"):
        time.sleep(0.05)

def example_context() -> None:
    """Use Progress when you control the update timing explicitly."""
    steps = ["Download", "Unpack", "Compile", "Link", "Install"]
    with Progress(total=len(steps), description="Building package") as p:
        for step in steps:
            p.set_description(f"Step: {step}")
            time.sleep(0.8)
            p.update(1)

def example_autoplay() -> None:
    """Let the AI controller play while your batch job runs."""
    dataset = list(range(80))
    for _d in track(dataset, description="Embedding vectors", autoplay=True):
        time.sleep(0.08)

_EXAMPLES: dict[str, tuple[str, object]] = {
    "track":    ("Process 60 files (default)", example_track),
    "range":    ("Iterate range(100)",         example_range),
    "context":  ("Manual Progress manager",    example_context),
    "autoplay": ("Autoplay AI controller",     example_autoplay),
}

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "track"
    if mode not in _EXAMPLES:
        print(f"Unknown example '{mode}'. Choose from: {', '.join(_EXAMPLES)}")
        sys.exit(1)
    label, fn = _EXAMPLES[mode]
    print(f"Running: {label}")
    fn()  # type: ignore[operator]
    print("\nAll done. Goodbye!")