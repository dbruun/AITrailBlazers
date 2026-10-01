import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import summarizer  # noqa: E402

TEXT = (
    "Contoso is launching a new customer support portal next month. "
    "The portal uses AI to summarize support tickets for agents. "
    "Agents said they spend too much time reading long support tickets. "
    "The weather was sunny on Tuesday. "
    "Early pilots show agents resolve support tickets faster with AI summaries."
)


class SummarizerTests(unittest.TestCase):
    def test_short_text_is_returned_unchanged(self):
        self.assertEqual(summarizer.summarize_offline("One. Two.", 3), "One. Two.")

    def test_limits_sentence_count_and_preserves_order(self):
        result = summarizer.summarize_offline(TEXT, 2)
        sentences = summarizer.split_sentences(result)
        self.assertEqual(len(sentences), 2)
        original = summarizer.split_sentences(TEXT)
        positions = [original.index(s) for s in sentences]
        self.assertEqual(positions, sorted(positions))

    def test_drops_off_topic_sentence(self):
        self.assertNotIn("weather", summarizer.summarize_offline(TEXT, 3))

    def test_uses_offline_mode_without_configuration(self):
        summary, mode = summarizer.summarize(TEXT, 2, env={})
        self.assertEqual(mode, "offline")
        self.assertTrue(summary)

    def test_detects_azure_openai_configuration(self):
        env = {
            "AZURE_OPENAI_ENDPOINT": "https://example.openai.azure.com",
            "AZURE_OPENAI_API_KEY": "placeholder",
            "AZURE_OPENAI_DEPLOYMENT": "gpt-4o-mini",
        }
        self.assertTrue(summarizer.azure_openai_configured(env))
        self.assertFalse(summarizer.azure_openai_configured({}))


if __name__ == "__main__":
    unittest.main()
