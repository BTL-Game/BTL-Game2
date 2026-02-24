from __future__ import annotations

from dataclasses import dataclass

import pygame

from game.assets import TankSprites, load_sprites
from game.config import (
    BG_COLOR,
    BRICK_COLOR,
    BULLET_COLOR,
    BULLET_RADIUS,
    FOOD_SIZE,
    PLAYER1_COLOR,
    PLAYER2_COLOR,
    POWERUP_COLORS,
    POWERUP_SIZE,
    SCORE_LIMIT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SHOOT_FLASH_DURATION,
    TANK_SIZE,
    TURRET_LENGTH,
    WALL_COLOR,
)
from game.entities.bullet import Bullet
from game.entities.powerup import PowerUpType
from game.entities.tank import Tank
from game.entities.wall import Wall, WallType
from game.input import PLAYER1, PLAYER2
from game.levels import ALL_MAPS, MapData, build_walls, get_open_tiles
from game.managers.bullet_manager import BulletManager
from game.managers.collision_manager import CollisionManager
from game.managers.particle_manager import ParticleManager
from game.managers.food_manager import FoodManager
from game.managers.powerup_manager import PowerUpManager
from game.managers.sound_manager import SoundManager
from game.ui import (
    draw_game_over,
    draw_hud,
    draw_map_select,
    draw_match_winner,
    draw_title_screen,
)


# ── small helper ──────────────────────────────────────────────────────────

@dataclass
class ShootFlash:
    position: pygame.Vector2
    rotation_deg: float
    time_left: float
    player_id: int


# ══════════════════════════════════════════════════════════════════════════
# GameState (orchestrator – delegates to managers)
# ══════════════════════════════════════════════════════════════════════════

