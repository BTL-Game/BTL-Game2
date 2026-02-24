from __future__ import annotations

from dataclasses import dataclass, field

import pygame

from game.config import (
    PLAYER_HEALTH,
    SPEED_BOOST_MULTIPLIER,
    TANK_SIZE,
    TANK_SPEED,
    TANK_TURN_SPEED,
    TURRET_TURN_SPEED,
)
from game.entities.powerup import PowerUpType


@dataclass
class Tank:
    position: pygame.Vector2
    rotation_deg: float
    turret_rotation_deg: float
    health: int = PLAYER_HEALTH
    active_powerups: dict[PowerUpType, float] = field(default_factory=dict)

    # -- Properties for easy checks ------------------------------------------

    @property
    def has_speed_boost(self) -> bool:
        return PowerUpType.SPEED in self.active_powerups

    @property
    def has_shield(self) -> bool:
        return PowerUpType.SHIELD in self.active_powerups

    @property
    def has_triple_shot(self) -> bool:
        return PowerUpType.TRIPLE in self.active_powerups

    # -- Power-up management --------------------------------------------------

    def apply_powerup(self, ptype: PowerUpType, duration: float) -> None:
        self.active_powerups[ptype] = duration

    def update_powerups(self, dt: float) -> None:
        expired = [k for k, v in self.active_powerups.items() if v - dt <= 0]
        for k in expired:
            del self.active_powerups[k]
        for k in self.active_powerups:
            self.active_powerups[k] -= dt

    def take_damage(self, amount: int = 1) -> bool:
        """Apply damage, respecting shield.

        Returns True if this damage reduced health to 0 or below (tank died),
        otherwise False.
        """
        if self.has_shield:
            # Shield absorbs the hit and is consumed
            del self.active_powerups[PowerUpType.SHIELD]
            return False
        self.health -= amount
        return self.health <= 0

    # -- Movement -------------------------------------------------------------

    def update(self, dt: float, forward: float, turn: float, turret_turn: float = 0.0) -> None:
        self.rotation_deg += turn * TANK_TURN_SPEED * dt
        direction = pygame.Vector2(1, 0).rotate(self.rotation_deg)

        speed = TANK_SPEED
        if self.has_speed_boost:
            speed *= SPEED_BOOST_MULTIPLIER

        self.position += direction * (forward * speed * dt)

        # Independent turret rotation – turret keeps its position when no input
        if turret_turn != 0.0:
            self.turret_rotation_deg += turret_turn * TURRET_TURN_SPEED * dt

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.position.x - TANK_SIZE / 2),
            int(self.position.y - TANK_SIZE / 2),
            TANK_SIZE,
            TANK_SIZE,
        )
