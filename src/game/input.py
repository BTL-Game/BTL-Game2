import pygame


class PlayerControls:
    def __init__(
        self,
        up: int,
        down: int,
        left: int,
        right: int,
        fire: int,
        fire_alt: int,
        turret_left: int,
        turret_right: int,
    ) -> None:
        self.up = up
        self.down = down
        self.left = left
        self.right = right
        self.fire = fire
        self.fire_alt = fire_alt
        self.turret_left = turret_left
        self.turret_right = turret_right


PLAYER1 = PlayerControls(
    up=pygame.K_w,
    down=pygame.K_s,
    left=pygame.K_a,
    right=pygame.K_d,
    fire=pygame.K_SPACE,
    fire_alt=pygame.K_f,
    turret_left=pygame.K_q,
    turret_right=pygame.K_e,
)

PLAYER2 = PlayerControls(
    up=pygame.K_UP,
    down=pygame.K_DOWN,
    left=pygame.K_LEFT,
    right=pygame.K_RIGHT,
    fire=pygame.K_RETURN,
    fire_alt=pygame.K_m,
    turret_left=pygame.K_n,
    turret_right=pygame.K_COMMA,
)
