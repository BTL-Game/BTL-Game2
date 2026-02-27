from __future__ import annotations

import pygame

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH, TANK_SIZE
from game.entities.wall import Wall
from game.physics import clamp


class CollisionManager:
    """Handles tank-wall, tank-boundary, and tank-tank collisions."""

    @staticmethod
    def resolve_tank_walls(
        tank_position: pygame.Vector2,
        previous_position: pygame.Vector2,
        walls: list[Wall],
        other_tank_rect: pygame.Rect | None = None,
    ) -> pygame.Vector2:
        """Move tank on X and Y independently to prevent corner sticking.

        Instead of reverting the entire position on any collision,
        we first try the X move, then the Y move separately.
        This lets the tank slide along walls.

        If *other_tank_rect* is provided the opposing tank is treated as an
        additional solid obstacle (tank-to-tank collision).
        """
        half = TANK_SIZE / 2

        def _blocked(rect: pygame.Rect) -> bool:
            """Return True when *rect* overlaps any active wall or the other tank."""
            if any(wall.rect.colliderect(rect) for wall in walls if not wall.is_destroyed):
                return True
            if other_tank_rect is not None and other_tank_rect.colliderect(rect):
                return True
            return False

        # Try X-axis movement first
        test_x = pygame.Vector2(tank_position.x, previous_position.y)
        test_x.x = clamp(test_x.x, half, SCREEN_WIDTH - half)
        if _blocked(_tank_rect(test_x)):
            test_x.x = previous_position.x

        # Try Y-axis movement
        test_y = pygame.Vector2(test_x.x, tank_position.y)
        test_y.y = clamp(test_y.y, half, SCREEN_HEIGHT - half)
        if _blocked(_tank_rect(test_y)):
            test_y.y = previous_position.y

        return test_y


def _tank_rect(pos: pygame.Vector2) -> pygame.Rect:
    return pygame.Rect(
        int(pos.x - TANK_SIZE / 2),
        int(pos.y - TANK_SIZE / 2),
        TANK_SIZE,
        TANK_SIZE,
    )
