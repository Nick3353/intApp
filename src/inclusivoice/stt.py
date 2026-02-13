from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Iterable

from .audio import AudioChunk


@dataclass
class TranscriptEvent:
    text: str
    confidence: float
    is_final: bool = True


class STTService:
    """
    Prototype STT service.
    - Fallback mode emits sample interview questions.
    - Replace transcribe_chunk with whisper.cpp / Azure streaming adapter.
    """

    def __init__(self) -> None:
        self._fallback_questions = itertools.cycle(
            [
                "Can you tell me about yourself?",
                "Describe a challenging project and how you handled it.",
                "Why do you want to work in this role?",
                "What are your strengths in team collaboration?",
            ]
        )

    def transcribe_chunk(self, chunk: AudioChunk) -> TranscriptEvent:
        # Placeholder behavior for prototype demonstration.
        _ = chunk
        return TranscriptEvent(text=next(self._fallback_questions), confidence=0.75)

    def stream_transcripts(self, chunks: Iterable[AudioChunk]) -> Iterable[TranscriptEvent]:
        for chunk in chunks:
            yield self.transcribe_chunk(chunk)
