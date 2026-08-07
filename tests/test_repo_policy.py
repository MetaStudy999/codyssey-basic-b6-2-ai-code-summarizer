from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class RepoPolicyTests(unittest.TestCase):
    def test_gitignore_blocks_env_files(self) -> None:
        text = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".env", text)
        self.assertIn("!.env.example", text)

    def test_env_example_has_placeholder_not_secret(self) -> None:
        text = (ROOT / ".env.example").read_text(encoding="utf-8")
        self.assertIn("AI_API_KEY=YOUR_KEY", text)
