from __future__ import annotations

from dataclasses import dataclass
import subprocess
from pathlib import Path

from .errors import GitContextError


@dataclass(frozen=True)
class GitContext:
    status: str
    diff: str
    changed_files: tuple[str, ...]
    diff_lines: int

    @property
    def has_changes(self) -> bool:
        return bool(self.status.strip())


def _run_git(args: list[str], cwd: str | Path | None = None) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as exc:
        raise GitContextError(f"Git 명령을 실행할 수 없습니다: {exc}") from exc

    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "unknown Git error"
        raise GitContextError(
            "Git 저장소에서 실행해야 합니다. "
            f"git {' '.join(args)} 실패: {detail}"
        )
    return completed.stdout


def _parse_changed_files(status: str) -> tuple[str, ...]:
    files: list[str] = []
    for raw_line in status.splitlines():
        if not raw_line.strip():
            continue
        path = raw_line[3:] if len(raw_line) >= 4 else raw_line.strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        path = path.strip().strip('"')
        if path and path not in files:
            files.append(path)
    return tuple(files)


def collect_git_context(cwd: str | Path | None = None) -> GitContext:
    """Collect the mission-required git status and git diff context.

    `git diff --cached` is included because staged changes are still a `git diff`
    view and would otherwise be omitted from the AI context.
    """

    status = _run_git(["status", "--porcelain=v1"], cwd=cwd)
    unstaged = _run_git(["diff", "--no-ext-diff", "--unified=3"], cwd=cwd)
    staged = _run_git(["diff", "--cached", "--no-ext-diff", "--unified=3"], cwd=cwd)

    parts = [part.rstrip() for part in (unstaged, staged) if part.strip()]
    diff = "\n\n".join(parts)
    return GitContext(
        status=status.rstrip(),
        diff=diff.rstrip(),
        changed_files=_parse_changed_files(status),
        diff_lines=len(diff.splitlines()) if diff else 0,
    )
