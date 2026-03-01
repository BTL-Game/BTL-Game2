from __future__ import annotations

from dataclasses import dataclass, field

import pygame

from game.config import (
    TILE_BRICK,
    TILE_OPEN,
    TILE_SIZE,
    TILE_SPAWN_P1,
    TILE_SPAWN_P2,
    TILE_STEEL,
    WALL_INSET,
)
from game.entities.wall import Wall, WallType


@dataclass
class MapData:
    """Represents a single map/level."""
    name: str
    grid: list[str]
    description: str = ""
    spawn_p1: pygame.Vector2 = field(default_factory=lambda: pygame.Vector2(0, 0))
    spawn_p2: pygame.Vector2 = field(default_factory=lambda: pygame.Vector2(0, 0))


def _tile_center(row: int, col: int) -> pygame.Vector2:
    """Convert grid coordinates to pixel coordinates (center of tile)."""
    return pygame.Vector2(col * TILE_SIZE + TILE_SIZE / 2, row * TILE_SIZE + TILE_SIZE / 2)


def build_walls(grid: list[str]) -> tuple[list[Wall], pygame.Vector2, pygame.Vector2]:
    """Parse a grid and return (walls, spawn_p1, spawn_p2)."""
    walls: list[Wall] = []
    spawn_p1 = pygame.Vector2(TILE_SIZE * 1.5, TILE_SIZE * 1.5)
    spawn_p2 = pygame.Vector2(TILE_SIZE * 1.5, TILE_SIZE * 1.5)
    wall_size = TILE_SIZE - WALL_INSET * 2

    for row_idx, row in enumerate(grid):
        for col_idx, char in enumerate(row):
            if char == TILE_STEEL:
                rect = pygame.Rect(
                    col_idx * TILE_SIZE + WALL_INSET,
                    row_idx * TILE_SIZE + WALL_INSET,
                    wall_size,
                    wall_size,
                )
                walls.append(Wall(rect=rect, wall_type=WallType.STEEL))
            elif char == TILE_BRICK:
                rect = pygame.Rect(
                    col_idx * TILE_SIZE + WALL_INSET,
                    row_idx * TILE_SIZE + WALL_INSET,
                    wall_size,
                    wall_size,
                )
                walls.append(Wall(rect=rect, wall_type=WallType.BRICK))
            elif char == TILE_SPAWN_P1:
                spawn_p1 = _tile_center(row_idx, col_idx)
            elif char == TILE_SPAWN_P2:
                spawn_p2 = _tile_center(row_idx, col_idx)

    return walls, spawn_p1, spawn_p2


def get_open_tiles(grid: list[str]) -> list[pygame.Vector2]:
    """Return center positions of all open (non-wall, non-spawn) tiles."""
    open_tiles: list[pygame.Vector2] = []
    for row_idx, row in enumerate(grid):
        for col_idx, char in enumerate(row):
            # Only include completely open tiles, excluding bricks and spawn points
            if char == TILE_OPEN:
                open_tiles.append(_tile_center(row_idx, col_idx))
    return open_tiles


# ---------------------------------------------------------------------------
# Map Registry — Single Source of Truth
# ---------------------------------------------------------------------------

class MapRegistry:
    """Manages all available maps in the game.

    """

    # Starts empty; populated by register_map() at module parse time.
    _maps: dict[str, MapData] = {}

    @classmethod
    def get_map(cls, name: str) -> MapData | None:
        """Get a map by its name (case-insensitive)."""
        return cls._maps.get(name.lower())

    @classmethod
    def get_all_maps(cls) -> list[MapData]:
        """Get all available maps in registration order."""
        return list(cls._maps.values())

    @classmethod
    def get_map_names(cls) -> list[str]:
        """Get all map keys in registration order."""
        return list(cls._maps.keys())

    @classmethod
    def add_map(cls, key: str, map_data: MapData) -> None:
        """Register a map. Called automatically by register_map()."""
        cls._maps[key.lower()] = map_data

    @classmethod
    def get_map_by_index(cls, index: int) -> MapData | None:
        """Get a map by its insertion index."""
        maps = cls.get_all_maps()
        if 0 <= index < len(maps):
            return maps[index]
        return None


