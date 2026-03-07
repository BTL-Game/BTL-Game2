from __future__ import annotations

import random

import pygame

from game.config import (
    FOOD_BASE_SCORE,
    FOOD_INITIAL_COUNT,
    FOOD_MAX_ON_MAP,
    FOOD_SCORE_INCREMENT,
    FOOD_SPAWN_INTERVAL,
)
from game.entities.food import Food
from game.entities.tank import Tank


class FoodManager:
    """Spawns food items on open tiles. Score values escalate per wave."""

    def __init__(self) -> None:
        self.items: list[Food] = []
        self._timer: float = FOOD_SPAWN_INTERVAL
        self._open_tiles: list[pygame.Vector2] = []
        self._wave: int = 1
        self._spawn_count_per_wave: int = FOOD_INITIAL_COUNT

    def set_open_tiles(self, tiles: list[pygame.Vector2]) -> None:
        self._open_tiles = tiles

    def reset(self) -> None:
        self.items.clear()
        self._timer = FOOD_SPAWN_INTERVAL
        self._wave = 1
        self._spawn_count_per_wave = FOOD_INITIAL_COUNT

    def spawn_initial(self) -> None:
        """Spawn the first batch of food at the start of the match."""
        self._spawn_batch(self._spawn_count_per_wave)

    def update(self, dt: float, tanks: dict[int, Tank]) -> list[tuple[int, int]]:
        """Tick timer, spawn food, check pickups. Returns [(player_id, score)] collected."""
        pickups: list[tuple[int, int]] = []

        # Periodic respawn with escalation
        self._timer -= dt
        if self._timer <= 0:
            self._timer = FOOD_SPAWN_INTERVAL
            if len(self.items) < FOOD_MAX_ON_MAP:
                self._wave += 1
                # Spawn more food each wave (caps at FOOD_MAX_ON_MAP)
                extra = min(2, self._wave // 3)  # +1 every 3 waves
                count = min(
                    self._spawn_count_per_wave + extra,
                    FOOD_MAX_ON_MAP - len(self.items),
                )
                self._spawn_batch(count)

        # Pickup detection
        remaining: list[Food] = []
        for food in self.items:
            picked = False
            food_rect = food.get_rect()
            for pid, tank in tanks.items():
                if tank.get_rect().colliderect(food_rect):
                    pickups.append((pid, food.score_value))
                    picked = True
                    break
            if not picked:
                remaining.append(food)
        self.items = remaining

        return pickups

    # Internal

    def _spawn_batch(self, count: int) -> None:
        if not self._open_tiles:
            return
        score = FOOD_BASE_SCORE + (self._wave - 1) * FOOD_SCORE_INCREMENT
        available = list(self._open_tiles)
        random.shuffle(available)
        for pos in available[:count]:
            self.items.append(Food(position=pos.copy(), score_value=score, wave=self._wave))
