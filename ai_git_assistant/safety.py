from __future__ import annotations

from dataclasses import dataclass
import re

from .git_context import GitContext


@dataclass(frozen=True)
class SafeContext:
    status: str
    diff: str
    changed_files: tuple[str, ...]
    masked_items: int
    truncated: bool


_SECRET_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"(?i)(authorization\s*:\s*bearer\s+)[A-Za-z0-9._~+/=-]{8,}"),
        r"\1[REDACTED]",
    ),
    (
        re.compile(
            r"(?i)((?:api[_-]?key|token|secret|password)\s*[=:]\s*[\"']?)[^\s\"']{6,}"
        ),
        r"\1[REDACTED]",
    ),
    (
        re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        "[REDACTED_EMAIL]",
    ),
)


def _mask(text: str) -> tuple[str, int]:
    masked = text
    total = 0
    for pattern, replacement in _SECRET_PATTERNS:
        masked, count = pattern.subn(replacement, masked)
        total += count
    return masked, total


def apply_safe_mode(
    context: GitContext,
    *,
    max_files: int = 10,
    max_lines: int = 200,
) -> SafeContext:
    """Mask common secret patterns and bound transmitted diff size."""

    status, status_masked = _mask(context.status)
    diff, diff_masked = _mask(context.diff)

    allowed_files = context.changed_files[:max_files]
    truncated = len(context.changed_files) > max_files

    lines = diff.splitlines()
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines.append("... [SAFE MODE: diff truncated] ...")
        truncated = True

    return SafeContext(
        status=status,
        diff="\n".join(lines),
        changed_files=tuple(allowed_files),
        masked_items=status_masked + diff_masked,
        truncated=truncated,
    )
