from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import pygame

from game.config import POWERUP_SIZE


class PowerUpType(Enum):
    SPEED = "speed"
    SHIELD = "shield"
    TRIPLE = "triple"


@dataclass
class PowerUp:
    position: pygame.Vector2
    powerup_type: PowerUpType

    def get_rect(self) -> pygame.Rect:
        half = POWERUP_SIZE / 2
        return pygame.Rect(
            int(self.position.x - half),
            int(self.position.y - half),
            POWERUP_SIZE,
            POWERUP_SIZE,
        )
