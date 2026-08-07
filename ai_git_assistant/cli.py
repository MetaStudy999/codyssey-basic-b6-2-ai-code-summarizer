from __future__ import annotations

import argparse
import os
import sys
from typing import Sequence

from .errors import AIGitAssistantError, ValidationError
from .generator import GenerationService
from .git_context import collect_git_context
from .providers import OpenAICompatibleProvider
from .safety import SafeContext, apply_safe_mode
from .validators import CommitDraft, PRDraft

DEFAULT_API_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODEL = "gpt-4o-mini"


def _add_generation_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-model", "--model", default=DEFAULT_MODEL)
    parser.add_argument(
        "-temperature",
        "--temperature",
        type=float,
        default=0.2,
        help="0.0~2.0 범위 권장",
    )
    parser.add_argument(
        "-max-tokens",
        "--max-tokens",
        type=int,
        default=700,
        help="생성 응답의 최대 토큰 수",
    )
    parser.add_argument(
        "-safe-mode",
        "--safe-mode",
        action="store_true",
        default=True,
        help="민감정보 마스킹 + 최대 10개 파일/200줄 제한 (기본 ON)",
    )
    parser.add_argument(
        "--no-safe-mode",
        dest="safe_mode",
        action="store_false",
        help="마스킹/전송 제한 해제 (주의해서 사용)",
    )
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument(
        "--api-url",
        default=os.environ.get("AI_API_URL", DEFAULT_API_URL),
        help="OpenAI-compatible chat completions endpoint",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python main.py",
        description="Git status/diff를 AI API에 전달해 commit/PR 초안을 생성합니다.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    commit_parser = subparsers.add_parser("commit", help="커밋 메시지 초안 생성")
    _add_generation_options(commit_parser)

    pr_parser = subparsers.add_parser("pr", help="PR 제목/본문 초안 생성")
    _add_generation_options(pr_parser)
    return parser


def _validate_options(args: argparse.Namespace) -> None:
    if not 0.0 <= args.temperature <= 2.0:
        raise ValueError("temperature는 0.0~2.0 범위여야 합니다.")
    if args.max_tokens <= 0:
        raise ValueError("max_tokens는 1 이상이어야 합니다.")
    if args.timeout <= 0:
        raise ValueError("timeout은 0보다 커야 합니다.")


def _prepare_context(args: argparse.Namespace) -> tuple[SafeContext, int, int]:
    context = collect_git_context()
    changed_count = len(context.changed_files)
    diff_lines = context.diff_lines
    print(f"[INFO] Git status 수집 완료: {changed_count}개 파일 변경 감지")
    if context.changed_files:
        print(f"[INFO] 변경 파일: {', '.join(context.changed_files)}")
    print(f"[INFO] Git diff 수집 완료: {diff_lines}줄")

    if not context.has_changes:
        print("[INFO] 변경 사항이 없습니다. 초안을 생성하지 않고 종료합니다.")
        raise SystemExit(0)

    if args.safe_mode:
        safe = apply_safe_mode(context)
        print(
            "[INFO] Safe mode ON: "
            f"masked={safe.masked_items}, truncated={'yes' if safe.truncated else 'no'}"
        )
        return safe, changed_count, diff_lines

    print("[WARN] Safe mode OFF: diff에 민감정보가 없는지 직접 확인하세요.")
    return (
        SafeContext(
            status=context.status,
            diff=context.diff,
            changed_files=context.changed_files,
            masked_items=0,
            truncated=False,
        ),
        changed_count,
        diff_lines,
    )


def _print_commit(draft: CommitDraft, api_calls: int, repaired: bool) -> None:
    print(f"[DONE] 커밋 메시지 생성 완료 (API calls={api_calls}, repaired={str(repaired).lower()})")
    print("--- Commit Message ---")
    print(draft.title)
    for bullet in draft.body:
        print(bullet)
    print("----------------------")


def _print_pr(draft: PRDraft, api_calls: int, repaired: bool) -> None:
    print(f"[DONE] PR 초안 생성 완료 (API calls={api_calls}, repaired={str(repaired).lower()})")
    print("--- PR Title ---")
    print(draft.title)
    print("--- PR Body ---")
    print(draft.body)
    print("---------------")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        _validate_options(args)
        safe_context, _, _ = _prepare_context(args)

        api_key = os.environ.get("AI_API_KEY", "").strip()
        if not api_key:
            print("[ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.", file=sys.stderr)
            print('예: export AI_API_KEY="YOUR_KEY"', file=sys.stderr)
            return 2

        provider = OpenAICompatibleProvider(
            api_key=api_key,
            api_url=args.api_url,
            timeout=args.timeout,
        )
        service = GenerationService(
            provider,
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
        )
        print(
            "[INFO] AI API 요청 중... "
            f"model={args.model}, temperature={args.temperature}, max_tokens={args.max_tokens}"
        )

        if args.command == "commit":
            result = service.generate_commit(safe_context)
            assert isinstance(result.draft, CommitDraft)
            _print_commit(result.draft, result.api_calls, result.repaired)
        else:
            result = service.generate_pr(safe_context)
            assert isinstance(result.draft, PRDraft)
            _print_pr(result.draft, result.api_calls, result.repaired)
        return 0
    except SystemExit:
        raise
    except ValueError as exc:
        print(f"[ERROR] 잘못된 옵션: {exc}", file=sys.stderr)
        return 2
    except ValidationError as exc:
        print(f"[ERROR] AI 출력 형식 검증 실패: {exc}", file=sys.stderr)
        return 3
    except AIGitAssistantError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 3
