# AGENTS.md - B6-2 Independent Review Contract

## Source of Truth

1. `b6-2-mission.pdf`
2. `b6-2-mission.md`
3. 공식 Evaluation - 현재 전용 Source를 찾지 못해 Source Gap
4. `MISSION-WORK-PACKET.md`
5. README / code / tests / evidence

Control Tower baseline: `0d1581b3e82366988f57e1d76da311c028b8e15e`

## Review scope

첫 독립감사는 코드를 수정하지 말고 다음만 보고한다.

- BLOCKER
- MAJOR
- 명백한 Mission 요구 누락
- 테스트 실패
- 문서와 실제 CLI 불일치
- 실제 실행하지 않은 항목을 PASS로 표시한 경우
- API key/token/secret 노출

## Preserve

- 입문자가 설명 가능한 단순한 모듈 분리
- `git status`/`git diff` 범위
- draft 출력까지만 수행하고 push/PR 생성 자동화는 하지 않는 Mission scope
- 최대 1~2회 AI 호출 정책

## Do not

- provider/framework 전면 교체
- 대규모 리팩터링
- Mission에 없는 enterprise architecture 추가
- MINOR/IMPROVEMENT 자동 수정
- secret을 테스트 fixture, 로그, evidence에 넣기

## Test command

```bash
python -m unittest discover -v
```

## Status definitions

- TODO: 미구현/미실행
- IMPLEMENTED: 코드 존재, 실행 검증 전
- TESTED: 자동 테스트 완료
- PASS: 실제 요구 검증 + evidence 완료
- NEEDS-RUNTIME: 실제 API/사용자 환경 확인 필요
- BLOCKED: 외부 조건으로 진행 불가

## Stop condition

BLOCKER=0, MAJOR=0, 자동 검증 가능한 Mission 요구가 통과하면 리뷰를 종료한다. 실제 API 호출은 key/비용/네트워크가 필요하면 `NEEDS-RUNTIME`으로 남긴다.
