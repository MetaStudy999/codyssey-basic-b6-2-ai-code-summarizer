from __future__ import annotations

import unittest

from ai_git_assistant.git_context import GitContext
from ai_git_assistant.safety import apply_safe_mode


class SafetyTests(unittest.TestCase):
    def test_masks_common_secrets_and_email(self) -> None:
        context = GitContext(
            status=" M config.py",
            diff="API_KEY=supersecret123\nuser=jane@example.com\n",
            changed_files=("config.py",),
            diff_lines=2,
        )
        safe = apply_safe_mode(context)
        self.assertNotIn("supersecret123", safe.diff)
        self.assertNotIn("jane@example.com", safe.diff)
        self.assertGreaterEqual(safe.masked_items, 2)

    def test_limits_files_and_lines(self) -> None:
        files = tuple(f"f{i}.py" for i in range(12))
        diff = "\n".join(f"line {i}" for i in range(250))
        context = GitContext(" M f0.py", diff, files, 250)
        safe = apply_safe_mode(context)
        self.assertEqual(len(safe.changed_files), 10)
        self.assertTrue(safe.truncated)
        self.assertIn("diff truncated", safe.diff)
