from __future__ import annotations

from pathlib import Path

import pygame


SOUND_DIR = Path(__file__).resolve().parents[2] / "assets" / "sounds"


class SoundManager:
    """Load and play sound effects. Gracefully degrades if files are missing."""

    def __init__(self) -> None:
        self._enabled = True
        self._sounds: dict[str, pygame.mixer.Sound | None] = {}
        try:
            pygame.mixer.init()
        except pygame.error:
            self._enabled = False
            return

        self._sounds = {
            "shoot": self._load("shoot.wav"),
            "bounce": self._load("bounce.wav"),
            "explosion": self._load("explosion.wav"),
            "powerup": self._load("powerup.wav"),
        }

    def play_shoot(self) -> None:
        self._play("shoot")

    def play_bounce(self) -> None:
        self._play("bounce")

    def play_explosion(self) -> None:
        self._play("explosion")

    def play_powerup(self) -> None:
        self._play("powerup")

    # -- internal -----------------------------------------------------------

    def _load(self, filename: str) -> pygame.mixer.Sound | None:
        path = SOUND_DIR / filename
        if not path.exists():
            return None
        try:
            return pygame.mixer.Sound(str(path))
        except pygame.error:
            return None

    def _play(self, name: str) -> None:
        if not self._enabled:
            return
        sound = self._sounds.get(name)
        if sound is not None:
            sound.play()
