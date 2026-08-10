from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from ai_git_assistant.git_context import collect_git_context


def run(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


class GitContextTests(unittest.TestCase):
    def make_repo(self) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        repo = Path(temp.name)
        run(repo, "init")
        run(repo, "config", "user.name", "Test User")
        run(repo, "config", "user.email", "test@example.com")
        (repo / "sample.txt").write_text("one\n", encoding="utf-8")
        run(repo, "add", "sample.txt")
        run(repo, "commit", "-m", "init")
        return repo

    def test_clean_repo_has_no_changes(self) -> None:
        repo = self.make_repo()
        context = collect_git_context(repo)
        self.assertFalse(context.has_changes)
        self.assertEqual(context.changed_files, ())

    def test_collects_status_and_diff_for_modified_file(self) -> None:
        repo = self.make_repo()
        (repo / "sample.txt").write_text("one\ntwo\n", encoding="utf-8")
        context = collect_git_context(repo)
        self.assertTrue(context.has_changes)
        self.assertIn("sample.txt", context.changed_files)
        self.assertIn("+two", context.diff)

    def test_collects_staged_diff(self) -> None:
        repo = self.make_repo()
        (repo / "sample.txt").write_text("changed\n", encoding="utf-8")
        run(repo, "add", "sample.txt")
        context = collect_git_context(repo)
        self.assertTrue(context.has_changes)
        self.assertIn("+changed", context.diff)
