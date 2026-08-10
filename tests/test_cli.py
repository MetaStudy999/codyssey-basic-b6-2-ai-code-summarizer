from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from ai_git_assistant.cli import build_parser, main


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


class CliTests(unittest.TestCase):
    def make_repo(self, changed: bool) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        repo = Path(temp.name)
        git(repo, "init")
        git(repo, "config", "user.name", "Test User")
        git(repo, "config", "user.email", "test@example.com")
        (repo / "a.txt").write_text("a\n", encoding="utf-8")
        git(repo, "add", "a.txt")
        git(repo, "commit", "-m", "init")
        if changed:
            (repo / "a.txt").write_text("a\nb\n", encoding="utf-8")
        return repo

    def test_cli_option_aliases_parse(self) -> None:
        args = build_parser().parse_args(
            ["commit", "-model", "demo", "-temperature", "0.4", "-max-tokens", "321"]
        )
        self.assertEqual(args.model, "demo")
        self.assertEqual(args.temperature, 0.4)
        self.assertEqual(args.max_tokens, 321)

    def test_clean_repo_exits_without_api_key(self) -> None:
        repo = self.make_repo(changed=False)
        previous = Path.cwd()
        try:
            os.chdir(repo)
            with self.assertRaises(SystemExit) as caught:
                main(["commit"])
            self.assertEqual(caught.exception.code, 0)
        finally:
            os.chdir(previous)

    def test_changed_repo_missing_api_key_returns_nonzero(self) -> None:
        repo = self.make_repo(changed=True)
        previous = Path.cwd()
        try:
            os.chdir(repo)
            with patch.dict(os.environ, {}, clear=True):
                self.assertEqual(main(["commit"]), 2)
        finally:
            os.chdir(previous)
