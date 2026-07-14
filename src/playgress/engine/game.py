from __future__ import annotations

import queue
import random
import threading
import time

from playgress.config import (
    CLOUD_H,
    CLOUD_SPEED_SCALE,
    CLOUD_SPRITES,
    CLOUD_W,
    FRAME_DURATION,
    INITIAL_SPEED,
    MAX_SPEED,
    SCORE_PER_FRAME,
    SPEED_STAGES,
)
from playgress.engine.obstacles import advance_obstacles, should_spawn, spawn_obstacle
from playgress.engine.physics import advance_anim, apply_physics, check_collision, start_duck, try_jump
from playgress.models import CloudData, DinoState, GameState, InputEvent, ProgressState
from playgress.terminal.render import Renderer


class GameLoop:

    def __init__(
        self,
        progress: ProgressState,
        progress_lock: threading.Lock,
        input_queue: queue.Queue[InputEvent],
        shutdown: threading.Event,
        renderer: Renderer,
        cols: int,
    ) -> None:
        self._progress = progress
        self._progress_lock = progress_lock
        self._input_queue = input_queue
        self._shutdown = shutdown
        self._renderer = renderer
        self._cols = cols
        self._state = GameState(clouds=self._init_clouds())

    def start(self) -> threading.Thread:
        t = threading.Thread(target=self.run, name="playgress-game", daemon=True)
        t.start()
        return t

    def run(self) -> None:
        while not self._shutdown.is_set():
            t0 = time.monotonic()
            self._tick()
            sleep_for = FRAME_DURATION - (time.monotonic() - t0)
            if sleep_for > 0.0:
                time.sleep(sleep_for)

    def _tick(self) -> None:
        g = self._state

        with self._progress_lock:
            if self._progress.is_complete and not g.is_done:
                g.is_done = True

        self._process_input(g)

        if not g.is_dead:
            self._update(g)

        with self._progress_lock:
            fraction = self._progress.fraction
            description = self._progress.description
            eta = self._progress.eta

        self._renderer.render(g, fraction, description, eta)

    def _process_input(self, g: GameState) -> None:
        events: list[InputEvent] = []
        try:
            while True:
                events.append(self._input_queue.get_nowait())
        except queue.Empty:
            pass

        for event in events:
            if event is InputEvent.QUIT:
                self._shutdown.set()
            elif event is InputEvent.RESTART:
                if g.is_dead or g.is_done:
                    self._reset(g)
            elif event is InputEvent.JUMP:
                if not g.is_dead:
                    try_jump(g.dino)
            elif event is InputEvent.DUCK_START:
                if not g.is_dead:
                    start_duck(g.dino)

    def _update(self, g: GameState) -> None:
        apply_physics(g.dino)
        g.obstacles = advance_obstacles(g.obstacles, g.speed)
        self._advance_clouds(g)

        if should_spawn(g.obstacles, g.speed, self._cols):
            g.obstacles.append(spawn_obstacle(g.score, g.speed, self._cols))

        if check_collision(g.dino, g.obstacles):
            g.dino.dead = True
            g.is_dead = True
        else:
            g.score += SCORE_PER_FRAME
            g.speed = min(_target_speed(g.score), MAX_SPEED)
            g.scroll += g.speed
            advance_anim(g.dino)

        g.frame += 1

    def _reset(self, g: GameState) -> None:
        if g.score > g.hi_score:
            g.hi_score = g.score
        g.dino = DinoState()
        g.obstacles = []
        g.clouds = self._init_clouds()
        g.score = 0.0
        g.speed = INITIAL_SPEED
        g.scroll = 0.0
        g.frame = 0
        g.is_dead = False

    def _advance_clouds(self, g: GameState) -> None:
        for cl in g.clouds:
            cl.x -= cl.speed
        for i, cl in enumerate(g.clouds):
            if cl.x + CLOUD_W < 0:
                g.clouds[i] = self._new_cloud(
                    float(self._cols + random.randint(10, 40))
                )

    def _init_clouds(self) -> list[CloudData]:
        step = max(1, self._cols // 3)
        return [
            self._new_cloud(float(step * i + random.randint(0, max(1, step // 2))))
            for i in range(3)
        ]

    @staticmethod
    def _new_cloud(x: float) -> CloudData:
        return CloudData(
            x=x,
            row=random.randint(1, 3),
            kind=random.randrange(len(CLOUD_SPRITES)),
            speed=random.uniform(0.2, 0.5) * CLOUD_SPEED_SCALE,
        )


def _target_speed(score: float) -> float:
    speed = INITIAL_SPEED
    for threshold, s in SPEED_STAGES:
        if score >= threshold:
            speed = s
    return speed
