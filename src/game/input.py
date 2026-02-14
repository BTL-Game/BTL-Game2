import pygame


class PlayerControls:
    def __init__(self, up: int, down: int, left: int, right: int, fire: int, fire_alt: int) -> None:
        self.up = up
        self.down = down
        self.left = left
        self.right = right
        self.fire = fire
        self.fire_alt = fire_alt


PLAYER1 = PlayerControls(
    up=pygame.K_w,
    down=pygame.K_s,
    left=pygame.K_a,
    right=pygame.K_d,
    fire=pygame.K_SPACE,
    fire_alt=pygame.K_f,
)

PLAYER2 = PlayerControls(
    up=pygame.K_UP,
    down=pygame.K_DOWN,
    left=pygame.K_LEFT,
    right=pygame.K_RIGHT,
    fire=pygame.K_RETURN,
    fire_alt=pygame.K_m,
)
