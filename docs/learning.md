# B6-2 Learning Guide

## 오늘의 목표

Git 변경 사항을 AI 입력 컨텍스트로 바꾸고, AI의 자유로운 텍스트 출력을 **검증 가능한 Commit/PR 계약**으로 제어하는 전체 흐름을 설명할 수 있게 된다.

## 1. REST AI API 요청-응답 흐름

`ai_git_assistant/providers.py`의 `OpenAICompatibleProvider`는 다음 순서로 동작한다.

```text
prompt
  -> JSON request(model, temperature, max_tokens, messages)
  -> HTTP POST + Authorization header
  -> JSON response
  -> choices[0].message.content 추출
  -> 사용자용 draft 반환
```

핵심은 API key를 코드에 쓰지 않고 `AI_API_KEY` 환경변수에서 읽는 것이다. 키는 인증 수단이므로 Git history, 로그, evidence에 남기지 않는다.

## 2. model / temperature / max_tokens

- `model`: 어떤 모델을 호출할지 선택한다.
- `temperature`: 생성 결과의 다양성을 조절한다. 이 도구는 일관된 개발 문구가 목적이므로 기본값을 낮게 둔다.
- `max_tokens`: 응답 상한을 정해 과도한 길이와 비용을 제한한다.

CLI에서 바꿀 수 있게 한 이유는 **코드를 수정하지 않고도 생성 품질/비용을 실험**하기 위해서다.

## 3. Git status와 diff를 프로그램 입력으로 연결하기

`git_context.py`는 subprocess로 다음 결과를 수집한다.

```text
git status --porcelain=v1
  -> 어떤 파일이 변경되었는가?

git diff
git diff --cached
  -> 파일 내부가 어떻게 바뀌었는가?
```

`status`가 비어 있으면 변경 사항이 없으므로 AI API를 호출할 이유가 없다. 이 guard는 비용과 불필요한 네트워크 호출을 줄인다.

## 4. Safe Mode가 필요한 이유

`git diff`에는 secret, 이메일, 개인정보가 섞일 수 있다. `safety.py`는 전송 전에 다음 처리를 한다.

1. 흔한 key/token/password 패턴 마스킹
2. 이메일 마스킹
3. 최대 10개 파일
4. 최대 200줄

마스킹은 보조 안전장치다. 가장 확실한 방법은 사용자가 전송 전 diff를 검토하고 secret 파일 자체를 Git에서 제외하는 것이다.

## 5. Prompt Contract

AI는 자연어만 요청하면 형식이 흔들릴 수 있다. 그래서 `prompts.py`는 출력 계약을 명시한다.

Commit:

```text
TITLE: <=72 chars
BODY:
- 1~2 bullets
```

PR:

```text
PR_TITLE: <=80 chars
PR_BODY:
## Why
- bullet
## What
- bullet
## How to Test
- bullet
```

즉, prompt는 단순한 질문이 아니라 **출력 스키마를 자연어로 정의한 인터페이스 계약**이다.

## 6. 왜 생성 결과를 다시 검증하는가

LLM 출력은 확률적이므로 prompt를 잘 써도 형식 위반이 생길 수 있다. `validators.py`는 다음을 코드로 검사한다.

- commit title 72자 이하
- PR title 80자 이하
- required section 존재 및 순서
- 각 section bullet 존재

검증 실패 시 `generator.py`가 오류 원인을 포함한 repair prompt로 **딱 1회** 다시 요청한다. 따라서 한 명령의 API 요청은 최대 2회다.

## 7. 전체 흐름을 자기 말로 설명하기

```text
사용자 명령
 -> Git status/diff
 -> 변경 없음 guard
 -> Safe Mode
 -> Commit/PR prompt
 -> REST AI API
 -> 응답 parser/validator
 -> 필요 시 1회 repair
 -> terminal draft
 -> 사용자 검토/복사
```

이 구조에서 중요한 분리는 다음과 같다.

- Git 수집: `git_context.py`
- 안전 처리: `safety.py`
- prompt: `prompts.py`
- API: `providers.py`
- 품질 검증: `validators.py`
- 전체 생성 정책: `generator.py`
- 사용자 경험: `cli.py`

## 8. 확인 문제

1. `git status`와 `git diff`는 각각 어떤 정보를 제공하는가?
2. clean repo에서 API를 호출하지 않는 이유는 무엇인가?
3. `temperature`를 너무 높게 하면 개발 문구 자동화에 어떤 위험이 있는가?
4. PR prompt에 `Why/What/How to Test`를 명시하는 이유는 무엇인가?
5. prompt만 믿지 않고 validator가 필요한 이유는 무엇인가?
6. Safe Mode가 있어도 사람이 diff를 검토해야 하는 이유는 무엇인가?
