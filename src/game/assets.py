import sys
from dataclasses import dataclass
from pathlib import Path

import pygame

from game.config import FOOD_SIZE, POWERUP_SIZE, SHOOT_SIZE, TANK_SIZE, TILE_SIZE, WALL_INSET


def _get_asset_root() -> Path:
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / "assets"
    else:
        return Path(__file__).resolve().parents[2] / "assets"


ASSET_ROOT = _get_asset_root()


@dataclass
class TankSprites:
    body: pygame.Surface
    turret: pygame.Surface


@dataclass
class WallSprites:
    """Sprites for different wall states."""
    unbroken: pygame.Surface    # Steel walls
    breakable: pygame.Surface   # Full health brick (2 hits)
    broken: pygame.Surface      # Damaged brick (1 hit)
    destroyed: pygame.Surface   # Destroyed brick (0 hits)


@dataclass
class PowerUpSprites:
    """Sprites for power-up types."""
    speed: pygame.Surface
    shield: pygame.Surface
    triple: pygame.Surface


@dataclass
class SpriteSet:
    tank_blue: TankSprites | None = None
    tank_red: TankSprites | None = None
    wall_sprites: WallSprites | None = None
    food_sprite: pygame.Surface | None = None
    powerup_sprites: PowerUpSprites | None = None
    background: pygame.Surface | None = None
    bullet: pygame.Surface | None = None
    shoot_blue: pygame.Surface | None = None
    shoot_red: pygame.Surface | None = None
    explosion_blue: pygame.Surface | None = None
    explosion_red: pygame.Surface | None = None


DEFAULT_BODY_NAME = "body_tracks.png"
DEFAULT_TURRET_NAME = "weapon.png"
DEFAULT_SHOOT_NAME = "shoot.png"
DEFAULT_EXPLOSION_BLUE_NAME = "blueexplosion.png"
DEFAULT_EXPLOSION_RED_NAME = "redexplosion.png"

# Wall asset names
WALL_UNBROKEN_NAME = "unbroken_wall.png"
WALL_BREAKABLE_NAME = "breakable_wall.png"
WALL_BROKEN_NAME = "broken_wall.png"
WALL_DESTROYED_NAME = "destroyed_wall.png"

# Food & power-up asset names
# Use coin image for food visuals
FOOD_NAME = "coin.png"
POWERUP_SPEED_NAME = "speed.png"
POWERUP_SHIELD_NAME = "shield.png"
POWERUP_TRIPLE_NAME = "tripple.png"
BACKGROUND_NAME = "background.png"


def _load_image(path: Path, size: tuple[int, int] | None = None) -> pygame.Surface | None:
    if not path.exists():
        return None

    try:
        image = pygame.image.load(str(path))
    except pygame.error:
        return None

    image = image.convert_alpha()
    if size is not None:
        image = pygame.transform.smoothscale(image, size)
    return image


def _build_tank_sprites(body: pygame.Surface | None, turret: pygame.Surface | None) -> TankSprites | None:
    if body is None or turret is None:
        return None
    return TankSprites(body=body, turret=turret)


def _build_wall_sprites(unbroken: pygame.Surface | None, breakable: pygame.Surface | None,
                        broken: pygame.Surface | None, destroyed: pygame.Surface | None) -> WallSprites | None:
    """Build wall sprites if all are present."""
    if unbroken is None or breakable is None or broken is None or destroyed is None:
        return None
    return WallSprites(
        unbroken=unbroken,
        breakable=breakable,
        broken=broken,
        destroyed=destroyed
    )


def _build_powerup_sprites(speed: pygame.Surface | None, shield: pygame.Surface | None,
                           triple: pygame.Surface | None) -> PowerUpSprites | None:
    """Build power-up sprites if all are present."""
    if speed is None or shield is None or triple is None:
        return None
    return PowerUpSprites(speed=speed, shield=shield, triple=triple)


def load_sprites() -> SpriteSet:
    size = (TANK_SIZE, TANK_SIZE)
    shoot_size = (SHOOT_SIZE, SHOOT_SIZE)
    explosion_size = (TANK_SIZE * 2, TANK_SIZE * 2)
    wall_size = (TILE_SIZE - WALL_INSET * 2, TILE_SIZE - WALL_INSET * 2)
    food_size = (FOOD_SIZE, FOOD_SIZE)
    powerup_size = (POWERUP_SIZE, POWERUP_SIZE)

    blue_body = _load_image(ASSET_ROOT / "Blue" / "Bodies" / DEFAULT_BODY_NAME, size)
    blue_turret = _load_image(ASSET_ROOT / "Blue" / "Weapons" / DEFAULT_TURRET_NAME, size)
    red_body = _load_image(ASSET_ROOT / "Red" / "Bodies" / DEFAULT_BODY_NAME, size)
    red_turret = _load_image(ASSET_ROOT / "Red" / "Weapons" / DEFAULT_TURRET_NAME, size)
    shoot_blue = _load_image(ASSET_ROOT / "Blue" / "Weapons" / DEFAULT_SHOOT_NAME, shoot_size)
    shoot_red = _load_image(ASSET_ROOT / "Red" / "Weapons" / DEFAULT_SHOOT_NAME, shoot_size)
    explosion_blue = _load_image(ASSET_ROOT / "Blue" / "Bodies" / DEFAULT_EXPLOSION_BLUE_NAME, explosion_size)
    explosion_red = _load_image(ASSET_ROOT / "Red" / "Bodies" / DEFAULT_EXPLOSION_RED_NAME, explosion_size)

    # Load wall sprites
    wall_unbroken = _load_image(ASSET_ROOT / "Wall" / WALL_UNBROKEN_NAME, wall_size)
    wall_breakable = _load_image(ASSET_ROOT / "Wall" / WALL_BREAKABLE_NAME, wall_size)
    wall_broken = _load_image(ASSET_ROOT / "Wall" / WALL_BROKEN_NAME, wall_size)
    wall_destroyed = _load_image(ASSET_ROOT / "Wall" / WALL_DESTROYED_NAME, wall_size)

    # Food and power-up sprites
    food_sprite = _load_image(ASSET_ROOT / "Food" / FOOD_NAME, food_size)
    powerup_speed = _load_image(ASSET_ROOT / "Food" / POWERUP_SPEED_NAME, powerup_size)
    powerup_shield = _load_image(ASSET_ROOT / "Food" / POWERUP_SHIELD_NAME, powerup_size)
    powerup_triple = _load_image(ASSET_ROOT / "Food" / POWERUP_TRIPLE_NAME, powerup_size)

    # Background sprite
    # Lazy import to avoid circular dependency
    try:
        from game.config import SCREEN_WIDTH, SCREEN_HEIGHT
        bg_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
    except Exception:
        bg_size = None
    background = _load_image(ASSET_ROOT / "Background" / BACKGROUND_NAME, bg_size)

    return SpriteSet(
        tank_blue=_build_tank_sprites(blue_body, blue_turret),
        tank_red=_build_tank_sprites(red_body, red_turret),
        wall_sprites=_build_wall_sprites(wall_unbroken, wall_breakable, wall_broken, wall_destroyed),
        food_sprite=food_sprite,
        powerup_sprites=_build_powerup_sprites(powerup_speed, powerup_shield, powerup_triple),
        background=background,
        shoot_blue=shoot_blue,
        shoot_red=shoot_red,
        explosion_blue=explosion_blue,
        explosion_red=explosion_red,
    )
