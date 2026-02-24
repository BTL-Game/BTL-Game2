from __future__ import annotations

from pathlib import Path

import pygame


SOUND_DIR = Path(__file__).resolve().parents[3] / "assets" / "sounds"
MUSIC_VOLUME = 0.2  # Lower volume for background music
SOUND_VOLUME = 0.3  # Lower volume for sound effects


class SoundManager:
    """Load and play sound effects and background music. Gracefully degrades if files are missing."""

    def __init__(self) -> None:
        self._enabled = True
        self._sounds: dict[str, pygame.mixer.Sound | None] = {}
        self._warned_disabled = False
        try:
            pygame.mixer.init()
        except pygame.error:
            # Try a more explicit init as a fallback (different platforms need params)
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            except pygame.error:
                self._enabled = False
                print("[SoundManager] Warning: pygame.mixer failed to initialize; audio disabled.")
                return

        self._sounds = {
            "shoot": self._load("shoot.wav"),
            "bounce": self._load("bounce.wav"),
            "explosion": self._load("explosion.wav"),
            "powerup": self._load("powerup.wav"),
        }

        # Set lower volumes for all sound effects
        for sound in self._sounds.values():
            if sound is not None:
                sound.set_volume(SOUND_VOLUME)

        # Load and play background music
        self._load_background_music()

    def play_shoot(self) -> None:
        self._play("shoot")

    def play_bounce(self) -> None:
        self._play("bounce")

    def play_explosion(self) -> None:
        self._play("explosion")

    def play_powerup(self) -> None:
        self._play("powerup")

    # -- internal -----------------------------------------------------------

    def _load_background_music(self) -> None:
        """Load and play background music on loop."""
        if not self._enabled:
            return
        path = SOUND_DIR / "backgroundmusic.mp3"
        if not path.exists():
            print(f"[SoundManager] Missing background music: {path}")
            return
        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
            pygame.mixer.music.play(-1)  # -1 means loop forever
            print("[SoundManager] Background music started.")
        except pygame.error as e:
            print(f"[SoundManager] Failed to load background music: {e}")

    def _load(self, filename: str) -> pygame.mixer.Sound | None:
        path = SOUND_DIR / filename
        if not path.exists():
            print(f"[SoundManager] Missing sound file: {path}")
            return None
        try:
            return pygame.mixer.Sound(str(path))
        except pygame.error:
            print(f"[SoundManager] Failed to load sound: {path}")
            return None

    def _play(self, name: str) -> None:
        if not self._enabled:
            if not self._warned_disabled:
                print("[SoundManager] Audio disabled; cannot play sounds.")
                self._warned_disabled = True
            return
        sound = self._sounds.get(name)
        if sound is not None:
            sound.play()
