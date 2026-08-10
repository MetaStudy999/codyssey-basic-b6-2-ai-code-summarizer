from __future__ import annotations

import unittest

from ai_git_assistant.errors import ValidationError
from ai_git_assistant.prompts import build_commit_prompt, build_pr_prompt
from ai_git_assistant.safety import SafeContext
from ai_git_assistant.validators import parse_commit_draft, parse_pr_draft


CONTEXT = SafeContext(
    status=" M app.py",
    diff="diff --git a/app.py b/app.py\n+print('ok')",
    changed_files=("app.py",),
    masked_items=0,
    truncated=False,
)


class PromptAndValidatorTests(unittest.TestCase):
    def test_commit_prompt_contains_git_context_and_contract(self) -> None:
        prompt = build_commit_prompt(CONTEXT)
        self.assertIn("TITLE:", prompt)
        self.assertIn("app.py", prompt)
        self.assertIn("git diff", prompt.lower())

    def test_pr_prompt_requires_three_sections(self) -> None:
        prompt = build_pr_prompt(CONTEXT)
        self.assertIn("## Why", prompt)
        self.assertIn("## What", prompt)
        self.assertIn("## How to Test", prompt)

    def test_parse_valid_commit(self) -> None:
        draft = parse_commit_draft("TITLE: feat: add output\nBODY:\n- Update app.py output")
        self.assertEqual(draft.title, "feat: add output")
        self.assertEqual(len(draft.body), 1)

    def test_rejects_long_commit_title(self) -> None:
        text = "TITLE: " + ("x" * 73) + "\nBODY:\n- change"
        with self.assertRaises(ValidationError):
            parse_commit_draft(text)

    def test_parse_valid_pr(self) -> None:
        draft = parse_pr_draft(
            "PR_TITLE: feat: add output\n"
            "PR_BODY:\n"
            "## Why\n- Improve output\n"
            "## What\n- Update app.py\n"
            "## How to Test\n- Run the CLI\n"
        )
        self.assertIn("## How to Test", draft.body)

    def test_rejects_pr_section_without_bullet(self) -> None:
        text = (
            "PR_TITLE: title\nPR_BODY:\n"
            "## Why\nplain text\n"
            "## What\n- change\n"
            "## How to Test\n- test\n"
        )
        with self.assertRaises(ValidationError):
            parse_pr_draft(text)
