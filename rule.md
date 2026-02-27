# Project Plan: Game Feature Overhaul (PLAN-game-overhaul)

## Phase 1: Context Analysis (The "Why")
- **Target User:** Players of the Tank Battle game.
- **Problem Statement:** The game needs better UI/UX (Main Menu, Pause Menu, and active Powerups HUD) to improve navigation and aesthetics (Sci-Fi theme). The "food" entity visual size is incorrect according to the design criteria. Furthermore, tanks currently overlap each other; they need solid collision.
- **Goal:** Implement entity scaling, menu expansions, sci-fi HUD improvements for powerups, and tank-to-tank collisions while adhering to SOLID principles and keeping modifications minimal.

## Phase 2: Requirement Definition (The "What")
- **Entity Resizing:** The food sprite (`coin.png`) must be resized to exactly half of a standard wall tile (`TILE_SIZE / 2`).
- **Main Menu Overhaul:** Redesign the initial `/home` menu with a Sci-Fi aesthetic (neon colors, glowing text, space themes). Add a "Settings" button to allow changing SFX and Music volume.
- **In-Game Menu Expansion:** The pause menu currently has SFX and Music Volume. Add a new "Return to Main Menu" option that cleanly exits the current session.
- **Powerups Sci-Fi HUD:** When a powerup (like Shield, Speed, or Triple) is active, display its effect using a best-in-class Sci-Fi UI design (e.g., stylized progress bars, glowing icons, or futuristic gauges) rather than plain text. 
- **Tank-to-Tank Collision:** Prevent tanks from overlapping. They should block each other like solid walls.

## Phase 3: Technical Blueprint (The "How")
- **Architecture:** We will leverage the existing State pattern in `GameState`, collision logic in `CollisionManager`, and UI rendering in `ui.py`.
- **Modifications:**
  - `src/game/config.py`: Update `FOOD_SIZE`.
  - `src/game/state.py`: Update `GameState` logic to handle new menu states, "Return to Main Menu" inputs, and pass the other tank's position to the collision manager.
  - `src/game/managers/collision_manager.py`: Update collision logic to handle circular or AABB tank-to-tank block resolution.
  - `src/game/ui.py`: Revamp `draw_title_screen`, `draw_pause_menu`, and replace `_powerup_text` with graphical, sci-fi rendering logic.

## Phase 4: Task Orchestration (The "Plan")

### Task 1: Update Food Entity Resizing
- **File:** `src/game/config.py`
- **Action:** Modify `FOOD_SIZE` to cleanly equal `TILE_SIZE // 2` (which evaluates to 20 instead of 16).
- **Verify:** Run the game and visually confirm the food item is exactly half the size of the 40x40 wall tile.

### Task 2: In-Game Menu Expansion (Return to Home)
- **File:** `src/game/state.py`
- **Action:** In `_update_pause_menu()`, enhance the `selection` variable to navigate 3 items: 0 = SFX, 1 = Music, 2 = Return to Main Menu. Add an event listener for `pygame.K_RETURN` or `pygame.K_SPACE` to change `self.mode = "title"` when `selection == 2`.
- **File:** `src/game/ui.py`
- **Action:** In `draw_pause_menu()`, add the "Return to Main Menu" button to the existing volume layout, highlighting it dynamically based on the current selection.

### Task 3: Main Menu UI/UX Overhaul (Sci-Fi Aesthetic & Settings)
- **File:** `src/game/state.py`
- **Action:** 
  1. Add a `self._title_selection = 0` (0: Play, 1: Settings) to `GameState`.
  2. Modify `update()` inside `self.mode == "title"` to accept Arrow Keys for selection and Enter for confirmation. 
  3. If "Settings" is selected, transition to the pause menu settings logic.
- **File:** `src/game/ui.py`
- **Action:** Revamp `draw_title_screen()`:
  1. Use modern, sci-fi colors (e.g., Cyberpunk Cyan/Magenta or Neon Blue).
  2. Implement an animated/glowing header or stylized borders if possible.
  3. Render the interactive `Play` and `Settings` menu buttons.

### Task 4: Sci-Fi Powerup HUD
- **File:** `src/game/ui.py`
- **Action:** Remove the basic string rendering (`_powerup_text`) inside `draw_hud()`. Replace it with a function like `_draw_powerup_ui()` that renders sleek, glowing progress bars or circular cooldown dials for each active powerup over the tank's UI area, utilizing Sci-Fi styling (neon borders, futuristic fonts, translucent backgrounds).

### Task 5: Tank-to-Tank Collision
- **File:** `src/game/managers/collision_manager.py`
- **Action:** Update or add a method `resolve_tank_tank(tank1_pos, tank1_prev, tank2_rect)` or similar, which treats the opposing tank as a solid obstacle during movement resolution.
- **File:** `src/game/state.py`
- **Action:** Inside `_handle_tank_input()`, fetch the bounding box or position of the opponent tank and feed it into the CollisionManager to halt movement if intersecting.
- **Verify:** Drive Player 1 into Player 2 and verify they collide as solid objects and cannot overlap.
