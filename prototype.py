#!/usr/bin/env python3
from __future__ import annotations

import os, random, sys, threading, time
from dataclasses import dataclass, field

RST   = "\x1b[0m"
GREEN = "\x1b[32m"
RED   = "\x1b[31m"
YEL   = "\x1b[33m"
MAG   = "\x1b[35m"
GRAY  = "\x1b[90m"
BOLD  = "\x1b[1m"
HIDE  = "\x1b[?25l"
SHOW  = "\x1b[?25h"
CLEAR = "\x1b[2J\x1b[H"

def at(r: int, c: int = 1) -> str: return f"\x1b[{r};{c}H"
def eol() -> str:                   return "\x1b[K"

try:
    W, _ = os.get_terminal_size()
except OSError:
    W = 80
W = min(W, 120)

GAME_H  = 13
GROUND  = GAME_H - 1

T_SCORE = 1
T_GAME  = 2
T_GNDLN = T_GAME + GAME_H
T_GNDEC = T_GNDLN + 1
T_BAR   = T_GNDEC + 1
T_DESC  = T_BAR + 1
TOTAL   = T_DESC

DINO_X = 4

FPS      = 60
_JH      = 5
_JD      = FPS // 4
GRAV     = 2.0 * _JH / (_JD * _JD)
JUMP_V   = -(2.0 * _JH / _JD)
FAST_V   = abs(JUMP_V) * 0.8
HANG_DUR = 2
DUCK_DUR = FPS // 2 + 1
ANIM_PER = FPS // 12

_SF    = 24.0 / FPS
SPD0   = 1.4 * _SF
SPDMAX = 3.5 * _SF

STAGES: list[tuple[int, float]] = [
    (0,    1.4 * _SF),
    (100,  1.8 * _SF),
    (300,  2.2 * _SF),
    (500,  2.8 * _SF),
    (1000, 3.0 * _SF),
    (1500, 3.0 * _SF),
    (2000, 3.0 * _SF),
    (2500, 3.2 * _SF),
    (3000, 3.3 * _SF),
    (6000, 3.5 * _SF),
]

DINO_RUN = [
    [
        "       ++++ ",
        "++    ++Q+++",
        " + +++++_ww ",
        "  ++++++    ",
        "   |   |    ",
    ],
    [
        "       ++++ ",
        " +    ++Q+++",
        " + +++++_ww ",
        "  ++++++    ",
        "   /   /    ",
    ],
]
DINO_DUCK = [
    [
        "       ++++ ",
        " -    ++@+++",
        "  ++++++__w ",
        "   :   :    ",
    ],
    [
        "       ++++ ",
        " +    ++@+++",
        "  ++++++__w ",
        "   ;   ;    ",
    ],
]
DINO_DEAD = [
    "       ++++ ",
    "++    ++X+++",
    " + +++++_ww ",
    "  ++++++    ",
    "   |   |    ",
]
DINO_W    = 12
DINO_H    = 5
DINO_H_DK = 4

CACT_SINGLE = [[" | ", "/|\\", " | "]]
CACT_SHORT  = [["/:\\/:\\", " | |"]]
CACT_GROUP  = [["    |  ", "/|\\/|\\", " |  |"]]

BIRD_S = [
    [" |   ", "<o=- ", " |   "],
    [" /   ", "<O=- ", " \\   "],
]
BIRD_B = [
    ["  /\\    ", " /  \\   ", "<ooo=-- ", " \\__/   "],
    ["  /\\    ", " /  \\   ", "<OOO=-- ", " \\__/   "],
]

CLOUD_SPRITES = [
    ["   .--.    ", " .(    ).  ", "(___.__)   "],
    ["  .-.      ", " (   ).    ", "(___(__)   "],
    ["    .--.   ", ".-(    )-. ", "(________) "],
]
CLOUD_W = 11
CLOUD_H = 3

CACT_SINGLE_TOP = GROUND - 3 + 1
CACT_SHORT_TOP  = GROUND - 2 + 1
CACT_GROUP_TOP  = GROUND - 3 + 1

BIRD_ROW_LOW  = GROUND - 2
BIRD_ROW_HIGH = GROUND - 6
BIG_BIRD_ROW  = GROUND - 7

