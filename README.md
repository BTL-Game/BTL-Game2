# Tank Battle: Chaos Maze

A two-player local multiplayer tank battle game built with Python and Pygame. Two players share a keyboard and fight through hand-crafted mazes — collecting coins, grabbing power-ups, and bouncing bullets off walls to outlast the other.

---

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Controls](#controls)
- [Gameplay Mechanics](#gameplay-mechanics)
- [Physics Implementation](#physics-implementation)
- [Maps](#maps)
- [Code Structure](#code-structure)
- [Asset Credits](#asset-credits)
- [Presentation](#presentation)

---

## Features

- **Local 2-player split-keyboard** multiplayer — no network required
- **3 hand-crafted maze maps** to choose from at the start of every match
- **Bouncing bullets** — projectiles reflect off walls up to 5 times using real vector reflection math
- **Destructible brick walls** — two hits crumble them, opening up new paths mid-match
- **Independent turret rotation** — aim separately from the direction you're moving
- **Triple-shot mode** — fires three bullets in a spread pattern simultaneously
- **Food/coin collection** scoring system — first to 30 points wins the match
- **Three power-ups** randomly spawned on the map: Speed Boost, Shield, and Triple Shot
- **Particle effects** on tank destruction
- **Sound effects and looping background music** with in-game volume controls
- **Pause menu** accessible at any point during play

---

## Quick Start


**Requirements:** Python 3.10+ and `pip`.

```bash
# 1. Clone or download the repo, then create a virtual environment
python -m venv .venv

# 2. Activate it
# On Linux / macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the game
python src/main.py
```

---

## Controls

### Player 1 — Blue Tank

| Action | Key |
|---|---|
| Move Forward | `W` |
| Move Backward | `S` |
| Rotate Left | `A` |
| Rotate Right | `D` |
| Rotate Turret Left | `Q` |
| Rotate Turret Right | `E` |
| Fire | `Space` or `F` |

### Player 2 — Red Tank

| Action | Key |
|---|---|
| Move Forward | `↑` |
| Move Backward | `↓` |
| Rotate Left | `←` |
| Rotate Right | `→` |
| Rotate Turret Left | `N` |
| Rotate Turret Right | `,` |
| Fire | `Enter` or `M` |

### General

| Action | Key |
|---|---|
| Pause / Resume | `Esc` |

> **Tip:** The tank body and turret rotate independently. You can strafe around a corner while keeping your turret aimed at the enemy.

---

## Gameplay Mechanics

### Scoring & Win Condition
Players earn points by driving over **coin pickups** scattered across the map. The first player to reach **30 points** wins the overall match. Coins respawn in waves every 6 seconds, keeping the pressure on throughout.

### Health & Combat
Each tank starts with **3 health points**. A direct bullet hit removes 1 HP. When a tank's HP reaches zero, a round ends. Multi-round matches track wins per player.

### Bullet Rules
- Each player can have at most **5 bullets** in play at once.
- There is a **0.25-second cooldown** between shots.
- Bullets are removed after leaving the screen boundary **or** bouncing **5 times**.
- Bullets cannot hit their own owner.

### Power-Ups

| Icon | Type | Effect | Duration |
|---|---|---|---|
| 🟢 Speed Boost | Speed | 1.5x movement speed | 5 seconds |
| 🔵 Shield | Shield | Absorbs the next bullet hit | 8 seconds |
| 🟡 Triple Shot | Triple | Fires 3 bullets in a 15 degree spread | 6 seconds |

Power-ups spawn randomly on open tiles every 8 seconds, up to a maximum of 2 on the map at once.

### Wall Types
- **Steel walls** (`#`) — Indestructible. Bullets and tanks bounce/stop.
- **Brick walls** (`B`) — Take 2 bullet hits to fully destroy, temporarily showing a cracked sprite after the first hit.

---

## Physics Implementation

### Vector-Based Movement
Tank movement uses standard 2D vector math. The engine keeps the tank's facing angle in degrees and derives a direction vector from it:

```python
direction = pygame.Vector2(0, -1).rotate(rotation_deg)
position += direction * speed * dt
```

This means "up" is the 0 degree reference, and rotating clockwise increases the angle — matching Pygame's coordinate system naturally.

### Bullet Reflection (Bouncing)

This is the core physics feature of the game. When a bullet collides with a wall, its velocity is **reflected** across the wall's surface normal using the standard vector reflection formula:

**v' = v - 2(v . n)n**

Where:
- **v** is the bullet's current velocity vector
- **n** is the unit normal vector of the surface that was hit
- **v'** is the resulting reflected velocity

Implemented in `src/game/physics.py`:

```python
def reflect_velocity(velocity: pygame.Vector2, normal: pygame.Vector2) -> pygame.Vector2:
    # Reflection formula: v' = v - 2 * (v dot n) * n
    return velocity - 2 * velocity.dot(normal) * normal
```

Because all walls are axis-aligned, the surface normal is always either `(±1, 0)` for vertical faces or `(0, ±1)` for horizontal faces. This is determined by comparing the **overlap depth** on each axis — whichever axis has the smaller overlap is the one the bullet is penetrating, so that axis's normal is used.

### Tank-Wall Collision Resolution

Rather than simply snapping the tank back on any collision, the engine resolves movement **axis-by-axis**. This lets tanks slide smoothly along wall surfaces instead of getting stuck on corners:

1. Apply the intended X movement. If that overlaps a wall, discard it and keep the previous X.
2. Apply the intended Y movement. If that overlaps a wall, discard it and keep the previous Y.

The same blocking check also treats the **opposing tank** as a solid obstacle, giving both tanks a physical presence.

---

## Maps

Three maps are available at the map-select screen before each match:

| Map | Description |
|---|---|
| **Classic** | An asymmetric steel maze. Complex corridors reward careful bullet ricochets. |
| **Fortress** | A symmetric layout with destructible brick walls forming inner fortifications. Walls can be blasted open. |
| **Arena** | An open arena-style map with scattered cover, favouring aggressive play. |

Each map is defined as a plain-text 2D grid in `src/game/maps.py`, making it easy to design and add new layouts.

---

## Code Structure

```
src/
├── main.py                         # Entry point — initialises Pygame and kicks off the game loop
└── game/
    ├── config.py                   # All tunable constants (speeds, sizes, timers, colours)
    ├── state.py                    # Master game state machine (title → map select → play → game over)
    ├── input.py                    # Key bindings for Player 1 and Player 2
    ├── assets.py                   # Sprite loading and scaling from the assets/ folder
    ├── maps.py                     # Map grid definitions and tile-to-pixel conversion
    ├── levels.py                   # Re-exports map utilities (backwards compatibility)
    ├── physics.py                  # Core physics helpers: reflect_velocity, aabb_overlap, clamp
    ├── ui.py                       # HUD, title screen, pause menu, countdown, game-over screens
    ├── entities/
    │   ├── tank.py                 # Tank dataclass: movement, power-up tracking, damage
    │   ├── bullet.py               # Bullet dataclass: position, velocity, bounce counter
    │   ├── wall.py                 # Wall dataclass: type (steel/brick) and destruction state
    │   ├── food.py                 # Coin/food pickup dataclass
    │   └── powerup.py              # Power-up dataclass and PowerUpType enum
    └── managers/
        ├── bullet_manager.py       # Bullet lifecycle: spawn, movement, wall reflection, hit detection
        ├── collision_manager.py    # Tank–wall and tank–tank collision resolution
        ├── food_manager.py         # Food spawning, wave escalation, pickup detection
        ├── powerup_manager.py      # Power-up spawning and pickup detection
        ├── particle_manager.py     # Explosion particle system
        └── sound_manager.py        # SFX and background music, with volume control
```

---

## Asset Credits

All external assets used in this project are listed below.

### Sprites

| Asset | File(s) 
|---|---|
| Blue Tank Body | `assets/Blue/Bodies/body_tracks.png` 
| Red Tank Body | `assets/Red/Bodies/body_tracks.png` 
| Blue Tank Turret | `assets/Blue/Weapons/weapon.png` 
| Red Tank Turret | `assets/Red/Weapons/weapon.png` 
| Shoot Flash (Blue/Red) | `assets/*/Weapons/shoot.png` 
| Explosion (Blue/Red) | `assets/*/Bodies/*explosion.png` 
| Wall Sprites (Steel/Brick) | `assets/Wall/*.png` 
| Coin (Food) | `assets/Food/coin.png` 
| Power-up Icons | `assets/Food/speed.png`, `shield.png`, `tripple.png` 
| Background | `assets/Background/background.png` 

### Audio

| Asset | File
|---|---|
| Shoot SFX | `assets/sounds/shoot.wav` 
| Bounce SFX | `assets/sounds/bounce.wav` 
| Explosion SFX | `assets/sounds/explosion.wav` 
| Power-up SFX | `assets/sounds/powerup.wav` 
| Background Music | `assets/sounds/backgroundmusic.mp3` 

> If you know the exact source URL for any asset, please open an issue or PR to update this table.

---

## Presentation

### Gameplay Demo

<video src="assets/demo.webm" controls autoplay loop muted style="max-width: 100%;"></video>


---

### Collision Code Breakdown

The two most important collision systems are **bullet–wall reflection** and **tank–wall resolution**. Here is the code for each with a plain-language walkthrough.

#### 1. Determining the Bounce Normal

When a bullet's bounding box overlaps a wall's bounding box, we need to figure out *which face* was hit so the reflection points in the right direction.

```python
@staticmethod
def _collision_normal(bullet: pygame.Rect, wall: pygame.Rect) -> tuple[pygame.Vector2, float]:
    overlap_x = min(bullet.right - wall.left, wall.right - bullet.left)
    overlap_y = min(bullet.bottom - wall.top, wall.bottom - bullet.top)

    if overlap_x < overlap_y:
        normal = pygame.Vector2(-1, 0) if bullet.centerx < wall.centerx else pygame.Vector2(1, 0)
        return normal, overlap_x

    normal = pygame.Vector2(0, -1) if bullet.centery < wall.centery else pygame.Vector2(0, 1)
    return normal, overlap_y
```

**Step-by-step:**

1. **Calculate the overlap on each axis.** `overlap_x` is how many pixels the two rectangles overlap horizontally; `overlap_y` is the vertical overlap.
2. **The smaller overlap tells us which face was hit.** A bullet moving mostly sideways into a vertical wall will have a tiny horizontal overlap but a large vertical one. The minimum-overlap axis is the one the bullet just crossed.
3. **Pick the outward normal.** If the horizontal overlap is smaller, the bullet hit either the left or right face — the normal points away from the wall's center on that axis. Same logic applies vertically.
4. **Return the normal and overlap depth.** The overlap value is used to push the bullet back out so it doesn't pass through the wall on the next frame.

#### 2. Applying the Reflection

```python
def reflect_velocity(velocity: pygame.Vector2, normal: pygame.Vector2) -> pygame.Vector2:
    # v' = v - 2 * (v . n) * n
    return velocity - 2 * velocity.dot(normal) * normal
```

**Step-by-step:**

1. **Compute the dot product** `v . n`. This gives a scalar representing how much of the bullet's velocity is pointing *into* the wall (the perpendicular component).
2. **Scale the normal** by twice that value: `2 * (v . n) * n`. This is the exact portion of velocity that needs to be flipped.
3. **Subtract from the original velocity.** The component that runs *parallel* to the wall surface is unchanged; only the perpendicular component is reversed. The angle of incidence equals the angle of reflection — a perfect elastic bounce.

#### 3. Tank Sliding Along Walls

```python
@staticmethod
def resolve_tank_walls(tank_position, previous_position, walls, other_tank_rect=None):
    half = TANK_SIZE / 2

    def _blocked(rect):
        if any(wall.rect.colliderect(rect) for wall in walls if not wall.is_destroyed):
            return True
        if other_tank_rect is not None and other_tank_rect.colliderect(rect):
            return True
        return False

    # Step 1: test X-axis movement only
    test_x = pygame.Vector2(tank_position.x, previous_position.y)
    test_x.x = clamp(test_x.x, half, SCREEN_WIDTH - half)
    if _blocked(_tank_rect(test_x)):
        test_x.x = previous_position.x   # blocked — revert X

    # Step 2: test Y-axis movement only
    test_y = pygame.Vector2(test_x.x, tank_position.y)
    test_y.y = clamp(test_y.y, half, SCREEN_HEIGHT - half)
    if _blocked(_tank_rect(test_y)):
        test_y.y = previous_position.y   # blocked — revert Y

    return test_y
```

**Step-by-step:**

1. **Test X movement in isolation.** Build a candidate position using the new X coordinate but the *previous* Y coordinate.
2. **If blocked, revert X only.** The tank can't move horizontally, but Y is still unrestricted at this point.
3. **Test Y movement** using the X result from the previous step and the new Y coordinate.
4. **If blocked, revert Y only.** Each axis is resolved independently, so the tank slides smoothly along wall surfaces instead of stopping dead on diagonal contact.
5. **Screen-boundary clamping** is applied before each check to keep tanks within the play area.
