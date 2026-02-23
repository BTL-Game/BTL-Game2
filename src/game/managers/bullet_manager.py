from __future__ import annotations

import pygame

from game.config import (
    BULLET_MAX_BOUNCES,
    BULLET_COOLDOWN,
    BULLET_MAX_PER_PLAYER,
    BULLET_RADIUS,
    BULLET_SPEED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TANK_SIZE,
    TRIPLE_SHOT_SPREAD,
)
from game.entities.bullet import Bullet
from game.entities.tank import Tank
from game.entities.wall import Wall
from game.physics import reflect_velocity


class BulletManager:
    """Owns bullet lifecycle: spawn, move, reflect off walls, remove dead."""

    def __init__(self) -> None:
        self.bullets: list[Bullet] = []
        self.fire_timers: dict[int, float] = {1: 0.0, 2: 0.0}

    def reset(self) -> None:
        self.bullets.clear()
        self.fire_timers = {1: 0.0, 2: 0.0}

    def can_fire(self, player_id: int) -> bool:
        if self.fire_timers[player_id] > 0.0:
            return False
        count = sum(1 for b in self.bullets if b.owner_id == player_id)
        return count < BULLET_MAX_PER_PLAYER

    def spawn(self, player_id: int, tank: Tank) -> None:
        direction = pygame.Vector2(1, 0).rotate(tank.turret_rotation_deg)
        offset = TANK_SIZE / 2 + BULLET_RADIUS + 2
        pos = tank.position + direction * offset
        vel = direction * BULLET_SPEED
        self.bullets.append(Bullet(position=pos.copy(), velocity=vel, owner_id=player_id))

        if tank.has_triple_shot:
            for angle_offset in (-TRIPLE_SHOT_SPREAD, TRIPLE_SHOT_SPREAD):
                side_dir = pygame.Vector2(1, 0).rotate(tank.turret_rotation_deg + angle_offset)
                side_pos = tank.position + side_dir * offset
                side_vel = side_dir * BULLET_SPEED
                self.bullets.append(
                    Bullet(position=side_pos.copy(), velocity=side_vel, owner_id=player_id)
                )

        self.fire_timers[player_id] = BULLET_COOLDOWN

    def update(self, dt: float, walls: list[Wall]) -> None:
        self.fire_timers[1] = max(0.0, self.fire_timers[1] - dt)
        self.fire_timers[2] = max(0.0, self.fire_timers[2] - dt)

        screen_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        alive: list[Bullet] = []

        for bullet in self.bullets:
            bullet.update(dt)
            bullet_rect = bullet.get_rect()

            for wall in walls:
                if wall.is_destroyed:
                    continue
                if bullet_rect.colliderect(wall.rect):
                    normal, overlap = self._collision_normal(bullet_rect, wall.rect)
                    bullet.velocity = reflect_velocity(bullet.velocity, normal)
                    bullet.position += normal * (overlap + 0.1)
                    bullet.bounces += 1

                    # Destructible wall hit
                    wall.hit()
                    break

            if (
                screen_rect.collidepoint(bullet.position.x, bullet.position.y)
                and bullet.bounces < BULLET_MAX_BOUNCES
            ):
                alive.append(bullet)

        self.bullets = alive

    def check_hits(self, tanks: dict[int, Tank]) -> int | None:
        """Check bullet-tank collisions. Returns winner_id if a tank was killed, else None."""
        remaining: list[Bullet] = []
        winner: int | None = None

        for bullet in self.bullets:
            hit = False
            for player_id, tank in tanks.items():
                if player_id == bullet.owner_id:
                    continue
                if tank.get_rect().colliderect(bullet.get_rect()):
                    tank.take_damage(1)
                    hit = True
                    if tank.health <= 0 and winner is None:
                        winner = bullet.owner_id
                    break
            if not hit:
                remaining.append(bullet)

        self.bullets = remaining
        return winner

    # -- internal helpers ---------------------------------------------------

    @staticmethod
    def _collision_normal(bullet: pygame.Rect, wall: pygame.Rect) -> tuple[pygame.Vector2, float]:
        overlap_x = min(bullet.right - wall.left, wall.right - bullet.left)
        overlap_y = min(bullet.bottom - wall.top, wall.bottom - bullet.top)

        if overlap_x < overlap_y:
            normal = pygame.Vector2(-1, 0) if bullet.centerx < wall.centerx else pygame.Vector2(1, 0)
            return normal, overlap_x

        normal = pygame.Vector2(0, -1) if bullet.centery < wall.centery else pygame.Vector2(0, 1)
        return normal, overlap_y
