from __future__ import annotations

from dataclasses import dataclass

import pygame

from game.config import FOOD_SIZE


@dataclass
class Food:
    position: pygame.Vector2
    score_value: int
    wave: int = 1  # which spawn wave this food belongs to (for color variation)

    def get_rect(self) -> pygame.Rect:
        half = FOOD_SIZE / 2
        return pygame.Rect(
            int(self.position.x - half),
            int(self.position.y - half),
            FOOD_SIZE,
            FOOD_SIZE,
        )
