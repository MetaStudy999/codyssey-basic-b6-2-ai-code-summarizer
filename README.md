# Codyssey Basic B6-2 - AI Git Commit & PR Draft Generator

Git 저장소의 `git status`와 `git diff`를 수집해 AI API에 전달하고, **커밋 메시지** 또는 **Pull Request 초안**을 터미널에 출력하는 Python CLI입니다.

> 이 도구는 초안만 생성합니다. `git push`나 GitHub PR 자동 생성은 하지 않으며, 결과는 반드시 사람이 검토한 뒤 적용합니다.

## 1. 요구 환경

- Python 3.10+
- Git
- Git이 초기화된 프로젝트 루트
- 실제 AI 호출 시 `AI_API_KEY`
- 기본 구현은 OpenAI-compatible Chat Completions 형식의 REST endpoint를 사용하며 `AI_API_URL`/`--api-url`로 교체 가능

런타임 외부 패키지는 없습니다.

## 2. 설치

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## 3. 환경변수

실제 키를 코드나 `.env`에 커밋하지 않습니다.

```bash
export AI_API_KEY="YOUR_KEY"
# 선택: 다른 OpenAI-compatible endpoint
export AI_API_URL="https://api.openai.com/v1/chat/completions"
```

Windows PowerShell:

```powershell
$env:AI_API_KEY="YOUR_KEY"
$env:AI_API_URL="https://api.openai.com/v1/chat/completions"
```

`.env.example`은 키 이름과 예시만 제공하며 실제 secret은 포함하지 않습니다.

## 4. 사용법

```bash
python main.py --help
python main.py commit
python main.py pr
```

주요 파라미터는 명령별 CLI 옵션으로 바꿀 수 있습니다.

```bash
python main.py commit --model MODEL_NAME --temperature 0.2 --max-tokens 700
python main.py pr -model MODEL_NAME -temperature 0.3 -max-tokens 900
```

지원 옵션:

- `--model`, `-model`: 모델명
- `--temperature`, `-temperature`: 생성 다양성 파라미터(0.0~2.0 검증)
- `--max-tokens`, `-max-tokens`: 최대 생성 토큰
- `--timeout`: API timeout(초)
- `--api-url`: OpenAI-compatible endpoint
- `--safe-mode`, `-safe-mode`: 안전 모드(기본 ON)
- `--no-safe-mode`: 안전 모드 해제

## 5. 처리 흐름

```text
CLI
 -> git status / git diff 수집
 -> 변경 없음이면 즉시 종료(AI 호출 0회)
 -> Safe Mode: 민감정보 마스킹 + 전송량 제한
 -> Commit 또는 PR 전용 prompt 생성
 -> AI REST API 호출
 -> 길이/섹션/bullet 형식 검증
 -> 형식 실패 시 1회 repair 요청
 -> 최종 초안 출력
```

한 실행의 AI 요청은 정상 출력이면 **1회**, 형식 repair가 필요해도 **최대 2회**입니다.

## 6. Safe Mode

기본값은 ON입니다.

- `API_KEY`, `token`, `secret`, `password`, `Authorization: Bearer ...` 형태 마스킹
- 이메일 주소 마스킹
- 변경 파일 최대 10개
- diff 최대 200줄

민감정보 패턴은 완전한 탐지기가 아닙니다. 실제 전송 전에 `git diff`를 직접 확인하는 것이 권장됩니다.

## 7. 출력 예시

### Commit

```text
[INFO] Git status 수집 완료: 2개 파일 변경 감지
[INFO] 변경 파일: app.py, README.md
[INFO] Git diff 수집 완료: 64줄
[INFO] Safe mode ON: masked=0, truncated=no
[INFO] AI API 요청 중... model=MODEL_NAME, temperature=0.2, max_tokens=700
[DONE] 커밋 메시지 생성 완료 (API calls=1, repaired=false)
--- Commit Message ---
feat: add Git change summary generation
- Update ai_git_assistant/git_context.py to collect status and diff
----------------------
```

### Pull Request

```text
[DONE] PR 초안 생성 완료 (API calls=1, repaired=false)
--- PR Title ---
feat: add AI-assisted Git draft generation
--- PR Body ---
## Why
- Reduce repeated manual drafting from the current Git changes.
## What
- Collect git status/diff and generate structured commit/PR drafts.
## How to Test
- Run the unit test suite and verify the CLI output format.
---------------
```

AI가 실제로 모르는 테스트 결과를 만들어내지 않도록 prompt에서 **Git context에 없는 사실은 쓰지 말 것**을 명시합니다.

## 8. 오류 처리

변경 사항 없음:

```text
[INFO] 변경 사항이 없습니다. 초안을 생성하지 않고 종료합니다.
```

API Key 없음:

```text
[ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.
예: export AI_API_KEY="YOUR_KEY"
```

네트워크/인증/API 오류는 HTTP 상태나 원인을 포함해 사용자 메시지로 출력하고 비정상 종료 코드(`3`)를 반환합니다.

## 9. 테스트

외부 API 호출 없이 표준 라이브러리 `unittest`로 Git parsing, prompt construction, mocked AI response, CLI option, 오류/timeout 계층, Safe Mode, secret 정책을 검증합니다.

```bash
python -m unittest discover -v
```

테스트 범위:

- clean repo no-change guard
- modified/staged `git status`/`git diff`
- `model`/`temperature`/`max_tokens` 옵션
- commit/PR output contract
- malformed AI response 1회 repair
- HTTP auth/network/timeout error
- Safe Mode masking/truncation
- `.env` ignore 정책

## 10. 실제 API Runtime 확인

실제 provider의 API key/비용/네트워크가 필요한 항목은 자동 테스트와 구분합니다.

```bash
# 1) 이 저장소 또는 테스트용 Git repo에서 의미 있는 파일 1개 수정
export AI_API_KEY="YOUR_KEY"
python main.py commit --model MODEL_NAME
python main.py pr --model MODEL_NAME
```

정상 판정:

- `git status`/`git diff` 수집 로그가 출력됨
- commit title이 1줄이고 72자 이하
- PR title이 80자 이하
- PR body에 `Why`, `What`, `How to Test`가 있고 각 섹션에 bullet이 있음
- API call count가 1~2회
- secret이 터미널/evidence에 노출되지 않음

## 11. 프로젝트 구조

```text
main.py
ai_git_assistant/
  cli.py          # CLI / 사용자 출력 / 오류 코드
  git_context.py  # git status/diff 수집
  safety.py       # secret masking / diff 제한
  prompts.py      # commit/PR prompt contract
  providers.py    # AI REST provider abstraction
  generator.py    # 1회 생성 + 필요 시 1회 repair
  validators.py   # title/section/bullet 검증
tests/
docs/
MISSION-WORK-PACKET.md
AGENTS.md
```

## 12. 미션 범위와 비범위

포함:

- Git 변경사항 수집
- AI API를 통한 commit/PR draft 생성
- CLI generation parameter
- prompt 최적화와 output validation
- 환경변수 secret 관리
- Safe Mode

미포함:

- `git push` 자동 실행
- GitHub API를 이용한 PR 자동 생성
- AI 결과를 자동 커밋/자동 병합

## 13. 학습 자료

- [`docs/learning.md`](docs/learning.md): REST AI API, `temperature`/`max_tokens`, Git-to-prompt 흐름, prompt contract, 결과 검증을 구현 코드와 연결해 설명합니다.
- [`MISSION-WORK-PACKET.md`](MISSION-WORK-PACKET.md): G1 Source 상태, 요구사항 추적, Test/Runtime/Evidence 계획을 기록합니다.
