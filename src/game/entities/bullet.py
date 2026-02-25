from __future__ import annotations

from dataclasses import dataclass

import pygame

from game.config import BULLET_RADIUS
@dataclass
class Bullet:
    position: pygame.Vector2
    velocity: pygame.Vector2
    owner_id: int
    bounces: int = 0

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt

    def get_rect(self) -> pygame.Rect:
        size = BULLET_RADIUS * 2
        return pygame.Rect(
            int(self.position.x - BULLET_RADIUS),
            int(self.position.y - BULLET_RADIUS),
            size,
            size,
        )
