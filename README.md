# Tank Battle: Chaos Maze

Structured project scaffold based on the provided specification. This repo contains a minimal, runnable entrypoint and placeholders for assets and game systems.

## Quick Start (Python + Pygame)

1) Create and activate a virtual environment
2) Install dependencies
3) Run the game

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src\main.py
```

Or directly with venv python:

```bash
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe src\main.py
```

## Controls (Spec)

- Player 1: WASD to move/rotate, Space or F to shoot
- Player 2: Arrow keys to move/rotate, Enter or M to shoot

## Project Layout

- src/main.py: Game entrypoint
- src/game/config.py: Constants (screen, speeds, limits)
- src/game/state.py: Game state and flow (start, play, game over)
- src/game/input.py: Key mappings and input handling
- src/game/entities/: Tank, Bullet, Wall objects
- src/game/physics.py: Collision + reflection utilities
- src/game/levels.py: Maze layout from 2D grid
- src/game/ui.py: HUD and screens
- assets/: Sprites and audio (placeholders)

## Notes

- Add sprites to assets/ and update paths in src/game/assets.py
- See Tank_battle_spec.md for the full requirements list
