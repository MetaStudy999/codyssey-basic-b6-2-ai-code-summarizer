from __future__ import annotations

import unittest

from ai_git_assistant.generator import GenerationService
from ai_git_assistant.providers import AIProvider
from ai_git_assistant.safety import SafeContext


CONTEXT = SafeContext(" M app.py", "+change", ("app.py",), 0, False)


class FakeProvider(AIProvider):
    def __init__(self, outputs: list[str]) -> None:
        self.outputs = outputs
        self.calls = 0
        self.params: list[tuple[str, float, int]] = []

    def generate(self, prompt: str, *, model: str, temperature: float, max_tokens: int) -> str:
        self.params.append((model, temperature, max_tokens))
        value = self.outputs[self.calls]
        self.calls += 1
        return value


class GeneratorTests(unittest.TestCase):
    def test_commit_uses_one_call_when_valid(self) -> None:
        provider = FakeProvider(["TITLE: feat: update app\nBODY:\n- Update app.py"])
        service = GenerationService(provider, model="m", temperature=0.1, max_tokens=100)
        result = service.generate_commit(CONTEXT)
        self.assertEqual(result.api_calls, 1)
        self.assertFalse(result.repaired)
        self.assertEqual(provider.params[0], ("m", 0.1, 100))

    def test_invalid_pr_gets_one_repair_call(self) -> None:
        provider = FakeProvider(
            [
                "bad output",
                "PR_TITLE: feat: update app\nPR_BODY:\n"
                "## Why\n- Keep draft consistent\n"
                "## What\n- Update app.py\n"
                "## How to Test\n- Verify generated draft\n",
            ]
        )
        service = GenerationService(provider, model="m", temperature=0.2, max_tokens=200)
        result = service.generate_pr(CONTEXT)
        self.assertEqual(result.api_calls, 2)
        self.assertTrue(result.repaired)
