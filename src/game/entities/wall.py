from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import pygame


class WallType(Enum):
    STEEL = "steel"
    BRICK = "brick"


class WallState(Enum):
    """Visual state of the wall based on health."""
    UNBROKEN = "unbroken"      # Steel walls or full-health brick
    BREAKABLE = "breakable"    # Full-health brick (2 hits remaining)
    BROKEN = "broken"          # Damaged brick (1 hit remaining)
    DESTROYED = "destroyed"    # No health left


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

    @property
    def visual_state(self) -> WallState:
        """Get the current visual state for rendering."""
        if self.wall_type == WallType.STEEL:
            return WallState.UNBROKEN
        if self.health <= 0:
            return WallState.DESTROYED
        elif self.health == 1:
            return WallState.BROKEN
        else:  # health >= 2
            return WallState.BREAKABLE

    def hit(self) -> bool:
        """Apply one hit. Returns True if the wall was destroyed by this hit."""
        if self.wall_type == WallType.STEEL:
            return False
        self.health -= 1
        return self.health <= 0
