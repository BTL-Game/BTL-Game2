from dataclasses import dataclass
from pathlib import Path

import pygame

from game.config import SHOOT_SIZE, TANK_SIZE


@dataclass
class TankSprites:
    body: pygame.Surface
    turret: pygame.Surface


@dataclass
class SpriteSet:
    tank_blue: TankSprites | None = None
    tank_red: TankSprites | None = None
    wall: pygame.Surface | None = None
    bullet: pygame.Surface | None = None
    shoot_blue: pygame.Surface | None = None
    shoot_red: pygame.Surface | None = None


ASSET_ROOT = Path(__file__).resolve().parents[2] / "assets"
DEFAULT_BODY_NAME = "body_tracks.png"
DEFAULT_TURRET_NAME = "weapon.png"
DEFAULT_SHOOT_NAME = "shoot.png"


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


def load_sprites() -> SpriteSet:
    size = (TANK_SIZE, TANK_SIZE)
    shoot_size = (SHOOT_SIZE, SHOOT_SIZE)

    blue_body = _load_image(ASSET_ROOT / "Blue" / "Bodies" / DEFAULT_BODY_NAME, size)
    blue_turret = _load_image(ASSET_ROOT / "Blue" / "Weapons" / DEFAULT_TURRET_NAME, size)
    red_body = _load_image(ASSET_ROOT / "Red" / "Bodies" / DEFAULT_BODY_NAME, size)
    red_turret = _load_image(ASSET_ROOT / "Red" / "Weapons" / DEFAULT_TURRET_NAME, size)
    shoot_blue = _load_image(ASSET_ROOT / "Blue" / "Weapons" / DEFAULT_SHOOT_NAME, shoot_size)
    shoot_red = _load_image(ASSET_ROOT / "Red" / "Weapons" / DEFAULT_SHOOT_NAME, shoot_size)

    return SpriteSet(
        tank_blue=_build_tank_sprites(blue_body, blue_turret),
        tank_red=_build_tank_sprites(red_body, red_turret),
        shoot_blue=shoot_blue,
        shoot_red=shoot_red,
    )
