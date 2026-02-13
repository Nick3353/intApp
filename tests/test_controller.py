import unittest

from inclusivoice.audio import AudioChunk
from inclusivoice.controller import InclusiVoiceController
from inclusivoice.nlp import SuggestionEngine, UserProfile
from inclusivoice.stt import STTService


class _FakeTTS:
    def __init__(self):
        self.spoken = []

    def speak(self, text: str) -> bool:
        self.spoken.append(text)
        return True


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.tts = _FakeTTS()
        self.controller = InclusiVoiceController(
            stt=STTService(),
            suggestion_engine=SuggestionEngine(),
            tts=self.tts,
            profile=UserProfile(name="Jordan"),
        )

    def test_processing_chunk_updates_transcript_and_suggestions(self):
        state = self.controller.process_audio_chunk(AudioChunk(pcm=b"", timestamp=0.0))
        self.assertTrue(state.transcript)
        self.assertGreater(len(state.suggestions), 0)

    def test_speak_requires_explicit_consent(self):
        self.assertFalse(self.controller.speak("hello"))
        self.controller.set_tts_enabled(True)
        self.assertTrue(self.controller.speak("hello"))
        self.assertEqual(self.tts.spoken, ["hello"])

    def test_speak_rejects_blank_text(self):
        self.controller.set_tts_enabled(True)
        self.assertFalse(self.controller.speak("   "))
        self.assertEqual(self.tts.spoken, [])


if __name__ == "__main__":
    unittest.main()