# Auto-Registration Helper

# ALL_MAPS is populated by register_map() at import time.
# It stays in sync with MapRegistry automatically — no manual updates required.
ALL_MAPS: list[MapData] = []


def register_map(map_data: MapData) -> MapData:
    """Register a MapData instance with MapRegistry and the ALL_MAPS list.

    Call this immediately after defining a new map constant::

        MAP_DESERT = MapData(name="Desert", grid=[...])
        register_map(MAP_DESERT)

    Adding that single call is the *only* step needed to make a new map appear
    in the map selection screen. No other file needs to be modified.

    Returns the same MapData object unchanged (for chaining convenience).
    """
    MapRegistry.add_map(map_data.name.lower(), map_data)
    ALL_MAPS.append(map_data)
    return map_data


# ---------------------------------------------------------------------------
# Map Definitions
# ---------------------------------------------------------------------------

MAP_CLASSIC = register_map(MapData(
    name="Classic",
    description="A sprawling maze \u2014 master the corridors",
    grid=[
        "########################",
        "#1.####....##....####..#",
        "#..#..#....##....#..#..#",
        "#.......##.##...##..#..#",
        "#..##.....#..#......#..#",
        "#...#....#....#....##..#",
        "#.........##..#........#",
        "###.##........#.##.##..#",
        "#..#.##..........#..#..#",
        "#..#.........#......#..#",
        "#..####..#...##....##..#",
        "###....#.............#.#",
        "###.##.#..##....##...#.#",
        "#....#.....##....##..2.#",
        "#....####.........##...#",
        "########################",
    ],
))

MAP_FORTRESS = register_map(MapData(
    name="Fortress",
    description="Brick bastions divide every lane",
    grid=[
        "########################",
        "#1.....#........#......#",
        "#.BBB..#..BBBB..#.BBB..#",
        "#.B....#........#...B..#",
        "#.B..#....####....#.B..#",
        "#....#....#..#....#....#",
        "#.BB.......BB.......BB.#",
        "#..........##..........#",
        "#..........##..........#",
        "#.BB.......BB.......BB.#",
        "#....#....#..#....#....#",
        "#.B..#....####....#.B..#",
        "#.B....#........#...B..#",
        "#.BBB..#..BBBB..#.BBB..#",
        "#.....#........#.....2.#",
        "########################",
    ],
))

MAP_ARENA = register_map(MapData(
    name="Arena",
    description="Open ground \u2014 nowhere to hide",
    grid=[
        "########################",
        "#1....................2#",
        "#..BBB..........BBB....#",
        "#..B..B........B..B....#",
        "#..BBB...BBBB...BBB....#",
        "#........B..B..........#",
        "#..##....BBBB....##....#",
        "#..##..............##..#",
        "#..##..............##..#",
        "#..##....BBBB....##....#",
        "#........B..B..........#",
        "#..BBB...BBBB...BBB....#",
        "#..B..B........B..B....#",
        "#..BBB..........BBB....#",
        "#......................#",
        "########################",
    ],
))

MAP_OPEN = register_map(MapData(
    name="Open Field",
    description="Wide open spaces \u2014 no cover at all",
    grid=[
        "########################",
        "#1.....................#",
        "#......................#",
        "#......................#",
        "#......####....####....#",
        "#......#..#....#..#....#",
        "#......####....####....#",
        "#......................#",
        "#......................#",
        "#......####....####....#",
        "#......#..#....#..#....#",
        "#......####....####....#",
        "#......................#",
        "#......................#",
        "#.....................2#",
        "########################",
    ],
))