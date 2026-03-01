"""Stable import facade for map-related symbols.

External modules (e.g. state.py) should import from here, not directly from
maps.py. This keeps the public API stable even if the internal implementation
of maps.py changes.

Individual map constants (MAP_CLASSIC, MAP_FORTRESS, MAP_ARENA) are
implementation details of maps.py and are intentionally NOT exported here.
Use ALL_MAPS or MapRegistry if you need to enumerate / look up maps.
"""
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
