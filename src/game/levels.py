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


# ---------------------------------------------------------------------------
# Map data structure
# ---------------------------------------------------------------------------

@dataclass
class MapData:
    name: str
    grid: list[str]
    spawn_p1: pygame.Vector2 = field(default_factory=lambda: pygame.Vector2(0, 0))
    spawn_p2: pygame.Vector2 = field(default_factory=lambda: pygame.Vector2(0, 0))


# ---------------------------------------------------------------------------
# Helper: parse grid into walls + spawn positions
# ---------------------------------------------------------------------------

def _tile_center(row: int, col: int) -> pygame.Vector2:
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
            # Only include completely open tiles, exclude bricks and spawn points
            if char == TILE_OPEN:
                open_tiles.append(_tile_center(row_idx, col_idx))
    return open_tiles


# ---------------------------------------------------------------------------
# Named Maps
# ---------------------------------------------------------------------------

MAP_CLASSIC = MapData(
    name="Classic",
    grid=[
        "########################",
        "#1.####....##....####..#",
        "#..#..#....##....#..#..#",
        "#.......##.##...##..#..#",
        "#..##.....#..#......#..#",
        "#...#....#....#....##..#",
        "#.........##..#......#.#",
        "###.##........#.##.##.##",
        "#..#.##..........#..#..#",
        "#..#.........#......#..#",
        "#..####..#...##....##..#",
        "###....#.............#.#",
        "###.##.#..##....##...#.#",
        "#....#.....##....##..2.#",
        "#....####.........##...#",
        "########################",
    ],
)

MAP_FORTRESS = MapData(
    name="Fortress",
    grid=[
        "########################",
        "#1.....#........#.....#",
        "#.BBB..#..BBBB..#.BBB.#",
        "#.B....#........#...B.#",
        "#.B..#....####....#.B.#",
        "#....#....#..#....#...#",
        "#.BB.......BB.......BB#",
        "#..........##.........#",
        "#..........##.........#",
        "#.BB.......BB.......BB#",
        "#....#....#..#....#...#",
        "#.B..#....####....#.B.#",
        "#.B....#........#...B.#",
        "#.BBB..#..BBBB..#.BBB.#",
        "#.....#........#.....2#",
        "########################",
    ],
)

MAP_ARENA = MapData(
    name="Arena",
    grid=[
        "########################",
        "#1....................2#",
        "#..BBB..........BBB...#",
        "#..B..B........B..B...#",
        "#..BBB...BBBB...BBB...#",
        "#........B..B.........#",
        "#..##....BBBB....##...#",
        "#..##..............##.#",
        "#..##..............##.#",
        "#..##....BBBB....##...#",
        "#........B..B.........#",
        "#..BBB...BBBB...BBB...#",
        "#..B..B........B..B...#",
        "#..BBB..........BBB...#",
        "#.....................#",
        "########################",
    ],
)

ALL_MAPS: list[MapData] = [MAP_CLASSIC, MAP_FORTRESS, MAP_ARENA]
MAP_NAMES: list[str] = [m.name for m in ALL_MAPS]
