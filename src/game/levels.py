"""Import facade for map symbols (MapData, build_walls, get_open_tiles, ALL_MAPS)."""
from game.maps import (
    MapData,
    build_walls,
    get_open_tiles,
    ALL_MAPS,
    MapRegistry,
    register_map,
)

__all__ = [
    "MapData",
    "build_walls",
    "get_open_tiles",
    "ALL_MAPS",
    "MapRegistry",
    "register_map",
]
