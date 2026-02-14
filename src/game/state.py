from dataclasses import dataclass

import pygame

from game.assets import TankSprites, load_sprites
from game.config import (
    BULLET_COLOR,
    BULLET_COOLDOWN,
    BULLET_MAX_PER_PLAYER,
    BULLET_RADIUS,
    BULLET_SPEED,
    BULLET_MAX_BOUNCES,
    PLAYER1_COLOR,
    PLAYER2_COLOR,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SHOOT_FLASH_DURATION,
    TANK_SIZE,
    TILE_SIZE,
    TURRET_LENGTH,
    WALL_INSET,
    WALL_COLOR,
)
from game.entities.bullet import Bullet
from game.entities.tank import Tank
from game.input import PLAYER1, PLAYER2
from game.levels import DEFAULT_LEVEL, build_tiles
from game.physics import clamp, reflect_velocity
from game.ui import draw_game_over, draw_hud, draw_title_screen


@dataclass
class ShootFlash:
    position: pygame.Vector2
    rotation_deg: float
    time_left: float
    player_id: int


class GameState:
    def __init__(self) -> None:
        self.mode = "title"
        self.level = DEFAULT_LEVEL
        self.tiles = build_tiles(self.level)
        wall_size = TILE_SIZE - WALL_INSET * 2
        self.walls = [
            pygame.Rect(tile.x + WALL_INSET, tile.y + WALL_INSET, wall_size, wall_size)
            for tile in self.tiles
        ]
        self.sprites = load_sprites()
        self.scores = {1: 0, 2: 0}
        self.bullets: list[Bullet] = []
        self.tanks: dict[int, Tank] = {}
        self.fire_timers = {1: 0.0, 2: 0.0}
        self.winner_id: int | None = None
        self.shoot_flashes: list[ShootFlash] = []
        self.reset_round()

    def reset_round(self) -> None:
        p1_pos = self._find_open_tile(1, 1, 1, 1)
        p2_pos = self._find_open_tile(len(self.level) - 2, len(self.level[0]) - 2, -1, -1)
        self.tanks = {
            1: Tank(position=p1_pos, rotation_deg=0.0, turret_rotation_deg=0.0),
            2: Tank(position=p2_pos, rotation_deg=180.0, turret_rotation_deg=180.0),
        }
        self.bullets = []
        self.fire_timers = {1: 0.0, 2: 0.0}
        self.winner_id = None
        self.shoot_flashes = []

    def update(self, dt: float) -> None:
        if self.mode == "title":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
                self.reset_round()
                self.mode = "play"
        elif self.mode == "play":
            self._update_play(dt)
        elif self.mode == "game_over":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
                self.reset_round()
                self.mode = "play"

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((20, 20, 24))
        if self.mode == "title":
            draw_title_screen(screen)
        elif self.mode == "play":
            self._render_play(screen)
        elif self.mode == "game_over":
            self._render_play(screen)
            winner_text = "Player 1 Wins!" if self.winner_id == 1 else "Player 2 Wins!"
            draw_game_over(screen, winner_text)

    def _update_play(self, dt: float) -> None:
        self.fire_timers[1] = max(0.0, self.fire_timers[1] - dt)
        self.fire_timers[2] = max(0.0, self.fire_timers[2] - dt)

        keys = pygame.key.get_pressed()
        self._handle_tank_input(1, PLAYER1, keys, dt)
        self._handle_tank_input(2, PLAYER2, keys, dt)

        self._update_bullets(dt)
        self._update_shoot_flashes(dt)
        self._check_bullet_hits()

        if self.winner_id is not None:
            self.scores[self.winner_id] += 1
            self.mode = "game_over"

    def _render_play(self, screen: pygame.Surface) -> None:
        for wall in self.walls:
            pygame.draw.rect(screen, WALL_COLOR, wall)

        for bullet in self.bullets:
            pygame.draw.circle(
                screen,
                BULLET_COLOR,
                (int(bullet.position.x), int(bullet.position.y)),
                BULLET_RADIUS,
            )

        for player_id, tank in self.tanks.items():
            tank_sprites = self.sprites.tank_blue if player_id == 1 else self.sprites.tank_red
            if tank_sprites is None:
                color = PLAYER1_COLOR if player_id == 1 else PLAYER2_COLOR
                rect = tank.get_rect()
                pygame.draw.rect(screen, color, rect)
                direction = pygame.Vector2(1, 0).rotate(tank.turret_rotation_deg)
                turret_end = tank.position + direction * TURRET_LENGTH
                pygame.draw.line(
                    screen,
                    (230, 230, 230),
                    (int(tank.position.x), int(tank.position.y)),
                    (int(turret_end.x), int(turret_end.y)),
                    3,
                )
            else:
                self._draw_tank_sprite(screen, tank, tank_sprites)

        for flash in self.shoot_flashes:
            self._draw_shoot_flash(screen, flash)

        p1 = self.tanks[1]
        p2 = self.tanks[2]
        draw_hud(screen, p1.health, p2.health, self.scores[1], self.scores[2])

    def _handle_tank_input(self, player_id: int, controls, keys, dt: float) -> None:
        tank = self.tanks[player_id]
        forward = (1 if keys[controls.up] else 0) - (1 if keys[controls.down] else 0)
        turn = (1 if keys[controls.right] else 0) - (1 if keys[controls.left] else 0)

        previous = tank.position.copy()
        tank.update(dt, forward, turn)
        tank.turret_rotation_deg = tank.rotation_deg

        half = TANK_SIZE / 2
        tank.position.x = clamp(tank.position.x, half, SCREEN_WIDTH - half)
        tank.position.y = clamp(tank.position.y, half, SCREEN_HEIGHT - half)

        if any(wall.colliderect(tank.get_rect()) for wall in self.walls):
            tank.position = previous

        if (keys[controls.fire] or keys[controls.fire_alt]) and self.fire_timers[player_id] <= 0.0:
            if self._count_bullets(player_id) < BULLET_MAX_PER_PLAYER:
                self._spawn_bullet(player_id, tank)
                self.fire_timers[player_id] = BULLET_COOLDOWN

    def _spawn_bullet(self, player_id: int, tank: Tank) -> None:
        direction = pygame.Vector2(1, 0).rotate(tank.turret_rotation_deg)
        spawn_offset = TANK_SIZE / 2 + BULLET_RADIUS + 2
        position = tank.position + direction * spawn_offset
        velocity = direction * BULLET_SPEED
        self.bullets.append(Bullet(position=position, velocity=velocity, owner_id=player_id))
        self._spawn_shoot_flash(player_id, tank, direction)

    def _update_bullets(self, dt: float) -> None:
        screen_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        alive: list[Bullet] = []

        for bullet in self.bullets:
            bullet.update(dt)
            bullet_rect = bullet.get_rect()

            for wall in self.walls:
                if bullet_rect.colliderect(wall):
                    normal, overlap = self._collision_normal_and_overlap(bullet_rect, wall)
                    bullet.velocity = reflect_velocity(bullet.velocity, normal)
                    bullet.position += normal * (overlap + 0.1)
                    bullet.bounces += 1
                    break

            if (
                screen_rect.collidepoint(bullet.position.x, bullet.position.y)
                and bullet.bounces < BULLET_MAX_BOUNCES
            ):
                alive.append(bullet)

        self.bullets = alive

    def _update_shoot_flashes(self, dt: float) -> None:
        remaining: list[ShootFlash] = []
        for flash in self.shoot_flashes:
            flash.time_left -= dt
            if flash.time_left > 0:
                remaining.append(flash)
        self.shoot_flashes = remaining

    def _check_bullet_hits(self) -> None:
        remaining: list[Bullet] = []
        for bullet in self.bullets:
            hit = False
            for player_id, tank in self.tanks.items():
                if player_id == bullet.owner_id:
                    continue
                if tank.get_rect().colliderect(bullet.get_rect()):
                    tank.health -= 1
                    hit = True
                    if tank.health <= 0 and self.winner_id is None:
                        self.winner_id = bullet.owner_id
                    break
            if not hit:
                remaining.append(bullet)
        self.bullets = remaining

    def _count_bullets(self, owner_id: int) -> int:
        return sum(1 for bullet in self.bullets if bullet.owner_id == owner_id)

    def _collision_normal_and_overlap(self, bullet: pygame.Rect, wall: pygame.Rect) -> tuple[pygame.Vector2, float]:
        overlap_x = min(bullet.right - wall.left, wall.right - bullet.left)
        overlap_y = min(bullet.bottom - wall.top, wall.bottom - bullet.top)

        if overlap_x < overlap_y:
            normal = pygame.Vector2(-1, 0) if bullet.centerx < wall.centerx else pygame.Vector2(1, 0)
            return normal, overlap_x

        normal = pygame.Vector2(0, -1) if bullet.centery < wall.centery else pygame.Vector2(0, 1)
        return normal, overlap_y

    def _draw_tank_sprite(self, screen: pygame.Surface, tank: Tank, sprites: TankSprites) -> None:
        body = pygame.transform.rotate(sprites.body, -tank.rotation_deg)
        body_rect = body.get_rect(center=(int(tank.position.x), int(tank.position.y)))
        screen.blit(body, body_rect)

        turret = pygame.transform.rotate(sprites.turret, -tank.turret_rotation_deg)
        turret_rect = turret.get_rect(center=(int(tank.position.x), int(tank.position.y)))
        screen.blit(turret, turret_rect)

    def _spawn_shoot_flash(self, player_id: int, tank: Tank, direction: pygame.Vector2) -> None:
        flash_offset = TANK_SIZE / 2 + 2
        position = tank.position + direction * flash_offset
        self.shoot_flashes.append(
            ShootFlash(
                position=position,
                rotation_deg=tank.turret_rotation_deg,
                time_left=SHOOT_FLASH_DURATION,
                player_id=player_id,
            )
        )

    def _draw_shoot_flash(self, screen: pygame.Surface, flash: ShootFlash) -> None:
        sprite = self.sprites.shoot_blue if flash.player_id == 1 else self.sprites.shoot_red
        if sprite is None:
            return
        sprite = pygame.transform.rotate(sprite, -flash.rotation_deg)
        rect = sprite.get_rect(center=(int(flash.position.x), int(flash.position.y)))
        screen.blit(sprite, rect)

    def _find_open_tile(self, start_row: int, start_col: int, row_step: int, col_step: int) -> pygame.Vector2:
        rows = len(self.level)
        cols = len(self.level[0])
        row = start_row

        while 0 <= row < rows:
            col = start_col
            while 0 <= col < cols:
                if self.level[row][col] != "#":
                    return pygame.Vector2(
                        col * TILE_SIZE + TILE_SIZE / 2,
                        row * TILE_SIZE + TILE_SIZE / 2,
                    )
                col += col_step
            row += row_step

        return pygame.Vector2(TILE_SIZE * 1.5, TILE_SIZE * 1.5)
