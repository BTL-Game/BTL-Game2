from __future__ import annotations

from typing import Tuple

import pygame


def reflect_velocity(velocity: pygame.Vector2, normal: pygame.Vector2) -> pygame.Vector2:
    # v' = v - 2*(v.n)*n
    return velocity - 2 * velocity.dot(normal) * normal


def aabb_overlap(a: pygame.Rect, b: pygame.Rect) -> bool:
    return a.colliderect(b)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))
