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
    ROUND_WIN_LIMIT,
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
from game.entities.wall import Wall, WallType, WallState
from game.input import PLAYER1, PLAYER2
from game.levels import ALL_MAPS, MapData, build_walls, get_open_tiles
from game.managers.bullet_manager import BulletManager
from game.managers.collision_manager import CollisionManager
from game.managers.particle_manager import ParticleManager
from game.managers.food_manager import FoodManager
from game.managers.powerup_manager import PowerUpManager
from game.managers.sound_manager import SoundManager
from game.ui import (
    draw_countdown,
    draw_game_over,
    draw_hud,
    draw_map_select,
    draw_match_winner,
    draw_pause_menu,
    draw_title_screen,
)


# ── small helper ──────────────────────────────────────────────────────────

@dataclass
class ShootFlash:
    position: pygame.Vector2
    rotation_deg: float
    time_left: float
    player_id: int




class GameState:
    def __init__(self) -> None:
        # Mode: "title" → "map_select" → "countdown" → "play" → "round_over" → "countdown" → "play"/… → "match_over"
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
        self.round_wins: dict[int, int] = {1: 0, 2: 0}  # track rounds won by each player
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
        # ESC key tracking for pause menu
        self._esc_pressed: bool = False
        # Pause menu state: 0 = SFX, 1 = Music, 2 = Return to Main Menu
        self._pause_menu_selection: int = 0
        # Countdown timer (3-2-1) before gameplay starts
        self._countdown_timer: float = 0.0
        # Title screen menu selection: 0 = Play, 1 = Settings
        self._title_selection: int = 0
        # Settings menu selection (reuses pause-menu volume controls from title)
        self._settings_selection: int = 0

    # ── public interface ──────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        self._key_cooldown = max(0.0, self._key_cooldown - dt)
        keys = pygame.key.get_pressed()

        if self.mode == "title":
            self._update_title(keys)

        elif self.mode == "settings":
            self._update_settings(keys)

        elif self.mode == "map_select":
            self._update_map_select(keys)

        elif self.mode == "play":
            self._update_play(dt, keys)

        elif self.mode == "paused":
            self._update_pause_menu(keys)

        elif self.mode == "countdown":
            self._countdown_timer -= dt
            if self._countdown_timer <= 0:
                self.mode = "play"

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
            draw_title_screen(screen, self._title_selection)

        elif self.mode == "settings":
            sfx_vol = self.sound_mgr.get_sfx_volume()
            music_vol = self.sound_mgr.get_music_volume()
            draw_title_screen(screen, self._title_selection)
            draw_pause_menu(screen, self._settings_selection, sfx_vol, music_vol,
                            title_text="SETTINGS", show_return=True, return_label="Back")

        elif self.mode == "map_select":
            draw_map_select(screen, ALL_MAPS, self.map_index)

        elif self.mode == "play":
            self._render_play(screen)

        elif self.mode == "paused":
            self._render_play(screen)
            sfx_vol = self.sound_mgr.get_sfx_volume()
            music_vol = self.sound_mgr.get_music_volume()
            draw_pause_menu(screen, self._pause_menu_selection, sfx_vol, music_vol,
                            show_return=True, return_label="Return to Main Menu")

        elif self.mode == "countdown":
            self._render_play(screen)
            draw_countdown(screen, self._countdown_timer)

        elif self.mode == "round_over":
            self._render_play(screen)
            
            # Draw explosion sprite if available
            if self._explosion_sprite is not None:
                explosion_rect = self._explosion_sprite.get_rect(
                    center=(int(self._explosion_pos.x), int(self._explosion_pos.y))
                )
                screen.blit(self._explosion_sprite, explosion_rect)
            
            killed_id = 1 if self.winner_id == 2 else 2
            winner_text = f"Player {self.winner_id} wins Round {self.round_number}!"
            draw_game_over(screen, winner_text, f"Rounds Won  |  "
                           f"P1: {self.round_wins[1]}  /  P2: {self.round_wins[2]}  "
                           f"(first to {ROUND_WIN_LIMIT})")

        elif self.mode == "match_over":
            self._render_play(screen)
            draw_match_winner(screen, self.match_winner_id or 1, self.round_wins)

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
        self.round_wins = {1: 0, 2: 0}
        self.round_number = 0
        self.match_winner_id = None
        self.food_mgr.reset()  # Clean up food items from the previous match
        self._load_map()
        self._start_round()  # This sets mode to "countdown"
        # Spawn initial food for the match
        self.food_mgr.set_open_tiles(get_open_tiles(self.current_map.grid))
        self.food_mgr.spawn_initial()

    def _load_map(self) -> None:
        walls, sp1, sp2 = build_walls(self.current_map.grid)
        self.walls = walls
        self.current_map.spawn_p1 = sp1
        self.current_map.spawn_p2 = sp2
        self.powerup_mgr.set_open_tiles(get_open_tiles(self.current_map.grid))

    def _start_round(self) -> None:
        self.round_number += 1
        self.scores = {1: 0, 2: 0}  # reset food score each round
        self.tanks = {
            1: Tank(position=self.current_map.spawn_p1.copy(), rotation_deg=90.0, turret_rotation_deg=90.0),
            2: Tank(position=self.current_map.spawn_p2.copy(), rotation_deg=-90.0, turret_rotation_deg=-90.0),
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
        # Start countdown before gameplay
        self._countdown_timer = 3.0
        self.mode = "countdown"

    # ── gameplay loop ─────────────────────────────────────────────────────

    def _update_play(self, dt: float, keys) -> None:
        # Handle ESC for pause menu
        if keys[pygame.K_ESCAPE] and not self._esc_pressed:
            self._esc_pressed = True
            self.mode = "paused"
            return
        if not keys[pygame.K_ESCAPE]:
            self._esc_pressed = False

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

        # Check if any player reached score limit via food → win the round
        for pid in (1, 2):
            if self.scores[pid] >= SCORE_LIMIT and round_winner is None and self.winner_id is None:
                round_winner = pid
                break

        # Power-ups
        pickups = self.powerup_mgr.update(dt, self.tanks)
        for _pid, _ptype in pickups:
            self.sound_mgr.play_powerup()

        # Particles
        self.particle_mgr.update(dt)

        # Round-end on kill OR reaching food score limit
        if round_winner is not None:
            self.winner_id = round_winner
            self.round_wins[round_winner] += 1  # increment round win counter

            # Check if this round win clinches the match
            if self.round_wins[round_winner] >= ROUND_WIN_LIMIT:
                self.match_winner_id = round_winner
                self.mode = "match_over"
                return

            # Spawn explosion at killed tank (only for kill rounds)
            killed_id = 1 if round_winner == 2 else 2
            if self.tanks[killed_id].health <= 0:
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
            # held key). Give players a short moment to see the result.
            self._round_over_timer = 1.0
            self.mode = "round_over"

    # ── title screen ──────────────────────────────────────────────────────

    def _update_title(self, keys) -> None:
        """Navigate the main menu (Play / Settings)."""
        if self._key_cooldown > 0:
            return
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self._title_selection = (self._title_selection - 1) % 2
            self._key_cooldown = 0.18
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self._title_selection = (self._title_selection + 1) % 2
            self._key_cooldown = 0.18
        elif self._menu_confirm(keys):
            if self._title_selection == 0:  # Play
                self.mode = "map_select"
            else:  # Settings
                self._settings_selection = 0
                self.mode = "settings"
            self._key_cooldown = 0.25

    def _update_settings(self, keys) -> None:
        """Volume settings accessible from the main menu."""
        from game.config import VOLUME_STEP

        if self._key_cooldown > 0:
            return

        # Handle ESC or Confirm on "Back" to return to title
        if keys[pygame.K_ESCAPE] and not self._esc_pressed:
            self._esc_pressed = True
            self.mode = "title"
            self._key_cooldown = 0.25
            return
        if not keys[pygame.K_ESCAPE]:
            self._esc_pressed = False

        max_sel = 2  # 0=SFX, 1=Music, 2=Back
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self._settings_selection = (self._settings_selection - 1) % (max_sel + 1)
            self._key_cooldown = 0.15
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self._settings_selection = (self._settings_selection + 1) % (max_sel + 1)
            self._key_cooldown = 0.15
        elif self._menu_confirm(keys) and self._settings_selection == 2:
            self.mode = "title"
            self._key_cooldown = 0.25
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self._adjust_volume(self._settings_selection, -VOLUME_STEP)
            self._key_cooldown = 0.12
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self._adjust_volume(self._settings_selection, VOLUME_STEP)
            self._key_cooldown = 0.12

    def _update_pause_menu(self, keys) -> None:
        """Handle input in pause menu for volume controls + Return to Main Menu."""
        from game.config import VOLUME_STEP

        # Handle ESC to unpause
        if keys[pygame.K_ESCAPE] and not self._esc_pressed:
            self._esc_pressed = True
            # Start countdown before resuming gameplay
            self._countdown_timer = 3.0
            self.mode = "countdown"
        if not keys[pygame.K_ESCAPE]:
            self._esc_pressed = False

        # Cooldown for menu navigation
        if self._key_cooldown > 0:
            return

        max_sel = 2  # 0=SFX, 1=Music, 2=Return to Main Menu
        # Navigate
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self._pause_menu_selection = (self._pause_menu_selection - 1) % (max_sel + 1)
            self._key_cooldown = 0.15
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self._pause_menu_selection = (self._pause_menu_selection + 1) % (max_sel + 1)
            self._key_cooldown = 0.15
        # Confirm on "Return to Main Menu"
        elif self._menu_confirm(keys) and self._pause_menu_selection == 2:
            self._pause_menu_selection = 0
            self.mode = "title"
            self._key_cooldown = 0.25
        # Adjust volume
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self._adjust_volume(self._pause_menu_selection, -VOLUME_STEP)
            self._key_cooldown = 0.12
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self._adjust_volume(self._pause_menu_selection, VOLUME_STEP)
            self._key_cooldown = 0.12

    def _adjust_volume(self, selection: int, delta: float) -> None:
        """Adjust SFX (0) or Music (1) volume by *delta*. Ignore other indices."""
        if selection == 0:
            self.sound_mgr.set_sfx_volume(self.sound_mgr.get_sfx_volume() + delta)
        elif selection == 1:
            self.sound_mgr.set_music_volume(self.sound_mgr.get_music_volume() + delta)

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

        # Collision resolution (split X/Y) – treat the other tank as solid
        other_id = 2 if player_id == 1 else 1
        other_tank = self.tanks[other_id]
        active_walls = [w for w in self.walls if not w.is_destroyed]
        tank.position = self.collision_mgr.resolve_tank_walls(
            tank.position, previous, active_walls,
            other_tank_rect=other_tank.get_rect(),
        )

        # Shooting
        if (keys[controls.fire] or keys[controls.fire_alt]) and self.bullet_mgr.can_fire(player_id):
            self.bullet_mgr.spawn(player_id, tank)
            self._spawn_shoot_flash(player_id, tank)
            self.sound_mgr.play_shoot()

    # ── rendering ─────────────────────────────────────────────────────────

    def _render_play(self, screen: pygame.Surface) -> None:
        # Draw background image if available, otherwise the screen is already filled with BG_COLOR
        if getattr(self.sprites, "background", None) is not None:
            screen.blit(self.sprites.background, (0, 0))

        # Walls
        for wall in self.walls:
            if wall.is_destroyed:
                continue
            
            # Use sprites if available, otherwise fallback to colored rectangles
            if self.sprites.wall_sprites is not None:
                wall_state = wall.visual_state
                if wall_state == WallState.UNBROKEN:
                    sprite = self.sprites.wall_sprites.unbroken
                elif wall_state == WallState.BREAKABLE:
                    sprite = self.sprites.wall_sprites.breakable
                elif wall_state == WallState.BROKEN:
                    sprite = self.sprites.wall_sprites.broken
                else:  # DESTROYED - shouldn't render, but just in case
                    sprite = self.sprites.wall_sprites.destroyed
                
                screen.blit(sprite, wall.rect)
            else:
                # Fallback to colored rectangles
                color = BRICK_COLOR if wall.wall_type == WallType.BRICK else WALL_COLOR
                pygame.draw.rect(screen, color, wall.rect)

        # Food items
        for food in self.food_mgr.items:
            center = (int(food.position.x), int(food.position.y))
            if self.sprites.food_sprite is not None:
                food_rect = self.sprites.food_sprite.get_rect(center=center)
                screen.blit(self.sprites.food_sprite, food_rect)
            else:
                # Fallback to colored circles
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
            center = (int(item.position.x), int(item.position.y))
            if self.sprites.powerup_sprites is not None:
                if item.powerup_type == PowerUpType.SPEED:
                    sprite = self.sprites.powerup_sprites.speed
                elif item.powerup_type == PowerUpType.SHIELD:
                    sprite = self.sprites.powerup_sprites.shield
                else:
                    sprite = self.sprites.powerup_sprites.triple
                item_rect = sprite.get_rect(center=center)
                screen.blit(sprite, item_rect)
            else:
                color = POWERUP_COLORS.get(item.powerup_type.value, (200, 200, 200))
                pygame.draw.circle(screen, color, center, POWERUP_SIZE // 2)
                # Inner icon indicator
                pygame.draw.circle(screen, (255, 255, 255), center, POWERUP_SIZE // 4)

        # Bullets
        for bullet in self.bullet_mgr.bullets:
            # Use player color for bullets
            bullet_color = PLAYER1_COLOR if bullet.owner_id == 1 else PLAYER2_COLOR
            pygame.draw.circle(
                screen,
                bullet_color,
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

            # Light arrow movement indicator
            if tank.is_moving_forward:
                base_color = PLAYER1_COLOR if player_id == 1 else PLAYER2_COLOR
                surf_size = TANK_SIZE * 3
                arrow_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
                cx, cy = surf_size / 2, surf_size / 2
                
                for i in range(3):
                    alpha = max(0, 200 - (i * 70))
                    color = (base_color[0], base_color[1], base_color[2], alpha)
                    tip_y = cy - (TANK_SIZE * 0.7) - (i * TANK_SIZE * 0.4)
                    
                    points = [
                        (cx, tip_y),                       # Top center
                        (cx - 10, tip_y + 10),             # Bottom left outer
                        (cx - 6, tip_y + 13),              # Bottom left inner
                        (cx, tip_y + 5),                   # Bottom center inner
                        (cx + 6, tip_y + 13),              # Bottom right inner
                        (cx + 10, tip_y + 10),             # Bottom right outer
                    ]
                    pygame.draw.polygon(arrow_surf, color, points)

                rotated_arrow = pygame.transform.rotate(arrow_surf, -tank.rotation_deg)
                arrow_rect = rotated_arrow.get_rect(center=(int(tank.position.x), int(tank.position.y)))
                screen.blit(rotated_arrow, arrow_rect)

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
        draw_hud(screen, p1, p2, self.scores, self.round_number, self.round_wins)

    # ── helper drawing methods ────────────────────────────────────────────

    def _draw_tank_fallback(self, screen: pygame.Surface, tank: Tank, player_id: int) -> None:
        color = PLAYER1_COLOR if player_id == 1 else PLAYER2_COLOR
        rect = tank.get_rect()
        pygame.draw.rect(screen, color, rect)
        direction = pygame.Vector2(0, -1).rotate(tank.turret_rotation_deg)
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

        turret = pygame.transform.rotate(sprites.turret, -tank.turret_rotation_deg + 90.0)
        turret_rect = turret.get_rect(center=(int(tank.position.x), int(tank.position.y)))
        screen.blit(turret, turret_rect)

    def _spawn_shoot_flash(self, player_id: int, tank: Tank) -> None:
        direction = pygame.Vector2(0, -1).rotate(tank.turret_rotation_deg)
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
        rotated = pygame.transform.rotate(sprite, -flash.rotation_deg + 90.0)
        rect = rotated.get_rect(center=(int(flash.position.x), int(flash.position.y)))
        screen.blit(rotated, rect)

    # ── utilities ─────────────────────────────────────────────────────────

    def _menu_confirm(self, keys) -> bool:
        if self._key_cooldown > 0:
            return False
        return keys[pygame.K_RETURN] or keys[pygame.K_SPACE]