random.seed(42)
_GND  = ''.join(random.choice('_' * 8 + '=~-^') for _ in range(W * 6))
_DECO = ''.join(random.choice(' ' * 6 + ".,',`-") for _ in range(W * 6))
random.seed()

@dataclass
class Obs:
    x:        float
    top_row:  int
    frames:   list[list[str]]
    width:    int
    color:    str = RED
    anim:     int = 0
    anim_cnt: int = 0

@dataclass
class Cloud:
    x:     float
    row:   int
    kind:  int
    speed: float

@dataclass
class G:
    dy:       float = float(GROUND)
    dvy:      float = 0.0
    grnd:     bool  = True
    ducking:  bool  = False
    duck_fr:  int   = 0
    fastdrop: bool  = False
    hang:     int   = 0
    dead:     bool  = False
    anim:     int   = 0
    anim_cnt: int   = 0
    fr:       int   = 0
    score:    float = 0.0
    hi:       float = 0.0
    spd:      float = SPD0
    scroll:   float = 0.0
    obs:      list  = field(default_factory=list)
    clouds:   list  = field(default_factory=list)
    prog:     float = 0.0
    desc:     str   = "Processing..."
    done:     bool  = False

_g    = G()
_lock = threading.Lock()
_jump = threading.Event()
_duck = threading.Event()
_rst  = threading.Event()
_quit = threading.Event()

def _posix_input() -> None:
    import os as _os, select, termios, tty
    fd  = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while not _quit.is_set():
            r, _, _ = select.select([fd], [], [], 0.04)
            if not r:
                continue
            ch = _os.read(fd, 1)
            if   ch == b' ':                   _jump.set()
            elif ch == b'\x1b':
                r2, _, _ = select.select([fd], [], [], 0.02)
                if r2:
                    seq = _os.read(fd, 2)
                    if   seq == b'[A': _jump.set()
                    elif seq == b'[B': _duck.set()
            elif ch in (b'r', b'R'):           _rst.set()
            elif ch in (b'q', b'Q', b'\x03'): _quit.set()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def _win_input() -> None:
    import msvcrt
    while not _quit.is_set():
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            if   ch == b' ':                    _jump.set()
            elif ch in (b'r', b'R'):            _rst.set()
            elif ch in (b'q', b'Q', b'\x03'):  _quit.set()
            elif ch == b'\xe0' and msvcrt.kbhit():
                c2 = msvcrt.getch()
                if   c2 == b'H': _jump.set()
                elif c2 == b'P': _duck.set()
        time.sleep(0.008)

def start_input() -> None:
    fn = _win_input if sys.platform == 'win32' else _posix_input
    threading.Thread(target=fn, daemon=True, name='inp').start()

def _target_spd(score: float) -> float:
    spd = SPD0
    for thr, s in STAGES:
        if score >= thr:
            spd = s
    return spd

def _new_cloud(x: float) -> Cloud:
    return Cloud(
        x=x,
        row=random.randint(1, 3),
        kind=random.randrange(len(CLOUD_SPRITES)),
        speed=random.uniform(0.2, 0.5) * _SF,
    )

