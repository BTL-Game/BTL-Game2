from __future__ import annotations

import pygame

from game.config import (
    BG_COLOR,
    HUD_COLOR,
    PLAYER1_COLOR,
    PLAYER2_COLOR,
    POWERUP_COLORS,
    SCORE_LIMIT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WALL_COLOR,
)
from game.entities.powerup import PowerUpType
from game.entities.tank import Tank


# ── Font cache (avoid re-creating every frame) ───────────────────────────

_fonts: dict[str, pygame.font.Font] = {}


def _font(name: str, size: int, bold: bool = False) -> pygame.font.Font:
    key = f"{name}_{size}_{'bold' if bold else 'normal'}"
    if key not in _fonts:
        _fonts[key] = pygame.font.SysFont(name, size, bold=bold)
    return _fonts[key]


# ══════════════════════════════════════════════════════════════════════════
# Screens
# ══════════════════════════════════════════════════════════════════════════

def draw_title_screen(screen: pygame.Surface) -> None:
    title = _font("arial", 42).render("Tank Battle: Chaos Maze", True, (235, 235, 235))
    sub = _font("arial", 20).render("Press Enter or Space to start", True, (180, 180, 180))

    cx, cy = screen.get_rect().center
    screen.blit(title, title.get_rect(center=(cx, cy - 30)))
    screen.blit(sub, sub.get_rect(center=(cx, cy + 20)))

    # Controls hint
    hint_font = _font("arial", 14)
    hints = [
        "P1: WASD move | Q/E turret | Space/F fire",
        "P2: Arrows move | N/Comma turret | Enter/M fire",
    ]
    for i, h in enumerate(hints):
        surf = hint_font.render(h, True, (140, 140, 140))
        screen.blit(surf, surf.get_rect(center=(cx, cy + 60 + i * 22)))


