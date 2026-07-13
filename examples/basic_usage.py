"""Basic usage examples for playgress."""

from __future__ import annotations

import time

from playgress import Progress, track
from playgress.config import Theme


# ── Example 1: drop-in for tqdm ────────────────────────────────────────────────
def example_track() -> None:
    files = [f"file_{i}.txt" for i in range(50)]
    for _f in track(files, description="Processing files"):
        time.sleep(0.05)  # simulate work


# ── Example 2: manual progress updates ────────────────────────────────────────
def example_progress_context() -> None:
    tasks = list(range(30))
    with Progress(total=len(tasks), description="Uploading", theme=Theme.EMOJI) as p:
        for _t in tasks:
            time.sleep(0.05)
            p.update(1)


# ── Example 3: autoplay enabled ───────────────────────────────────────────────
def example_autoplay() -> None:
    data = list(range(100))
    for _d in track(data, description="Training model", autoplay=True):
        time.sleep(0.02)


if __name__ == "__main__":
    print("Running example 1: track()")
    example_progress_context()
    print("\nDone! Try example_progress_context() or example_autoplay() next.")
