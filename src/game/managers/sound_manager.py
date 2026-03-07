from __future__ import annotations

import sys
from pathlib import Path
import logging

import pygame

from game.config import DEFAULT_MUSIC_VOLUME, DEFAULT_SFX_VOLUME


def _get_sound_dir() -> Path:
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / "assets" / "sounds"
    else:
        return Path(__file__).resolve().parents[3] / "assets" / "sounds"


SOUND_DIR = _get_sound_dir()
_log = logging.getLogger(__name__)


class SoundManager:
    """Loads and plays SFX and background music. Silently degrades if audio is unavailable."""

    def __init__(self) -> None:
        self._enabled = True
        self._sounds: dict[str, pygame.mixer.Sound | None] = {}
        self._warned_disabled = False
        self._sfx_volume = DEFAULT_SFX_VOLUME
        self._music_volume = DEFAULT_MUSIC_VOLUME
        
        try:
            pygame.mixer.init()
        except pygame.error:
            # Fallback init for platform compatibility
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            except pygame.error:
                self._enabled = False
                _log.warning("pygame.mixer failed to initialize; audio disabled.")
                return

        self._sounds = {
            "shoot": self._load("shoot.wav"),
            "bounce": self._load("bounce.wav"),
            "explosion": self._load("explosion.wav"),
            "powerup": self._load("powerup.wav"),
        }

        # Set volumes for all sound effects
        self._update_sfx_volume()

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

    def set_sfx_volume(self, volume: float) -> None:
        """Set SFX volume (0.0 to 1.0)."""
        self._sfx_volume = max(0.0, min(1.0, volume))
        self._update_sfx_volume()

    def set_music_volume(self, volume: float) -> None:
        """Set music volume (0.0 to 1.0)."""
        self._music_volume = max(0.0, min(1.0, volume))
        if self._enabled:
            pygame.mixer.music.set_volume(self._music_volume)

    def get_sfx_volume(self) -> float:
        """Get current SFX volume."""
        return self._sfx_volume

    def get_music_volume(self) -> float:
        """Get current music volume."""
        return self._music_volume

    # Internal

    def _update_sfx_volume(self) -> None:
        """Apply current SFX volume to all sounds."""
        for sound in self._sounds.values():
            if sound is not None:
                sound.set_volume(self._sfx_volume)

    def _load_background_music(self) -> None:
        """Load and play background music on loop."""
        if not self._enabled:
            return
        path = SOUND_DIR / "backgroundmusic.mp3"
        if not path.exists():
            _log.debug("Missing background music: %s", path)
            return
        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(self._music_volume)
            pygame.mixer.music.play(-1)  # -1 means loop forever
            _log.info("Background music started.")
        except pygame.error as e:
            _log.debug("Failed to load background music: %s", e)

    def _load(self, filename: str) -> pygame.mixer.Sound | None:
        path = SOUND_DIR / filename
        if not path.exists():
            _log.debug("Missing sound file: %s", path)
            return None
        try:
            return pygame.mixer.Sound(str(path))
        except pygame.error:
            _log.debug("Failed to load sound: %s", path)
            return None

    def _play(self, name: str) -> None:
        if not self._enabled:
            if not self._warned_disabled:
                _log.info("Audio disabled; cannot play sounds.")
                self._warned_disabled = True
            return
        sound = self._sounds.get(name)
        if sound is not None:
            sound.play()
