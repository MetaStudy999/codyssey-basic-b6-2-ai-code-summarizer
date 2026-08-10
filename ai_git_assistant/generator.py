from __future__ import annotations

from dataclasses import dataclass

from .errors import ValidationError
from .prompts import build_commit_prompt, build_pr_prompt, build_repair_prompt
from .providers import AIProvider
from .safety import SafeContext
from .validators import CommitDraft, PRDraft, parse_commit_draft, parse_pr_draft


@dataclass(frozen=True)
class GenerationResult:
    draft: CommitDraft | PRDraft
    api_calls: int
    repaired: bool


class GenerationService:
    def __init__(
        self,
        provider: AIProvider,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> None:
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def _call(self, prompt: str) -> str:
        return self.provider.generate(
            prompt,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

    def generate_commit(self, context: SafeContext) -> GenerationResult:
        raw = self._call(build_commit_prompt(context))
        try:
            return GenerationResult(parse_commit_draft(raw), api_calls=1, repaired=False)
        except ValidationError as first_error:
            repaired = self._call(build_repair_prompt("commit", raw, str(first_error)))
            return GenerationResult(parse_commit_draft(repaired), api_calls=2, repaired=True)

    def generate_pr(self, context: SafeContext) -> GenerationResult:
        raw = self._call(build_pr_prompt(context))
        try:
            return GenerationResult(parse_pr_draft(raw), api_calls=1, repaired=False)
        except ValidationError as first_error:
            repaired = self._call(build_repair_prompt("pr", raw, str(first_error)))
            return GenerationResult(parse_pr_draft(repaired), api_calls=2, repaired=True)
