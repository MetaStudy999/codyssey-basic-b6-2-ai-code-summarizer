from __future__ import annotations

from dataclasses import dataclass
import re

from .errors import ValidationError


@dataclass(frozen=True)
class CommitDraft:
    title: str
    body: tuple[str, ...]


@dataclass(frozen=True)
class PRDraft:
    title: str
    body: str


def _strip_fence(text: str) -> str:
    value = text.strip()
    if value.startswith("```") and value.endswith("```"):
        lines = value.splitlines()
        if len(lines) >= 2:
            value = "\n".join(lines[1:-1]).strip()
    return value


def parse_commit_draft(text: str) -> CommitDraft:
    value = _strip_fence(text)
    match = re.search(r"(?m)^TITLE:\s*(.+)$", value)
    if not match:
        raise ValidationError("commit TITLE marker is missing")
    title = " ".join(match.group(1).split())
    if not title:
        raise ValidationError("commit title is empty")
    if len(title) > 72:
        raise ValidationError(f"commit title exceeds 72 characters ({len(title)})")

    body_match = re.search(r"(?ms)^BODY:\s*\n(?P<body>.*)$", value)
    if not body_match:
        raise ValidationError("commit BODY marker is missing")
    bullets = tuple(
        line.strip()
        for line in body_match.group("body").splitlines()
        if line.strip().startswith("-")
    )
    if not (1 <= len(bullets) <= 2):
        raise ValidationError("commit body must contain 1-2 bullets")
    return CommitDraft(title=title, body=bullets)


def parse_pr_draft(text: str) -> PRDraft:
    value = _strip_fence(text)
    title_match = re.search(r"(?m)^PR_TITLE:\s*(.+)$", value)
    if not title_match:
        raise ValidationError("PR_TITLE marker is missing")
    title = " ".join(title_match.group(1).split())
    if not title:
        raise ValidationError("PR title is empty")
    if len(title) > 80:
        raise ValidationError(f"PR title exceeds 80 characters ({len(title)})")

    body_match = re.search(r"(?ms)^PR_BODY:\s*\n(?P<body>.*)$", value)
    if not body_match:
        raise ValidationError("PR_BODY marker is missing")
    body = body_match.group("body").strip()

    headers = ["## Why", "## What", "## How to Test"]
    positions: list[int] = []
    for header in headers:
        pos = body.find(header)
        if pos < 0:
            raise ValidationError(f"required PR section is missing: {header}")
        positions.append(pos)
    if positions != sorted(positions):
        raise ValidationError("PR sections are out of order")

    for index, header in enumerate(headers):
        start = positions[index] + len(header)
        end = positions[index + 1] if index + 1 < len(headers) else len(body)
        section = body[start:end]
        if not any(line.strip().startswith("-") for line in section.splitlines()):
            raise ValidationError(f"PR section needs at least one bullet: {header}")

    return PRDraft(title=title, body=body)