class GameState:
    def __init__(self) -> None:
        # Mode: "title" → "map_select" → "play" → "round_over" → "play"/… → "match_over"
        self.mode: str = "title"

        # Managers
        self.bullet_mgr = BulletManager()
        self.collision_mgr = CollisionManager()
        self.powerup_mgr = PowerUpManager()
        self.food_mgr = FoodManager()
        self.particle_mgr = ParticleManager()
        self.sound_mgr = SoundManager()

        # Sprites
        self.sprites = load_sprites()

        # Map
        self.map_index: int = 0
        self.current_map: MapData = ALL_MAPS[0]
        self.walls: list[Wall] = []

        # Game data
        self.scores: dict[int, int] = {1: 0, 2: 0}
        self.tanks: dict[int, Tank] = {}
        self.shoot_flashes: list[ShootFlash] = []
        self.winner_id: int | None = None      # round winner
        self.match_winner_id: int | None = None  # overall match winner
        self.round_number: int = 0

        # Debounce for key presses in menus
        self._key_cooldown: float = 0.0
        # Timer to keep the round_over screen visible before accepting input
        self._round_over_timer: float = 0.0
        # Explosion sprite and position for drawing during round_over
        self._explosion_sprite: pygame.Surface | None = None
        self._explosion_pos: pygame.Vector2 = pygame.Vector2(0, 0)

    # ── public interface ──────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        self._key_cooldown = max(0.0, self._key_cooldown - dt)
        keys = pygame.key.get_pressed()

        if self.mode == "title":
            if self._menu_confirm(keys):
                self.mode = "map_select"
                self._key_cooldown = 0.25

        elif self.mode == "map_select":
            self._update_map_select(keys)

        elif self.mode == "play":
            self._update_play(dt, keys)

        elif self.mode == "round_over":
            # Respect the explicit round-over timer first, then allow confirm
            if self._round_over_timer > 0.0:
                self._round_over_timer = max(0.0, self._round_over_timer - dt)
            else:
                if self._menu_confirm(keys):
                    self._start_round()
                    self._key_cooldown = 0.25

        elif self.mode == "match_over":
            if self._menu_confirm(keys):
                self.mode = "title"
                self._key_cooldown = 0.25

    def render(self, screen: pygame.Surface) -> None:
        screen.fill(BG_COLOR)

        if self.mode == "title":
            draw_title_screen(screen)

        elif self.mode == "map_select":
            draw_map_select(screen, ALL_MAPS, self.map_index)

        elif self.mode == "play":
            self._render_play(screen)

        elif self.mode == "round_over":
            self._render_play(screen)
            
            # Draw explosion sprite if available
            if self._explosion_sprite is not None:
                explosion_rect = self._explosion_sprite.get_rect(
                    center=(int(self._explosion_pos.x), int(self._explosion_pos.y))
                )
                screen.blit(self._explosion_sprite, explosion_rect)
            
            killed_id = 1 if self.winner_id == 2 else 2
            winner_text = f"Player {self.winner_id} eliminated Player {killed_id}!"
            draw_game_over(screen, winner_text, f"Round {self.round_number}  |  "
                           f"P1: {self.scores[1]}  P2: {self.scores[2]}")

        elif self.mode == "match_over":
            self._render_play(screen)
            draw_match_winner(screen, self.match_winner_id or 1, self.scores)

    # ── map select ────────────────────────────────────────────────────────

    def _update_map_select(self, keys) -> None:
        if self._key_cooldown > 0:
            return
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.map_index = (self.map_index - 1) % len(ALL_MAPS)
            self._key_cooldown = 0.18
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.map_index = (self.map_index + 1) % len(ALL_MAPS)
            self._key_cooldown = 0.18
        elif self._menu_confirm(keys):
            self._start_match()
            self._key_cooldown = 0.25

    # ── match / round lifecycle ───────────────────────────────────────────

    def _start_match(self) -> None:
        self.current_map = ALL_MAPS[self.map_index]
        self.scores = {1: 0, 2: 0}
        self.round_number = 0
        self.match_winner_id = None
        self._load_map()
        self._start_round()
        # Spawn initial food for the match
        self.food_mgr.set_open_tiles(get_open_tiles(self.current_map.grid))
        self.food_mgr.spawn_initial()
        self.mode = "play"

    def _load_map(self) -> None:
        walls, sp1, sp2 = build_walls(self.current_map.grid)
        self.walls = walls
        self.current_map.spawn_p1 = sp1
        self.current_map.spawn_p2 = sp2
        self.powerup_mgr.set_open_tiles(get_open_tiles(self.current_map.grid))

    def _start_round(self) -> None:
        self.round_number += 1
        self.tanks = {
            1: Tank(position=self.current_map.spawn_p1.copy(), rotation_deg=0.0, turret_rotation_deg=0.0),
            2: Tank(position=self.current_map.spawn_p2.copy(), rotation_deg=180.0, turret_rotation_deg=180.0),
        }
        self.bullet_mgr.reset()
        self.powerup_mgr.reset()
        self.particle_mgr.reset()
        self.shoot_flashes.clear()
        self.winner_id = None
        self._explosion_sprite = None
        self._round_over_timer = 0.0

        # Rebuild destructible walls each round
        self._load_map()
        # NOTE: food persists across rounds (not reset here)
        self.mode = "play"

    # ── gameplay loop ─────────────────────────────────────────────────────

    def _update_play(self, dt: float, keys) -> None:
        # Input
        self._handle_tank_input(1, PLAYER1, keys, dt)
        self._handle_tank_input(2, PLAYER2, keys, dt)

        # Bullets
        active_walls = [w for w in self.walls if not w.is_destroyed]
        bounces = self.bullet_mgr.update(dt, active_walls)
        if bounces > 0:
            self.sound_mgr.play_bounce()
        self._update_shoot_flashes(dt)

        round_winner = self.bullet_mgr.check_hits(self.tanks)

        # Food collection (this is how score increases)
        food_pickups = self.food_mgr.update(dt, self.tanks)
        for pid, score_val in food_pickups:
            self.scores[pid] += score_val
            self.sound_mgr.play_powerup()  # reuse powerup sound for food

        # Check if any player reached score limit via food
        for pid in (1, 2):
            if self.scores[pid] >= SCORE_LIMIT and self.match_winner_id is None:
                self.match_winner_id = pid
                self.mode = "match_over"
                return

        # Power-ups
        pickups = self.powerup_mgr.update(dt, self.tanks)
        for _pid, _ptype in pickups:
            self.sound_mgr.play_powerup()

        # Particles
        self.particle_mgr.update(dt)

        # Round-end on kill (reset round, NOT score)
        if round_winner is not None:
            self.winner_id = round_winner

            # Spawn explosion at killed tank
            killed_id = 1 if round_winner == 2 else 2
            killed_tank = self.tanks[killed_id]
            color = PLAYER1_COLOR if killed_id == 1 else PLAYER2_COLOR
            self.particle_mgr.spawn_explosion(killed_tank.position.copy(), color)
            self.sound_mgr.play_explosion()

            # Store explosion sprite for display during round_over
            explosion_sprite = self.sprites.explosion_blue if killed_id == 1 else self.sprites.explosion_red
            if explosion_sprite is not None:
                self._explosion_sprite = explosion_sprite
                self._explosion_pos = killed_tank.position.copy()

            # Prevent immediately skipping the round-over screen (e.g. from a
            # held key). Give players a short moment to see the explosion.
            self._round_over_timer = 1.0
            self.mode = "round_over"

    def _handle_tank_input(self, player_id: int, controls, keys, dt: float) -> None:
        tank = self.tanks[player_id]
        forward = (1 if keys[controls.up] else 0) - (1 if keys[controls.down] else 0)
        turn = (1 if keys[controls.right] else 0) - (1 if keys[controls.left] else 0)
        turret_turn = (1 if keys[controls.turret_right] else 0) - (1 if keys[controls.turret_left] else 0)

        previous = tank.position.copy()
        previous_rotation = tank.rotation_deg
        tank.update(dt, forward, turn, turret_turn)

        # make the turret follow the tank body's rotation delta
        tank.turret_rotation_deg += (tank.rotation_deg - previous_rotation)

        # Collision resolution (split X/Y)
        active_walls = [w for w in self.walls if not w.is_destroyed]
        tank.position = self.collision_mgr.resolve_tank_walls(tank.position, previous, active_walls)

        # Shooting
        if (keys[controls.fire] or keys[controls.fire_alt]) and self.bullet_mgr.can_fire(player_id):
            self.bullet_mgr.spawn(player_id, tank)
            self._spawn_shoot_flash(player_id, tank)
            self.sound_mgr.play_shoot()

    # ── rendering ─────────────────────────────────────────────────────────

    def _render_play(self, screen: pygame.Surface) -> None:
        # Walls
        for wall in self.walls:
            if wall.is_destroyed:
                continue
            color = BRICK_COLOR if wall.wall_type == WallType.BRICK else WALL_COLOR
            pygame.draw.rect(screen, color, wall.rect)

        # Food items
        for food in self.food_mgr.items:
            center = (int(food.position.x), int(food.position.y))
            # Color varies by wave for visual interest
            wave_colors = [
                (255, 220, 80), (80, 230, 120), (120, 200, 255),
                (255, 150, 80), (200, 120, 255),
            ]
            color = wave_colors[(food.wave - 1) % len(wave_colors)]
            pygame.draw.circle(screen, color, center, FOOD_SIZE // 2)
            # Score value label
            if food.score_value > 1:
                font = pygame.font.SysFont("arial", 10)
                val_surf = font.render(str(food.score_value), True, (20, 20, 20))
                screen.blit(val_surf, val_surf.get_rect(center=center))

        # Power-ups
        for item in self.powerup_mgr.items:
            color = POWERUP_COLORS.get(item.powerup_type.value, (200, 200, 200))
            center = (int(item.position.x), int(item.position.y))
            pygame.draw.circle(screen, color, center, POWERUP_SIZE // 2)
            # Inner icon indicator
            pygame.draw.circle(screen, (255, 255, 255), center, POWERUP_SIZE // 4)

        # Bullets
        for bullet in self.bullet_mgr.bullets:
            pygame.draw.circle(
                screen,
                BULLET_COLOR,
                (int(bullet.position.x), int(bullet.position.y)),
                BULLET_RADIUS,
            )

        # Tanks
        for player_id, tank in self.tanks.items():
            tank_sprites = self.sprites.tank_blue if player_id == 1 else self.sprites.tank_red
            if tank_sprites is None:
                self._draw_tank_fallback(screen, tank, player_id)
            else:
                self._draw_tank_sprite(screen, tank, tank_sprites)

            # Shield glow
            if tank.has_shield:
                shield_surf = pygame.Surface((TANK_SIZE + 8, TANK_SIZE + 8), pygame.SRCALPHA)
                pygame.draw.circle(
                    shield_surf, (100, 180, 255, 80),
                    (TANK_SIZE // 2 + 4, TANK_SIZE // 2 + 4), TANK_SIZE // 2 + 4,
                )
                screen.blit(shield_surf, (int(tank.position.x - TANK_SIZE // 2 - 4),
                                          int(tank.position.y - TANK_SIZE // 2 - 4)))

        # Shoot flashes
        for flash in self.shoot_flashes:
            self._draw_shoot_flash(screen, flash)

        # Particles
        self.particle_mgr.render(screen)

        # HUD
        p1 = self.tanks[1]
        p2 = self.tanks[2]
        draw_hud(screen, p1, p2, self.scores, self.round_number)

    # ── helper drawing methods ────────────────────────────────────────────

    def _draw_tank_fallback(self, screen: pygame.Surface, tank: Tank, player_id: int) -> None:
        color = PLAYER1_COLOR if player_id == 1 else PLAYER2_COLOR
        rect = tank.get_rect()
        pygame.draw.rect(screen, color, rect)
        direction = pygame.Vector2(1, 0).rotate(tank.turret_rotation_deg)
        turret_end = tank.position + direction * TURRET_LENGTH
        pygame.draw.line(
            screen, (230, 230, 230),
            (int(tank.position.x), int(tank.position.y)),
            (int(turret_end.x), int(turret_end.y)), 3,
        )

    def _draw_tank_sprite(self, screen: pygame.Surface, tank: Tank, sprites: TankSprites) -> None:
        body = pygame.transform.rotate(sprites.body, -tank.rotation_deg)
        body_rect = body.get_rect(center=(int(tank.position.x), int(tank.position.y)))
        screen.blit(body, body_rect)

        turret = pygame.transform.rotate(sprites.turret, -tank.turret_rotation_deg)
        turret_rect = turret.get_rect(center=(int(tank.position.x), int(tank.position.y)))
        screen.blit(turret, turret_rect)

    def _spawn_shoot_flash(self, player_id: int, tank: Tank) -> None:
        direction = pygame.Vector2(1, 0).rotate(tank.turret_rotation_deg)
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

    def _update_shoot_flashes(self, dt: float) -> None:
        self.shoot_flashes = [f for f in self.shoot_flashes if f.time_left - dt > 0]
        for f in self.shoot_flashes:
            f.time_left -= dt

    def _draw_shoot_flash(self, screen: pygame.Surface, flash: ShootFlash) -> None:
        sprite = self.sprites.shoot_blue if flash.player_id == 1 else self.sprites.shoot_red
        if sprite is None:
            return
        rotated = pygame.transform.rotate(sprite, -flash.rotation_deg)
        rect = rotated.get_rect(center=(int(flash.position.x), int(flash.position.y)))
        screen.blit(rotated, rect)

    # ── utilities ─────────────────────────────────────────────────────────

    def _menu_confirm(self, keys) -> bool:
        if self._key_cooldown > 0:
            return False
        return keys[pygame.K_RETURN] or keys[pygame.K_SPACE]
