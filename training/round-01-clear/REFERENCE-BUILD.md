# B6-2 R01 — Reference Build

## 목적

공식 Mission/Evaluation을 기준으로 **Git 변경사항을 수집해 AI API에 전달하고 Commit Message와 Pull Request 초안을 생성하는 Python CLI**의 Reference Complete Version을 준비합니다.

Phase A에서는 실제 API Key를 입력하거나 유료 AI API를 호출하지 않습니다. API Runtime, 실제 생성 품질, 실제 Commit/PR 적용과 Evidence는 Phase C에서 확인합니다.

## Source of Truth

1. `b6-2-mission.pdf`
2. `b6-2-mission.md`
3. `b6-2-evaluation.md`

## Reference 설계 결정

- Python 3.10+
- 실행: `python -m git_ai <commit|pr> [options]`
- Git root에서 실행
- 수집:
  - `git status --short`
  - `git diff`
  - `git diff --cached`
- 변경이 없으면 AI 호출 없이 `변경 사항이 없습니다.` 출력 후 종료
- 실제 Secret:
  - `AI_API_KEY` 환경변수
  - `.env`/Key 하드코딩 금지
- Endpoint:
  - `AI_API_URL` 환경변수로 Runtime provider endpoint 지정
  - Reference client는 OpenAI-compatible `choices[0].message.content`와 일반 `output_text` 응답을 해석
- CLI 옵션:
  - `--model`
  - `--temperature`
  - `--max-tokens`
- `commit` 결과:
  - Commit 제목 1줄 필수
  - 필요 시 본문 bullet
- `pr` 결과:
  - PR 제목
  - `## Why`
  - `## What`
  - `## How to Test`
  - 각 section 최소 1 bullet
- API/network/auth/JSON/format 오류는 원인을 포함한 사용자용 오류로 처리

## Reference Complete Path

1. Git repository 확인
2. status/diff 수집
3. no-change 종료
4. prompt context 구성
5. API client + env Secret
6. model/temperature/max-tokens CLI
7. Commit prompt + 결과 검증
8. PR prompt + 결과 검증
9. 오류 처리
10. 자동 tests/verify
11. 실제 API Runtime
12. 실제 Commit/PR 적용
13. Evaluation/Evidence
14. CLEAR

## 현재 판정

**Reference Build 진행 중 / Mission 상태 ⬜ NOT STARTED / 실제 AI API Runtime 미시작**
