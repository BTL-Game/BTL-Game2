import pygame

from game.config import HUD_COLOR

def draw_title_screen(screen: pygame.Surface) -> None:
    font = pygame.font.SysFont("arial", 36)
    prompt = pygame.font.SysFont("arial", 20)
    title_surface = font.render("Tank Battle: Chaos Maze", True, (235, 235, 235))
    prompt_surface = prompt.render("Press Enter or Space to start", True, (200, 200, 200))

    screen_rect = screen.get_rect()
    title_rect = title_surface.get_rect(center=(screen_rect.centerx, screen_rect.centery - 20))
    prompt_rect = prompt_surface.get_rect(center=(screen_rect.centerx, screen_rect.centery + 30))

    screen.blit(title_surface, title_rect)
    screen.blit(prompt_surface, prompt_rect)


def draw_hud(screen: pygame.Surface, p1_health: int, p2_health: int, p1_score: int, p2_score: int) -> None:
    font = pygame.font.SysFont("arial", 18)
    left = font.render(f"P1 HP: {p1_health}  Score: {p1_score}", True, HUD_COLOR)
    right = font.render(f"P2 HP: {p2_health}  Score: {p2_score}", True, HUD_COLOR)

    screen.blit(left, (12, 10))
    right_rect = right.get_rect(topright=(screen.get_width() - 12, 10))
    screen.blit(right, right_rect)


def draw_game_over(screen: pygame.Surface, winner_text: str) -> None:
    font = pygame.font.SysFont("arial", 32)
    prompt = pygame.font.SysFont("arial", 20)

    title_surface = font.render(winner_text, True, HUD_COLOR)
    prompt_surface = prompt.render("Press Enter or Space to restart", True, (200, 200, 200))

    screen_rect = screen.get_rect()
    title_rect = title_surface.get_rect(center=(screen_rect.centerx, screen_rect.centery - 20))
    prompt_rect = prompt_surface.get_rect(center=(screen_rect.centerx, screen_rect.centery + 30))

    screen.blit(title_surface, title_rect)
    screen.blit(prompt_surface, prompt_rect)
