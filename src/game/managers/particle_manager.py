from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from game.config import (
    PARTICLE_COUNT,
    PARTICLE_LIFETIME,
    PARTICLE_SIZE,
    PARTICLE_SPEED_MAX,
    PARTICLE_SPEED_MIN,
)


@dataclass
class Particle:
    position: pygame.Vector2
    velocity: pygame.Vector2
    color: tuple[int, int, int]
    lifetime: float
    max_lifetime: float


class ParticleManager:
    """Lightweight pixel-particle explosions."""

    def __init__(self) -> None:
        self.particles: list[Particle] = []

    def reset(self) -> None:
        self.particles.clear()

    def spawn_explosion(
        self,
        center: pygame.Vector2,
        base_color: tuple[int, int, int],
    ) -> None:
        for _ in range(PARTICLE_COUNT):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(PARTICLE_SPEED_MIN, PARTICLE_SPEED_MAX)
            vel = pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed)

            # Slight color variation
            r = min(255, max(0, base_color[0] + random.randint(-30, 30)))
            g = min(255, max(0, base_color[1] + random.randint(-30, 30)))
            b = min(255, max(0, base_color[2] + random.randint(-30, 30)))

            self.particles.append(
                Particle(
                    position=center.copy(),
                    velocity=vel,
                    color=(r, g, b),
                    lifetime=PARTICLE_LIFETIME,
                    max_lifetime=PARTICLE_LIFETIME,
                )
            )

    def update(self, dt: float) -> None:
        alive: list[Particle] = []
        for p in self.particles:
            p.lifetime -= dt
            if p.lifetime > 0:
                p.position += p.velocity * dt
                # Apply gravity
                p.velocity.y += 120.0 * dt
                alive.append(p)
        self.particles = alive

    def render(self, screen: pygame.Surface) -> None:
        for p in self.particles:
            alpha = max(0.0, p.lifetime / p.max_lifetime)
            size = max(1, int(PARTICLE_SIZE * alpha))
            color = (
                int(p.color[0] * alpha),
                int(p.color[1] * alpha),
                int(p.color[2] * alpha),
            )
            pygame.draw.rect(
                screen, color,
                (int(p.position.x), int(p.position.y), size, size),
            )
