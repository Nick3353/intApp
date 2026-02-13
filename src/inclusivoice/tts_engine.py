from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TTSConfig:
    rate: int = 170
    volume: float = 1.0


class TTSEngine:
    def __init__(self, config: TTSConfig | None = None) -> None:
        self.config = config or TTSConfig()
        self._engine = None
        try:
            import pyttsx3

            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", self.config.rate)
            self._engine.setProperty("volume", self.config.volume)
        except Exception:
            self._engine = None

    def speak(self, text: str) -> bool:
        if not text.strip():
            return False
        if self._engine is None:
            # No backend available in current environment.
            return False
        self._engine.say(text)
        self._engine.runAndWait()
        return True
