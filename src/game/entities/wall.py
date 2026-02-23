from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import pygame


class WallType(Enum):
    STEEL = "steel"
    BRICK = "brick"


@dataclass
class Wall:
    rect: pygame.Rect
    wall_type: WallType = WallType.STEEL
    health: int = -1  # -1 = indestructible (steel)

    def __post_init__(self) -> None:
        if self.wall_type == WallType.BRICK and self.health < 0:
            from game.config import BRICK_HEALTH
            self.health = BRICK_HEALTH

    @property
    def is_destroyed(self) -> bool:
        return self.wall_type == WallType.BRICK and self.health <= 0

    def hit(self) -> bool:
        """Apply one hit. Returns True if the wall was destroyed by this hit."""
        if self.wall_type == WallType.STEEL:
            return False
        self.health -= 1
        return self.health <= 0
