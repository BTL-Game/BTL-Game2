from dataclasses import dataclass

import pygame


@dataclass
class Wall:
    rect: pygame.Rect
