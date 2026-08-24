# tqrex

> A progress bar that lets you play the Chrome T-Rex game in your terminal.

<img src="https://github.com/Samoilov2004/tqrex/blob/main/demo.gif" width="100%">

Your long-running script doesn't have to be boring. **tqrex** wraps any
iterable in a full T-Rex side-scroller — jump cacti, dodge birds, rack up a
high score — while your real work happens in the background. When the task
finishes the game keeps running until you decide to quit.

---

## Features

- **Zero runtime dependencies** — pure Python standard library
- **Familiar iterable API** — wrap any iterable with `track()`
- **`Progress` context manager** — for manual update control
- **60 FPS physics** — faithful gravity, jump arc, and speed curve from the
  original Chrome dino
- **Double-buffered renderer** — flicker-free diff-based redraw, single write
  per frame
- **Cross-platform** — macOS, Linux, Windows (ANSI terminal required)
- **Python 3.11+**

---

## Installation

```bash
pip install tqrex
```

Or for local development:

```bash
git clone https://github.com/Samoilov2004/tqrex.git
cd tqrex
pip install -e ".[dev]"
```

---

## Quickstart

### Wrap an iterable

```python
import time

from tqrex import track

for item in track(range(100), description="Processing"):
    time.sleep(0.05)
```

### Any iterable works

```python
files = ["data_001.csv", "data_002.csv", ...]

for f in track(files, description="Crunching files"):
    crunch(f)
```

### Manual control with the `Progress` context manager

```python
from tqrex import Progress

steps = ["Download", "Extract", "Build", "Install"]
with Progress(total=len(steps), description="Installing") as p:
    for step in steps:
        p.set_description(f"Step: {step}")
        run(step)
        p.update(1)
```

## Keyboard controls

| Key | Action |
|-----|--------|
| `Space` / `↑` | Jump |
| `↓` | Duck on ground / fast-drop mid-air |
| `R` | Restart after game-over; replay after task completes |
| `Q` / `Ctrl-C` | Quit — unblocks the script |

> **Note:** The game keeps running after all items are processed so you can
> finish your current run. Press **Q** when you're done.