def _init_clouds() -> list[Cloud]:
    step = W // 3
    return [_new_cloud(float(step * i + random.randint(0, step // 2))) for i in range(3)]

def _spawn(g: G) -> None:
    rightmost = max((o.x + o.width for o in g.obs), default=-1.0)
    min_gap   = max(30, int(48 - g.spd * 8))
    max_gap   = max(45, int(65 - g.spd * 8))
    if rightmost >= W - random.randint(min_gap, max_gap):
        return

    birds_ok = g.score >= 300
    r = random.random()

    if not birds_ok or r < 0.75:
        t = random.random()
        if   t < 0.50: g.obs.append(Obs(float(W), CACT_SINGLE_TOP, CACT_SINGLE, 3))
        elif t < 0.75: g.obs.append(Obs(float(W), CACT_SHORT_TOP,  CACT_SHORT,  6))
        else:           g.obs.append(Obs(float(W), CACT_GROUP_TOP,  CACT_GROUP,  7))
    else:
        t = random.random()
        if   t < 0.15: g.obs.append(Obs(float(W), BIG_BIRD_ROW,   BIRD_B, 8, MAG))
        elif t < 0.55: g.obs.append(Obs(float(W), BIRD_ROW_LOW,   BIRD_S, 5, YEL))
        else:           g.obs.append(Obs(float(W), BIRD_ROW_HIGH,  BIRD_S, 5, YEL))

def _dino_h(g: G) -> int:
    return DINO_H_DK if g.ducking else DINO_H

def _collide(g: G) -> bool:
    dbot  = int(round(g.dy))
    dtop  = dbot - _dino_h(g) + 1
    dhx1  = DINO_X + 2
    dhx2  = DINO_X + DINO_W - 2
    for obs in g.obs:
        spr  = obs.frames[obs.anim % len(obs.frames)]
        obot = obs.top_row + len(spr) - 1
        ohx1 = int(obs.x) + 1
        ohx2 = int(obs.x) + obs.width - 2
        if dhx1 <= ohx2 and dhx2 >= ohx1 and dtop <= obot and dbot >= obs.top_row:
            return True
    return False

def _reset(g: G) -> None:
    if g.score > g.hi: g.hi = g.score
    g.dy = float(GROUND); g.dvy = 0.0; g.grnd = True
    g.ducking = False; g.duck_fr = 0; g.fastdrop = False; g.hang = 0
    g.dead = False; g.anim = 0; g.anim_cnt = 0; g.fr = 0
    g.score = 0.0; g.spd = SPD0; g.obs.clear()
    g.clouds = _init_clouds()

def _game_row(g: G, gr: int) -> str:
    chars  = [' '] * W
    colors = ['']  * W

    for cl in g.clouds:
        if cl.row <= gr <= cl.row + CLOUD_H - 1:
            spr = CLOUD_SPRITES[cl.kind]
            ri  = gr - cl.row
            for ci, ch in enumerate(spr[ri]):
                pos = int(cl.x) + ci
                if ch != ' ' and 0 <= pos < W:
                    chars[pos] = ch; colors[pos] = GRAY

    dbot = int(round(g.dy))
    dh   = _dino_h(g)
    dtop = dbot - dh + 1
    if dtop <= gr <= dbot:
        ri = gr - dtop
        if   g.dead:    row_s = DINO_DEAD[ri]
        elif g.ducking: row_s = DINO_DUCK[g.anim % 2][ri]
        else:           row_s = DINO_RUN[g.anim % 2][ri]
        for ci, ch in enumerate(row_s):
            pos = DINO_X + ci
            if ch != ' ' and 0 <= pos < W:
                chars[pos] = ch; colors[pos] = GREEN

    for obs in g.obs:
        spr = obs.frames[obs.anim % len(obs.frames)]
        ob  = obs.top_row
        if ob <= gr <= ob + len(spr) - 1:
            ri = gr - ob
            for ci, ch in enumerate(spr[ri]):
                pos = int(obs.x) + ci
                if ch != ' ' and 0 <= pos < W:
                    chars[pos] = ch; colors[pos] = obs.color

    out, cur = [], ''
    for ch, clr in zip(chars, colors):
        if clr != cur:
            out.append(clr if clr else RST); cur = clr
        out.append(ch)
    if cur: out.append(RST)
    return ''.join(out)

def _render(g: G) -> None:
    p: list[str] = []

    sc     = f"Score: {BOLD}{int(g.score):05d}{RST}"
    hi     = f"HI: {int(g.hi):05d}"
    sc_raw = f"Score: {int(g.score):05d}"
    pad    = max(W - len(sc_raw) - len(hi), 2)
    p.append(at(T_SCORE) + sc + ' ' * pad + hi + eol())

    for gr in range(GAME_H):
        p.append(at(T_GAME + gr) + _game_row(g, gr) + eol())

    off  = int(g.scroll) % (W * 6)
    gnd  = (_GND  * 2)[off: off + W]
    deco = (_DECO * 2)[off: off + W]
    p.append(at(T_GNDLN) + RST + gnd + eol())

    p.append(at(T_GNDEC) + GRAY + deco + RST + eol())

    bw  = W - 9
    fil = round(g.prog * bw)
    p.append(at(T_BAR) + GREEN + '█' * fil + GRAY + '░' * (bw - fil)
             + RST + f' {g.prog * 100:5.1f}%' + eol())

    if g.dead:
        msg = '  GAME OVER  ·  R: restart  ·  Q: quit'
    elif g.done:
        msg = f'  ✓ Done!  Score: {int(g.score)}   ·  R: replay  ·  Q: quit'
    else:
        msg = f'  {g.desc}'
    p.append(at(T_DESC) + msg[:W] + eol())

    p.append(at(TOTAL + 1))
    sys.stdout.write(''.join(p))
    sys.stdout.flush()

def game_loop() -> None:
    last = time.monotonic()
    while not _quit.is_set():
        t0 = time.monotonic()
        last = t0

        with _lock:
            g = _g

            if _rst.is_set():
                _rst.clear()
                if g.dead or g.done:
                    _reset(g)

            if not g.dead:

                if _jump.is_set():
                    _jump.clear()
                    if g.grnd:
                        g.dvy = JUMP_V; g.grnd = False; g.hang = 0
                        g.ducking = False; g.duck_fr = 0; g.fastdrop = False

                if _duck.is_set():
                    _duck.clear()
                    if g.grnd:
                        g.ducking = True; g.duck_fr = DUCK_DUR
                    else:
                        g.fastdrop = True; g.hang = 0

                if g.duck_fr > 0:
                    g.duck_fr -= 1
                    if g.duck_fr == 0:
                        g.ducking = False

                if not g.grnd:
                    if g.fastdrop:
                        g.dvy = FAST_V
                    elif g.hang > 0:
                        g.hang -= 1
                    else:
                        nv = g.dvy + GRAV
                        if g.dvy < 0 <= nv:
                            g.hang = HANG_DUR; g.dvy = 0.0
                        else:
                            g.dvy = nv
                    g.dy += g.dvy
                    if g.dy >= float(GROUND):
                        g.dy = float(GROUND); g.dvy = 0.0; g.grnd = True
                        if g.fastdrop:
                            g.ducking = True; g.duck_fr = DUCK_DUR // 2
                        g.fastdrop = False

                for obs in g.obs:
                    obs.x -= g.spd
                    obs.anim_cnt += 1
                    if obs.anim_cnt >= ANIM_PER:
                        obs.anim_cnt = 0
                        obs.anim = (obs.anim + 1) % len(obs.frames)
                g.obs = [o for o in g.obs if o.x + o.width > 0]
                _spawn(g)

                for cl in g.clouds:
                    cl.x -= cl.speed
                for i, cl in enumerate(g.clouds):
                    if cl.x + CLOUD_W < 0:
                        g.clouds[i] = _new_cloud(float(W + random.randint(10, 40)))

                if _collide(g):
                    g.dead = True
                else:
                    g.score    += 0.5
                    g.spd       = min(_target_spd(g.score), SPDMAX)
                    g.scroll   += g.spd
                    g.anim_cnt += 1
                    if g.anim_cnt >= ANIM_PER:
                        g.anim_cnt = 0; g.anim += 1
                    g.fr += 1

            _render(g)

        sleep = 1.0 / FPS - (time.monotonic() - t0)
        if sleep > 0:
            time.sleep(sleep)

def main() -> None:
    sys.stdout.write(HIDE + CLEAR)
    sys.stdout.flush()

    with _lock:
        _g.clouds = _init_clouds()

    start_input()
    threading.Thread(target=game_loop, daemon=True, name='game').start()

    total = 80
    for i in range(total):
        if _quit.is_set():
            break
        time.sleep(0.15)
        with _lock:
            _g.prog = (i + 1) / total
            _g.desc = f'Processing item {i + 1}/{total}...'

    with _lock:
        _g.prog = 1.0
        _g.done = True

    _quit.wait()
    sys.stdout.write(SHOW + at(TOTAL + 2))
    sys.stdout.flush()
    print('\nGoodbye!')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(SHOW)
        sys.stdout.flush()
        print()
