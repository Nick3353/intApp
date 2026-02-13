import unittest

from inclusivoice.nlp import SuggestionEngine, UserProfile


class SuggestionEngineTests(unittest.TestCase):
    def test_intro_question_generates_intro_suggestion(self):
        engine = SuggestionEngine()
        profile = UserProfile(name="Alex")
        suggestions = engine.generate("Can you tell me about yourself?", profile)
        self.assertGreater(len(suggestions), 0)
        self.assertIn("Alex", suggestions[0].text)

    def test_limit_is_respected(self):
        engine = SuggestionEngine()
        suggestions = engine.generate("Why do you want this role?", UserProfile(), limit=2)
        self.assertEqual(len(suggestions), 2)


if __name__ == "__main__":
    unittest.main()
