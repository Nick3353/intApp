from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AppConfig:
    app_name: str = "InclusiVoice"
    sample_rate: int = 16000
    chunk_seconds: float = 0.5
    max_suggestions: int = 3
    window_alpha: float = 0.92
    data_dir: Path = field(default_factory=lambda: Path.home() / ".inclusivoice")

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
