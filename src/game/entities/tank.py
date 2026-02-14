from __future__ import annotations

from dataclasses import dataclass

import pygame

from game.config import PLAYER_HEALTH, TANK_SIZE, TANK_SPEED, TANK_TURN_SPEED


@dataclass
class Tank:
    position: pygame.Vector2
    rotation_deg: float
    turret_rotation_deg: float
    health: int = PLAYER_HEALTH

    def update(self, dt: float, forward: float, turn: float) -> None:
        # Movement based on rotation angle
        self.rotation_deg += turn * TANK_TURN_SPEED * dt
        direction = pygame.Vector2(1, 0).rotate(self.rotation_deg)
        self.position += direction * (forward * TANK_SPEED * dt)

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.position.x - TANK_SIZE / 2),
            int(self.position.y - TANK_SIZE / 2),
            TANK_SIZE,
            TANK_SIZE,
        )
