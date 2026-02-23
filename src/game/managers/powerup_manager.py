from __future__ import annotations

import random

import pygame

from game.config import (
    POWERUP_MAX_ON_MAP,
    POWERUP_SPAWN_INTERVAL,
    SHIELD_DURATION,
    SPEED_BOOST_DURATION,
    TRIPLE_SHOT_DURATION,
)
from game.entities.powerup import PowerUp, PowerUpType
from game.entities.tank import Tank


_DURATIONS: dict[PowerUpType, float] = {
    PowerUpType.SPEED: SPEED_BOOST_DURATION,
    PowerUpType.SHIELD: SHIELD_DURATION,
    PowerUpType.TRIPLE: TRIPLE_SHOT_DURATION,
}


class PowerUpManager:
    """Handles spawning, rendering, and collection of map power-ups."""

    def __init__(self) -> None:
        self.items: list[PowerUp] = []
        self._timer: float = POWERUP_SPAWN_INTERVAL
        self._open_tiles: list[pygame.Vector2] = []

    def set_open_tiles(self, tiles: list[pygame.Vector2]) -> None:
        self._open_tiles = tiles

    def reset(self) -> None:
        self.items.clear()
        self._timer = POWERUP_SPAWN_INTERVAL

    def update(self, dt: float, tanks: dict[int, Tank]) -> list[tuple[int, PowerUpType]]:
        """Tick timer, spawn, check pickups. Returns list of (player_id, type) pickups."""
        pickups: list[tuple[int, PowerUpType]] = []

        # Spawn logic
        self._timer -= dt
        if self._timer <= 0 and len(self.items) < POWERUP_MAX_ON_MAP and self._open_tiles:
            self._timer = POWERUP_SPAWN_INTERVAL
            ptype = random.choice(list(PowerUpType))
            pos = random.choice(self._open_tiles).copy()
            self.items.append(PowerUp(position=pos, powerup_type=ptype))
        elif self._timer <= 0:
            self._timer = POWERUP_SPAWN_INTERVAL

        # Pickup detection
        remaining: list[PowerUp] = []
        for item in self.items:
            picked = False
            item_rect = item.get_rect()
            for pid, tank in tanks.items():
                if tank.get_rect().colliderect(item_rect):
                    duration = _DURATIONS[item.powerup_type]
                    tank.apply_powerup(item.powerup_type, duration)
                    pickups.append((pid, item.powerup_type))
                    picked = True
                    break
            if not picked:
                remaining.append(item)
        self.items = remaining

        # Update tank powerup timers
        for tank in tanks.values():
            tank.update_powerups(dt)

        return pickups
