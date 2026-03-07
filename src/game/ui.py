from __future__ import annotations

import math
import time

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
    # UI palette
    NEON_CYAN,
    NEON_MAGENTA,
    NEON_BLUE,
    DARK_PANEL,
    PANEL_BORDER,
    # Map-select layout
    MAP_SELECT_VISIBLE_CARDS,
    MAP_CARD_W,
    MAP_CARD_H,
    MAP_CARD_GAP,
)
from game.entities.powerup import PowerUpType
from game.entities.tank import Tank


# Colour aliases (edit values in game.config, not here).
_NEON_CYAN    = NEON_CYAN
_NEON_MAGENTA = NEON_MAGENTA
_NEON_BLUE    = NEON_BLUE
_DARK_PANEL   = DARK_PANEL
_PANEL_BORDER = PANEL_BORDER


# Font cache

_fonts: dict[str, pygame.font.Font] = {}


def _font(name: str, size: int, bold: bool = False) -> pygame.font.Font:
    key = f"{name}_{size}_{'bold' if bold else 'normal'}"
    if key not in _fonts:
        _fonts[key] = pygame.font.SysFont(name, size, bold=bold)
    return _fonts[key]


# Screens

def draw_title_screen(screen: pygame.Surface, selection: int = 0) -> None:
    """Sci-fi themed main menu with Play / Settings buttons."""
    cx, cy = screen.get_rect().center
    t = time.time()

    # Background scanlines
    for y in range(0, SCREEN_HEIGHT, 4):
        alpha = int(8 + 4 * math.sin(y * 0.05 + t * 2))
        line_surf = pygame.Surface((SCREEN_WIDTH, 2), pygame.SRCALPHA)
        line_surf.fill((0, 255, 255, alpha))
        screen.blit(line_surf, (0, y))

    # Border frame
    glow_alpha = int(100 + 40 * math.sin(t * 3))
    border_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    border_color = (_NEON_CYAN[0], _NEON_CYAN[1], _NEON_CYAN[2], glow_alpha)
    pygame.draw.rect(border_surf, border_color, (20, 20, SCREEN_WIDTH - 40, SCREEN_HEIGHT - 40), 2, border_radius=12)
    screen.blit(border_surf, (0, 0))

    # Title
    title_font = _font("arial", 48, bold=True)
    title_text = "TANK BATTLE: CHAOS MAZE"
    # Glow layer
    glow_surf = title_font.render(title_text, True, _NEON_CYAN)
    glow_rect = glow_surf.get_rect(center=(cx, cy - 100))
    glow_alpha_surf = pygame.Surface(glow_surf.get_size(), pygame.SRCALPHA)
    glow_alpha_surf.blit(glow_surf, (0, 0))
    glow_alpha_surf.set_alpha(int(120 + 60 * math.sin(t * 2)))
    screen.blit(glow_alpha_surf, glow_rect.move(0, 2))
    # Main title
    title_surf = title_font.render(title_text, True, (235, 245, 255))
    screen.blit(title_surf, title_surf.get_rect(center=(cx, cy - 100)))

    # Subtitle
    sub_font = _font("arial", 16)
    sub_surf = sub_font.render("[ ENTER THE ARENA ]", True, _NEON_MAGENTA)
    sub_alpha = int(140 + 80 * math.sin(t * 4))
    sub_surf.set_alpha(sub_alpha)
    screen.blit(sub_surf, sub_surf.get_rect(center=(cx, cy - 55)))

    # Buttons
    button_labels = ["PLAY", "SETTINGS"]
    btn_font = _font("arial", 26, bold=True)
    btn_w, btn_h = 220, 48
    for i, label in enumerate(button_labels):
        bx = cx - btn_w // 2
        by = cy - 5 + i * 64
        is_sel = i == selection

        # Button panel
        panel_color = (20, 30, 50) if not is_sel else (15, 40, 70)
        pygame.draw.rect(screen, panel_color, (bx, by, btn_w, btn_h), border_radius=6)

        # Border glow
        border_c = _NEON_CYAN if is_sel else _PANEL_BORDER
        pygame.draw.rect(screen, border_c, (bx, by, btn_w, btn_h), 2, border_radius=6)

        if is_sel:
            # animated glow edges
            edge_surf = pygame.Surface((btn_w + 8, btn_h + 8), pygame.SRCALPHA)
            edge_alpha = int(60 + 30 * math.sin(t * 5))
            pygame.draw.rect(edge_surf, (_NEON_CYAN[0], _NEON_CYAN[1], _NEON_CYAN[2], edge_alpha),
                             (0, 0, btn_w + 8, btn_h + 8), 3, border_radius=8)
            screen.blit(edge_surf, (bx - 4, by - 4))

        text_color = _NEON_CYAN if is_sel else (160, 170, 190)
        lbl_surf = btn_font.render(label, True, text_color)
        screen.blit(lbl_surf, lbl_surf.get_rect(center=(cx, by + btn_h // 2)))

    # Controls hint
    hint_font = _font("arial", 13)
    hints = [
        "P1: WASD move | Q/E turret | Space/F fire",
        "P2: Arrows move | N/Comma turret | Enter/M fire",
    ]
    for i, h in enumerate(hints):
        surf = hint_font.render(h, True, (90, 100, 120))
        screen.blit(surf, surf.get_rect(center=(cx, cy + 175 + i * 20)))



def draw_map_select(screen: pygame.Surface, maps, selected_index: int) -> None:
    """Sci-fi map selection screen with animated neon cards and mini-map previews."""
    cx, cy = screen.get_rect().center
    t = time.time()

    # Background
    for scan_y in range(0, SCREEN_HEIGHT, 4):
        alpha = int(8 + 4 * math.sin(scan_y * 0.05 + t * 2))
        line_surf = pygame.Surface((SCREEN_WIDTH, 2), pygame.SRCALPHA)
        line_surf.fill((0, 255, 255, alpha))
        screen.blit(line_surf, (0, scan_y))

    # Glowing border frame
    glow_alpha = int(100 + 40 * math.sin(t * 3))
    border_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(border_surf,
                     (_NEON_CYAN[0], _NEON_CYAN[1], _NEON_CYAN[2], glow_alpha),
                     (20, 20, SCREEN_WIDTH - 40, SCREEN_HEIGHT - 40), 2, border_radius=12)
    screen.blit(border_surf, (0, 0))

    # Title
    title_font = _font("arial", 40, bold=True)
    title_text = "SELECT ARENA"
    glow_s = title_font.render(title_text, True, _NEON_CYAN)
    glow_s.set_alpha(int(110 + 55 * math.sin(t * 2)))
    screen.blit(glow_s, glow_s.get_rect(center=(cx, 60)))
    screen.blit(title_font.render(title_text, True, (230, 240, 255)),
                title_font.render(title_text, True, (230, 240, 255)).get_rect(center=(cx, 60)))

    # Subtitle tag
    tag = _font("arial", 14).render("[ ←→  NAVIGATE   ENTER  DEPLOY ]", True, _NEON_MAGENTA)
    tag.set_alpha(int(150 + 70 * math.sin(t * 4)))
    screen.blit(tag, tag.get_rect(center=(cx, 100)))

    # Map cards (sliding window)
    card_w, card_h = MAP_CARD_W, MAP_CARD_H
    gap = MAP_CARD_GAP
    n = len(maps)
    card_top = 125

    # Center window on selected card, clamped to bounds
    half = MAP_SELECT_VISIBLE_CARDS // 2
    win_start = max(0, min(selected_index - half, max(0, n - MAP_SELECT_VISIBLE_CARDS)))
    win_end   = min(n, win_start + MAP_SELECT_VISIBLE_CARDS)
    visible   = list(range(win_start, win_end))

    # Center the visible strip on screen
    total_w = len(visible) * card_w + (len(visible) - 1) * gap
    start_x = cx - total_w // 2

    for slot, map_idx in enumerate(visible):
        m = maps[map_idx]
        is_sel = map_idx == selected_index

        cx_card = start_x + slot * (card_w + gap) + card_w // 2
        card_x  = cx_card - card_w // 2
        card_y  = card_top

        # Animated card lift for selected
        if is_sel:
            card_y -= int(4 + 3 * math.sin(t * 3))

        # Card shadow
        shadow = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 80))
        screen.blit(shadow, (card_x + 4, card_y + 4))

        # Card background
        bg_color = (16, 26, 46) if is_sel else (12, 14, 22)
        pygame.draw.rect(screen, bg_color, (card_x, card_y, card_w, card_h), border_radius=10)

        # Outer neon border
        border_col = _NEON_CYAN if is_sel else _PANEL_BORDER
        pygame.draw.rect(screen, border_col, (card_x, card_y, card_w, card_h), 2, border_radius=10)

        # Selected card glow
        if is_sel:
            g_alpha = int(50 + 35 * math.sin(t * 5))
            glow_rect_surf = pygame.Surface((card_w + 12, card_h + 12), pygame.SRCALPHA)
            pygame.draw.rect(glow_rect_surf,
                             (_NEON_CYAN[0], _NEON_CYAN[1], _NEON_CYAN[2], g_alpha),
                             (0, 0, card_w + 12, card_h + 12), 3, border_radius=13)
            screen.blit(glow_rect_surf, (card_x - 6, card_y - 6))

        # Header
        header_h = 38
        header_col = (20, 50, 80) if is_sel else (18, 22, 35)
        pygame.draw.rect(screen, header_col,
                         (card_x + 2, card_y + 2, card_w - 4, header_h), border_radius=9)

        name_col = _NEON_CYAN if is_sel else (140, 155, 180)
        name_surf = _font("arial", 20, bold=True).render(m.name.upper(), True, name_col)
        screen.blit(name_surf, name_surf.get_rect(center=(cx_card, card_y + 2 + header_h // 2)))

        # Mini-map
        preview_pad = 10
        preview_x = card_x + preview_pad
        preview_y = card_y + header_h + 8
        preview_w = card_w - preview_pad * 2
        preview_h = 170
        _draw_mini_map(screen, m.grid, preview_x, preview_y, preview_w, preview_h,
                       neon=is_sel)

        # Description
        desc_col = (160, 200, 230) if is_sel else (90, 100, 120)
        desc_surf = _font("arial", 12).render(m.description, True, desc_col)
        desc_y = preview_y + preview_h + 10
        screen.blit(desc_surf, desc_surf.get_rect(center=(cx_card, desc_y)))

        # Badge
        if is_sel:
            badge_y = desc_y + 18
            badge_surf = _font("arial", 11, bold=True).render("▶  SELECTED  ◀", True, _NEON_CYAN)
            badge_surf.set_alpha(int(160 + 80 * math.sin(t * 5)))
            screen.blit(badge_surf, badge_surf.get_rect(center=(cx_card, badge_y)))

    # Navigation arrows
    arr_y = card_top + card_h // 2
    arr_font = _font("arial", 36, bold=True)
    left_arr  = arr_font.render("◀", True, _NEON_CYAN if selected_index > 0 else (40, 50, 65))
    right_arr = arr_font.render("▶", True, _NEON_CYAN if selected_index < n - 1 else (40, 50, 65))
    screen.blit(left_arr,  left_arr.get_rect(midright=(start_x - 14, arr_y)))
    screen.blit(right_arr, right_arr.get_rect(midleft=(start_x + total_w + 14, arr_y)))

    # Map index dots
    dot_y = card_top + card_h + 24
    for i in range(n):
        dot_col = _NEON_CYAN if i == selected_index else (40, 55, 75)
        dot_r   = 5 if i == selected_index else 3
        dot_x   = cx + (i - n // 2) * 20
        pygame.draw.circle(screen, dot_col, (dot_x, dot_y), dot_r)


def _draw_mini_map(screen: pygame.Surface, grid: list[str],
                   x: int, y: int, w: int, h: int,
                   neon: bool = False) -> None:
    """Render a small grid preview using sci-fi-tinted colors."""
    rows = len(grid)
    cols = max(len(r) for r in grid) if grid else 1
    cell_w = max(1, w // cols)
    cell_h = max(1, h // rows)

    # Background fill
    bg = pygame.Surface((w, h), pygame.SRCALPHA)
    bg.fill((8, 10, 18, 220))
    screen.blit(bg, (x, y))

    # Subtle grid lines
    grid_col = (25, 35, 55) if neon else (18, 22, 30)
    for ci in range(cols + 1):
        px = x + ci * cell_w
        pygame.draw.line(screen, grid_col, (px, y), (px, y + h))
    for ri in range(rows + 1):
        py = y + ri * cell_h
        pygame.draw.line(screen, grid_col, (x, py), (x + w, py))

    for ri, row in enumerate(grid):
        for ci, ch in enumerate(row):
            px = x + ci * cell_w + 1
            py = y + ri * cell_h + 1
            cw = max(1, cell_w - 1)
            ch_px = max(1, cell_h - 1)
            if ch == "#":        # steel wall
                color = (50, 65, 95) if neon else (45, 50, 65)
                pygame.draw.rect(screen, color, (px, py, cw, ch_px))
            elif ch == "B":      # brick wall
                color = (160, 80, 30) if neon else (110, 60, 25)
                pygame.draw.rect(screen, color, (px, py, cw, ch_px))
            elif ch == "1":      # P1 spawn
                color = PLAYER1_COLOR
                pygame.draw.rect(screen, color, (px, py, cw, ch_px))
            elif ch == "2":      # P2 spawn
                color = PLAYER2_COLOR
                pygame.draw.rect(screen, color, (px, py, cw, ch_px))

    # Neon border around preview
    border_col = (0, 160, 180) if neon else (30, 40, 60)
    pygame.draw.rect(screen, border_col, (x, y, w, h), 1)


# In-game HUD

def draw_hud(screen: pygame.Surface, p1: Tank, p2: Tank, scores: dict[int, int], round_num: int, round_wins: dict[int, int]) -> None:
    font = _font("arial", 18, bold=True)

    # P1 info (left)
    p1_text = f"P1  HP: {p1.health}  Score: {scores[1]}/{SCORE_LIMIT}"
    left = font.render(p1_text, True, HUD_COLOR)
    left_rect = left.get_rect(topleft=(12, 8))
    pygame.draw.rect(screen, BG_COLOR, left_rect.inflate(8, 6))
    screen.blit(left, left_rect)

    # P1 powerups
    _draw_powerup_ui(screen, p1, x=12, y=30, align_right=False)

    # P2 info (right)
    p2_text = f"P2  HP: {p2.health}  Score: {scores[2]}/{SCORE_LIMIT}"
    right = font.render(p2_text, True, HUD_COLOR)
    right_rect = right.get_rect(topright=(screen.get_width() - 12, 8))
    pygame.draw.rect(screen, BG_COLOR, right_rect.inflate(8, 6))
    screen.blit(right, right_rect)

    # P2 powerups
    _draw_powerup_ui(screen, p2, x=screen.get_width() - 12, y=30, align_right=True)

    # Round info (center top)
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


# Powerup HUD

_POWERUP_META: dict[PowerUpType, tuple[str, tuple[int, int, int], float]] = {
    PowerUpType.SPEED: ("SPD", POWERUP_COLORS["speed"], 5.0),
    PowerUpType.SHIELD: ("SHD", POWERUP_COLORS["shield"], 8.0),
    PowerUpType.TRIPLE: ("TRI", POWERUP_COLORS["triple"], 6.0),
}


def _draw_powerup_ui(screen: pygame.Surface, tank: Tank,
                     x: int, y: int, align_right: bool) -> None:
    """Render sleek neon progress bars for each active powerup."""
    if not tank.active_powerups:
        return

    bar_w = 110
    bar_h = 14
    spacing = 3
    label_font = _font("arial", 11, bold=True)
    t = time.time()

    for idx, (ptype, remaining) in enumerate(tank.active_powerups.items()):
        meta = _POWERUP_META.get(ptype)
        if meta is None:
            continue
        label, base_color, max_dur = meta
        ratio = max(0.0, min(1.0, remaining / max_dur))

        by = y + idx * (bar_h + spacing)
        if align_right:
            bx = x - bar_w
        else:
            bx = x

        # Translucent background panel
        panel = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
        panel.fill((10, 12, 20, 180))
        screen.blit(panel, (bx, by))

        # Filled portion with glow
        fill_w = int((bar_w - 2) * ratio)
        if fill_w > 0:
            glow_alpha = int(180 + 40 * math.sin(t * 6 + idx))
            fill_color = (base_color[0], base_color[1], base_color[2], glow_alpha)
            fill_surf = pygame.Surface((fill_w, bar_h - 2), pygame.SRCALPHA)
            fill_surf.fill(fill_color)
            screen.blit(fill_surf, (bx + 1, by + 1))

        # Neon border
        border_alpha = int(160 + 50 * math.sin(t * 4 + idx * 2))
        border_surf = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
        border_c = (base_color[0], base_color[1], base_color[2], border_alpha)
        pygame.draw.rect(border_surf, border_c, (0, 0, bar_w, bar_h), 1, border_radius=3)
        screen.blit(border_surf, (bx, by))

        # Label
        lbl = label_font.render(f"{label} {remaining:.1f}s", True, (230, 240, 255))
        lbl_rect = lbl.get_rect(midleft=(bx + 4, by + bar_h // 2)) if not align_right \
            else lbl.get_rect(midright=(bx + bar_w - 4, by + bar_h // 2))
        screen.blit(lbl, lbl_rect)


# Overlay screens

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

    title = _font("arial", 40).render(f" Player {winner_id} Wins the Match!", True, color)
    screen.blit(title, title.get_rect(center=(cx, cy - 40)))

    score_text = f"Rounds Won  —  P1: {scores[1]}  |  P2: {scores[2]}"
    score_surf = _font("arial", 22).render(score_text, True, HUD_COLOR)
    screen.blit(score_surf, score_surf.get_rect(center=(cx, cy + 10)))

    prompt = _font("arial", 18).render("Press Enter or Space to return to title", True, (160, 160, 160))
    screen.blit(prompt, prompt.get_rect(center=(cx, cy + 50)))


def draw_pause_menu(screen: pygame.Surface, selection: int, sfx_volume: float,
                    music_volume: float, *, title_text: str = "PAUSED",
                    show_return: bool = False, return_label: str = "Return to Main Menu") -> None:
    """Draw pause/settings overlay with volume controls and optional return button."""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    cx, cy = screen.get_rect().center
    t = time.time()

    # Title
    title_font = _font("arial", 36, bold=True)
    glow = title_font.render(title_text, True, _NEON_CYAN)
    glow.set_alpha(int(100 + 50 * math.sin(t * 3)))
    screen.blit(glow, glow.get_rect(center=(cx, cy - 100)))
    title = title_font.render(title_text, True, (230, 240, 255))
    screen.blit(title, title.get_rect(center=(cx, cy - 100)))

    # Volume controls
    option_font = _font("arial", 20)
    value_font = _font("arial", 18)
    
    bar_width = 200
    bar_height = 20
    bar_x = cx + 10

    def _draw_volume_row(label: str, volume: float, row_y: int, sel_idx: int) -> None:
        is_sel = selection == sel_idx
        color = _NEON_CYAN if is_sel else (140, 150, 170)
        lbl = option_font.render(label, True, color)
        screen.blit(lbl, lbl.get_rect(midright=(cx - 20, row_y)))

        by = row_y - bar_height // 2
        # Background bar
        pygame.draw.rect(screen, (30, 35, 50), (bar_x, by, bar_width, bar_height), border_radius=4)
        # Filled bar
        filled = int(bar_width * volume)
        if filled > 0:
            fill_color = _NEON_CYAN if is_sel else (60, 90, 140)
            pygame.draw.rect(screen, fill_color, (bar_x, by, filled, bar_height), border_radius=4)
        # Neon border
        pygame.draw.rect(screen, color, (bar_x, by, bar_width, bar_height), 2, border_radius=4)
        # Percentage
        pct = value_font.render(f"{int(volume * 100)}", True, color)
        screen.blit(pct, pct.get_rect(midleft=(bar_x + bar_width + 10, row_y)))

    _draw_volume_row("SFX Volume", sfx_volume, cy - 20, 0)
    _draw_volume_row("Music Volume", music_volume, cy + 30, 1)

    # Return button
    if show_return:
        btn_y = cy + 75
        is_sel = selection == 2
        btn_w, btn_h = 280, 40
        bx = cx - btn_w // 2

        panel_c = (20, 30, 50) if not is_sel else (15, 40, 70)
        pygame.draw.rect(screen, panel_c, (bx, btn_y, btn_w, btn_h), border_radius=6)
        border_c = _NEON_MAGENTA if is_sel else _PANEL_BORDER
        pygame.draw.rect(screen, border_c, (bx, btn_y, btn_w, btn_h), 2, border_radius=6)

        text_c = _NEON_MAGENTA if is_sel else (160, 160, 180)
        btn_font = _font("arial", 20, bold=True)
        btn_surf = btn_font.render(return_label, True, text_c)
        screen.blit(btn_surf, btn_surf.get_rect(center=(cx, btn_y + btn_h // 2)))

    # Instructions
    hint_font = _font("arial", 14)
    bottom_y = cy + 130 if show_return else cy + 90
    hints = [
        "↑↓ / WS: Select   ←→ / AD: Adjust",
        "ESC: Resume Game" if title_text == "PAUSED" else "ESC: Back",
    ]
    for i, hint in enumerate(hints):
        hint_surf = hint_font.render(hint, True, (90, 100, 120))
        screen.blit(hint_surf, hint_surf.get_rect(center=(cx, bottom_y + i * 20)))


def draw_countdown(screen: pygame.Surface, time_left: float) -> None:
    """Draw countdown overlay (3-2-1) in center of screen."""
    # Overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 100))
    screen.blit(overlay, (0, 0))

    cx, cy = screen.get_rect().center
    
    # Show 3, 2, or 1
    if time_left > 2.0:
        number = "3"
        color = (255, 100, 100)  # Red
    elif time_left > 1.0:
        number = "2"
        color = (255, 200, 100)  # Orange
    else:
        number = "1"
        color = (100, 255, 100)  # Green
    
    # Number
    countdown_font = _font("arial", 120)
    countdown_surf = countdown_font.render(number, True, color)
    screen.blit(countdown_surf, countdown_surf.get_rect(center=(cx, cy)))
    
    # Ready text
    ready_font = _font("arial", 32)
    ready_surf = ready_font.render("Get Ready!", True, (235, 235, 235))
    screen.blit(ready_surf, ready_surf.get_rect(center=(cx, cy - 100)))