def draw_map_select(screen: pygame.Surface, maps, selected_index: int) -> None:
    title = _font("arial", 32).render("Select Map", True, HUD_COLOR)
    cx, cy = screen.get_rect().center
    screen.blit(title, title.get_rect(center=(cx, cy - 100)))

    prompt = _font("arial", 16).render("← → to browse  |  Enter to confirm", True, (160, 160, 160))
    screen.blit(prompt, prompt.get_rect(center=(cx, cy - 60)))

    # Map cards
    card_width = 180
    total_width = len(maps) * card_width + (len(maps) - 1) * 20
    start_x = cx - total_width // 2

    for i, m in enumerate(maps):
        x = start_x + i * (card_width + 20)
        y = cy - 20
        is_selected = i == selected_index

        # Card background
        card_color = (60, 70, 90) if is_selected else (35, 35, 40)
        border_color = (100, 180, 255) if is_selected else (60, 60, 70)
        card_rect = pygame.Rect(x, y, card_width, 120)
        pygame.draw.rect(screen, card_color, card_rect, border_radius=8)
        pygame.draw.rect(screen, border_color, card_rect, 2, border_radius=8)

        # Map name
        name_surf = _font("arial", 20).render(m.name, True, (235, 235, 235) if is_selected else (160, 160, 160))
        screen.blit(name_surf, name_surf.get_rect(center=(x + card_width // 2, y + 30)))

        # Mini preview (tiny grid)
        _draw_mini_map(screen, m.grid, x + 30, y + 50, card_width - 60, 55)


def _draw_mini_map(screen: pygame.Surface, grid: list[str], x: int, y: int, w: int, h: int) -> None:
    rows = len(grid)
    cols = max(len(r) for r in grid) if grid else 1
    cell_w = max(1, w // cols)
    cell_h = max(1, h // rows)

    for ri, row in enumerate(grid):
        for ci, ch in enumerate(row):
            px = x + ci * cell_w
            py = y + ri * cell_h
            if ch == "#":
                pygame.draw.rect(screen, (80, 80, 90), (px, py, cell_w, cell_h))
            elif ch == "B":
                pygame.draw.rect(screen, (130, 80, 40), (px, py, cell_w, cell_h))
            elif ch == "1":
                pygame.draw.rect(screen, PLAYER1_COLOR, (px, py, cell_w, cell_h))
            elif ch == "2":
                pygame.draw.rect(screen, PLAYER2_COLOR, (px, py, cell_w, cell_h))


# ── In-game HUD ──────────────────────────────────────────────────────────

def draw_hud(screen: pygame.Surface, p1: Tank, p2: Tank, scores: dict[int, int], round_num: int, round_wins: dict[int, int]) -> None:
    font = _font("arial", 18, bold=True)
    small = _font("arial", 14)

    # P1 info (left)
    p1_text = f"P1  HP: {p1.health}  Score: {scores[1]}/{SCORE_LIMIT}"
    left = font.render(p1_text, True, HUD_COLOR)
    left_rect = left.get_rect(topleft=(12, 8))
    pygame.draw.rect(screen, BG_COLOR, left_rect.inflate(8, 6))
    screen.blit(left, left_rect)

    # P1 active power-ups
    p1_pups = _powerup_text(p1)
    if p1_pups:
        pup_surf = small.render(p1_pups, True, (180, 220, 180))
        screen.blit(pup_surf, (12, 28))

    # P2 info (right)
    p2_text = f"P2  HP: {p2.health}  Score: {scores[2]}/{SCORE_LIMIT}"
    right = font.render(p2_text, True, HUD_COLOR)
    right_rect = right.get_rect(topright=(screen.get_width() - 12, 8))
    pygame.draw.rect(screen, BG_COLOR, right_rect.inflate(8, 6))
    screen.blit(right, right_rect)

    # P2 active power-ups
    p2_pups = _powerup_text(p2)
    if p2_pups:
        pup_surf = small.render(p2_pups, True, (180, 220, 180))
        pup_rect = pup_surf.get_rect(topright=(screen.get_width() - 12, 28))
        screen.blit(pup_surf, pup_rect)

    # Round info (center top) with win counters on either side
    round_font = _font("arial", 22, bold=True)
    round_surf = round_font.render(f"Round {round_num}", True, HUD_COLOR)
    round_rect = round_surf.get_rect(midtop=(screen.get_width() // 2, 8))
    pygame.draw.rect(screen, BG_COLOR, round_rect.inflate(8, 6))
    screen.blit(round_surf, round_rect)
    
    # P1 round wins (left of Round text, blue)
    win_font = _font("arial", 24)
    p1_wins_surf = win_font.render(str(round_wins[1]), True, PLAYER1_COLOR)
    p1_wins_rect = p1_wins_surf.get_rect(midright=(round_rect.left - 20, round_rect.centery))
    pygame.draw.rect(screen, BG_COLOR, p1_wins_rect.inflate(8, 6))
    screen.blit(p1_wins_surf, p1_wins_rect)
    
    # P2 round wins (right of Round text, red)
    p2_wins_surf = win_font.render(str(round_wins[2]), True, PLAYER2_COLOR)
    p2_wins_rect = p2_wins_surf.get_rect(midleft=(round_rect.right + 20, round_rect.centery))
    pygame.draw.rect(screen, BG_COLOR, p2_wins_rect.inflate(8, 6))
    screen.blit(p2_wins_surf, p2_wins_rect)


def _powerup_text(tank: Tank) -> str:
    names = {PowerUpType.SPEED: "⚡SPD", PowerUpType.SHIELD: "🛡SHD", PowerUpType.TRIPLE: "🔱TRI"}
    parts = []
    for ptype, remaining in tank.active_powerups.items():
        label = names.get(ptype, ptype.value)
        parts.append(f"{label} {remaining:.1f}s")
    return "  ".join(parts)


# ── Overlay screens ──────────────────────────────────────────────────────

def draw_game_over(screen: pygame.Surface, winner_text: str, info_text: str = "") -> None:
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    screen.blit(overlay, (0, 0))

    cx, cy = screen.get_rect().center
    title = _font("arial", 32).render(winner_text, True, HUD_COLOR)
    screen.blit(title, title.get_rect(center=(cx, cy - 30)))

    if info_text:
        info = _font("arial", 18).render(info_text, True, (200, 200, 200))
        screen.blit(info, info.get_rect(center=(cx, cy + 10)))

    prompt = _font("arial", 18).render("Press Enter or Space to continue", True, (160, 160, 160))
    screen.blit(prompt, prompt.get_rect(center=(cx, cy + 45)))


def draw_match_winner(screen: pygame.Surface, winner_id: int, scores: dict[int, int]) -> None:
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    cx, cy = screen.get_rect().center
    color = PLAYER1_COLOR if winner_id == 1 else PLAYER2_COLOR

    title = _font("arial", 40).render(f"🏆 Player {winner_id} Wins the Match!", True, color)
    screen.blit(title, title.get_rect(center=(cx, cy - 40)))

    score_text = f"Final Score  —  P1: {scores[1]}  |  P2: {scores[2]}"
    score_surf = _font("arial", 22).render(score_text, True, HUD_COLOR)
    screen.blit(score_surf, score_surf.get_rect(center=(cx, cy + 10)))

    prompt = _font("arial", 18).render("Press Enter or Space to return to title", True, (160, 160, 160))
    screen.blit(prompt, prompt.get_rect(center=(cx, cy + 50)))


def draw_pause_menu(screen: pygame.Surface, selection: int, sfx_volume: float, music_volume: float) -> None:
    """Draw pause/options menu overlay with volume controls."""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    cx, cy = screen.get_rect().center

    title = _font("arial", 36).render("PAUSED", True, HUD_COLOR)
    screen.blit(title, title.get_rect(center=(cx, cy - 80)))

    # Volume controls
    option_font = _font("arial", 20)
    value_font = _font("arial", 18)
    
    # SFX Volume
    sfx_y = cy - 20
    sfx_color = (100, 180, 255) if selection == 0 else (180, 180, 180)
    sfx_text = option_font.render("SFX Volume", True, sfx_color)
    screen.blit(sfx_text, sfx_text.get_rect(midright=(cx - 20, sfx_y)))
    
    # SFX volume bar
    bar_width = 200
    bar_height = 20
    bar_x = cx + 10
    bar_y = sfx_y - bar_height // 2
    
    # Background bar
    pygame.draw.rect(screen, (60, 60, 70), (bar_x, bar_y, bar_width, bar_height), border_radius=4)
    # Filled bar
    filled_width = int(bar_width * sfx_volume)
    if filled_width > 0:
        pygame.draw.rect(screen, (100, 180, 255), (bar_x, bar_y, filled_width, bar_height), border_radius=4)
    # Border
    pygame.draw.rect(screen, sfx_color, (bar_x, bar_y, bar_width, bar_height), 2, border_radius=4)
    
    # SFX percentage
    sfx_pct = value_font.render(f"{int(sfx_volume * 100)}", True, sfx_color)
    screen.blit(sfx_pct, sfx_pct.get_rect(midleft=(bar_x + bar_width + 10, sfx_y)))
    
    # Music Volume
    music_y = cy + 30
    music_color = (100, 180, 255) if selection == 1 else (180, 180, 180)
    music_text = option_font.render("Music Volume", True, music_color)
    screen.blit(music_text, music_text.get_rect(midright=(cx - 20, music_y)))
    
    # Music volume bar
    bar_y = music_y - bar_height // 2
    
    # Background bar
    pygame.draw.rect(screen, (60, 60, 70), (bar_x, bar_y, bar_width, bar_height), border_radius=4)
    # Filled bar
    filled_width = int(bar_width * music_volume)
    if filled_width > 0:
        pygame.draw.rect(screen, (100, 180, 255), (bar_x, bar_y, filled_width, bar_height), border_radius=4)
    # Border
    pygame.draw.rect(screen, music_color, (bar_x, bar_y, bar_width, bar_height), 2, border_radius=4)
    
    # Music percentage
    music_pct = value_font.render(f"{int(music_volume * 100)}", True, music_color)
    screen.blit(music_pct, music_pct.get_rect(midleft=(bar_x + bar_width + 10, music_y)))

    # Instructions
    hint_font = _font("arial", 14)
    hints = [
        "↑↓ / WS: Select   ←→ / AD: Adjust",
        "ESC: Resume Game"
    ]
    for i, hint in enumerate(hints):
        hint_surf = hint_font.render(hint, True, (140, 140, 140))
        screen.blit(hint_surf, hint_surf.get_rect(center=(cx, cy + 90 + i * 20)))


def draw_countdown(screen: pygame.Surface, time_left: float) -> None:
    """Draw countdown overlay (3-2-1) in center of screen."""
    # Semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 100))
    screen.blit(overlay, (0, 0))

    cx, cy = screen.get_rect().center
    
    # Calculate which number to show (3, 2, 1)
    if time_left > 2.0:
        number = "3"
        color = (255, 100, 100)  # Red
    elif time_left > 1.0:
        number = "2"
        color = (255, 200, 100)  # Orange
    else:
        number = "1"
        color = (100, 255, 100)  # Green
    
    # Large countdown number
    countdown_font = _font("arial", 120)
    countdown_surf = countdown_font.render(number, True, color)
    screen.blit(countdown_surf, countdown_surf.get_rect(center=(cx, cy)))
    
    # "Get Ready!" text above the number
    ready_font = _font("arial", 32)
    ready_surf = ready_font.render("Get Ready!", True, (235, 235, 235))
    screen.blit(ready_surf, ready_surf.get_rect(center=(cx, cy - 100)))

