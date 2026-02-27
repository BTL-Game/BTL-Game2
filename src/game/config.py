# ---------------------------------------------------------------------------
# Screen
# ---------------------------------------------------------------------------
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
SCREEN_TITLE = "Tank Battle: Chaos Maze"
FPS = 60

# ---------------------------------------------------------------------------
# Tiles & Walls
# ---------------------------------------------------------------------------
TILE_SIZE = 40
WALL_INSET = 1

TILE_OPEN = "."
TILE_STEEL = "#"
TILE_BRICK = "B"
TILE_SPAWN_P1 = "1"
TILE_SPAWN_P2 = "2"

BRICK_HEALTH = 2  # hits to destroy a brick wall

# ---------------------------------------------------------------------------
# Tank
# ---------------------------------------------------------------------------
TANK_SPEED = 120.0
TANK_TURN_SPEED = 180.0
TANK_SIZE = 40
TURRET_LENGTH = 26
TURRET_TURN_SPEED = 200.0  # independent turret rotation speed (deg/s)

# ---------------------------------------------------------------------------
# Shooting & Bullets
# ---------------------------------------------------------------------------
SHOOT_SIZE = 28
SHOOT_FLASH_DURATION = 0.12

BULLET_SPEED = 280.0
BULLET_RADIUS = 4
BULLET_MAX_PER_PLAYER = 5
BULLET_COOLDOWN = 0.25
BULLET_MAX_BOUNCES = 5

# ---------------------------------------------------------------------------
# Health & Scoring
# ---------------------------------------------------------------------------
PLAYER_HEALTH = 3
SCORE_LIMIT = 30  # first player to reach this score (by collecting food) wins

# ---------------------------------------------------------------------------
# Food (scoring items)
# ---------------------------------------------------------------------------
FOOD_SIZE = TILE_SIZE // 2  # exactly half a wall tile (20px)
FOOD_INITIAL_COUNT = 8       # food items spawned at match start
FOOD_SPAWN_INTERVAL = 6.0    # seconds between respawn waves
FOOD_MAX_ON_MAP = 15         # maximum food items on map at once
FOOD_BASE_SCORE = 1          # score value for wave-1 food
FOOD_SCORE_INCREMENT = 0     # added per wave (all food worth 1pt now)

# ---------------------------------------------------------------------------
# Power-ups
# ---------------------------------------------------------------------------
POWERUP_SPAWN_INTERVAL = 8.0   # seconds between spawn attempts
POWERUP_MAX_ON_MAP = 2
POWERUP_SIZE = 24

SPEED_BOOST_MULTIPLIER = 1.5
SPEED_BOOST_DURATION = 5.0

SHIELD_DURATION = 8.0

TRIPLE_SHOT_DURATION = 6.0
TRIPLE_SHOT_SPREAD = 15.0  # degrees offset for side bullets

# ---------------------------------------------------------------------------
# Particles
# ---------------------------------------------------------------------------
PARTICLE_COUNT = 25
PARTICLE_SPEED_MIN = 60.0
PARTICLE_SPEED_MAX = 200.0
PARTICLE_LIFETIME = 0.8
PARTICLE_SIZE = 3

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------
WALL_COLOR = (70, 70, 80)
BRICK_COLOR = (160, 90, 50)
PLAYER1_COLOR = (80, 180, 240)
PLAYER2_COLOR = (240, 120, 80)
BULLET_COLOR = (240, 230, 120)
HUD_COLOR = (235, 235, 235)
BG_COLOR = (20, 20, 24)

POWERUP_COLORS = {
    "speed": (50, 220, 100),
    "shield": (100, 180, 255),
    "triple": (255, 200, 60),
}

# ---------------------------------------------------------------------------
# Audio Settings
# ---------------------------------------------------------------------------
DEFAULT_SFX_VOLUME = 0.5  # 50/100
DEFAULT_MUSIC_VOLUME = 0.5  # 50/100
VOLUME_STEP = 0.1  # Volume adjustment increment
