from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .nlp import Suggestion, SuggestionEngine, UserProfile
from .stt import STTService
from .tts_engine import TTSEngine


@dataclass
class AppState:
    transcript: str = "Waiting for audio…"
    suggestions: List[Suggestion] = field(default_factory=list)
    drafted_text: str = ""
    tts_enabled: bool = False


class InclusiVoiceController:
    """Coordinates transcript -> suggestions -> optional user-triggered speech."""

    def __init__(
        self,
        stt: STTService,
        suggestion_engine: SuggestionEngine,
        tts: TTSEngine,
        profile: UserProfile,
        max_suggestions: int = 3,
    ) -> None:
        self.stt = stt
        self.suggestion_engine = suggestion_engine
        self.tts = tts
        self.profile = profile
        self.max_suggestions = max_suggestions
        self.state = AppState()

    def process_audio_chunk(self, chunk) -> AppState:
        transcript = self.stt.transcribe_chunk(chunk)
        self.state.transcript = transcript.text
        self.state.suggestions = self.suggestion_engine.generate(
            transcript.text,
            self.profile,
            self.max_suggestions,
        )
        return self.state

    def select_suggestion(self, index: int) -> str:
        if index < 0 or index >= len(self.state.suggestions):
            return ""
        self.state.drafted_text = self.state.suggestions[index].text
        return self.state.drafted_text

    def set_tts_enabled(self, enabled: bool) -> None:
        self.state.tts_enabled = enabled

    def speak(self, text: str) -> bool:
        if not self.state.tts_enabled:
            return False
        return self.tts.speak(text)
