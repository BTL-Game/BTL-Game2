from __future__ import annotations

from dataclasses import dataclass

from game.config import TILE_SIZE


DEFAULT_LEVEL = [
    "########################",
    "#..####....##....####..#",
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
    "#....#.....##....##....#",
    "#....####.........##...#",
    "########################",
]


@dataclass
class Tile:
    x: int
    y: int
    solid: bool


def build_tiles(level: list[str]) -> list[Tile]:
    tiles: list[Tile] = []
    for row_index, row in enumerate(level):
        for col_index, char in enumerate(row):
            if char == "#":
                tiles.append(Tile(col_index * TILE_SIZE, row_index * TILE_SIZE, True))
    return tiles
