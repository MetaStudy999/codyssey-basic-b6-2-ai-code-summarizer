# B6-2 Mission Work Packet - Confirmed at G1 SOURCE

## 1. Identity

- Mission: `B6-2`
- Title: 내가 고친 코드 설명을 AI가 대신 써주는 도우미 만들기
- Mission repository: `MetaStudy999/codyssey-basic-b6-2-ai-code-summarizer`
- Control Tower: `MetaStudy999/codyssey-basic` - READ ONLY
- Control Tower frozen baseline: `0d1581b3e82366988f57e1d76da311c028b8e15e`
- Mission repository baseline: `8e12cbcc80956f0192469462ddf015e1b6055ce5`
- Active wave: `20260808-01`

## 2. Source Inventory

| Source | State | Use |
|---|---|---|
| `b6-2-mission.pdf` (8 pages) | VALID | Primary Mission Source |
| `b6-2-mission.md` | VALID / DUPLICATE transcription | Secondary Mission Source |
| Dedicated B6-2 official Evaluation/rubric in mission repo | MISSING | Source Gap |
| Dedicated B6-2 Evaluation located by Control Tower repository search | MISSING | Source Gap |
| Dedicated B6-2 Evaluation located by available uploaded-file search | MISSING | Source Gap |
| 2026 Orientation material | VALID but high-level | Confirms B6-2 is required Cloud & AI API mission; not a substitute Evaluation |

### Source Mode

- Mode: `MISSION-LED`
- Confidence: `MEDIUM`
- Gap: dedicated official Evaluation/평가문항 was not located.
- Rule: Evaluation criteria are **not inferred** from README/code/general knowledge. If an official Evaluation appears later, G1 mapping must be reopened and diffed.

## 3. Mission Contract - Confirmed Requirements

| ID | Requirement | Source |
|---|---|---|
| REQ-B6-2-001 | Git-initialized project root에서 CLI 실행 | Mission §4.1 |
| REQ-B6-2-002 | `git status`로 변경 파일 상태 수집 | Mission §4.1 |
| REQ-B6-2-003 | `git diff`로 변경 내용 수집 | Mission §4.1 |
| REQ-B6-2-004 | 변경 없음 메시지 후 종료 | Mission §4.1 |
| REQ-B6-2-005 | API key는 환경변수, 하드코딩 금지 | Mission §4.2/§7 |
| REQ-B6-2-006 | AI API 실패 시 원인을 포함한 사용자 오류 | Mission §4.2 |
| REQ-B6-2-007 | model/temperature/max_tokens CLI option + defaults | Mission §4.2 |
| REQ-B6-2-008 | `commit` 명령 -> 변경 기반 1줄 title 출력 | Mission §4.3 |
| REQ-B6-2-009 | commit body 사용 시 파일/모듈 또는 1~2개 핵심 bullet | Mission §4.3 |
| REQ-B6-2-010 | `pr` 명령 -> 1줄 title + body | Mission §4.4 |
| REQ-B6-2-011 | PR `Why`/`What`/`How to Test` + 섹션별 bullet | Mission §4.4 |
| REQ-B6-2-012 | commit title 최대 72자(50자 권장), PR title 최대 80자 검증 | Mission §4.5 |
| REQ-B6-2-013 | 최종 출력은 헤더/구분선으로 검토 가능 | Mission §4.5 |
| REQ-B6-2-014 | README 설치/환경변수/명령/출력/운영 주의사항 | Mission §4.6 |
| REQ-B6-2-015 | Python 3.10+, 터미널 프로그램 | Mission §6 |
| REQ-B6-2-016 | commit/pr 자동 원격 적용하지 않고 draft까지만 | Mission §7 |
| REQ-B6-2-017 | Safe Mode: masking 또는 diff 제한 중 1개 이상 | Mission §7 |
| REQ-B6-2-018 | 실제 생성 결과는 사람이 검토 후 적용 | Mission §7 |

## 4. Evaluation Mapping

Dedicated Evaluation Source가 없으므로 `UNVERIFIED` 상태다. 현재 G2/G3는 Mission-derived acceptance만 사용한다.

## 5. Repository Baseline

G1 조사 시 root에는 다음 3개만 존재했다.

```text
README.md
b6-2-mission.md
b6-2-mission.pdf
```

즉 기존 Python CLI, Git integration layer, AI provider abstraction, prompts, tests, `.env` policy는 **없었다**. G2는 신규 최소 충분 구현이다.

## 6. Architecture / Mission-specific TOC

```text
CLI
├── Git Context Collector
│   ├── git status
│   ├── git diff
│   └── no-change guard
├── Safe Mode
│   ├── masking
│   └── 10 files / 200 lines bound
├── Prompt Builder
│   ├── Commit contract
│   └── PR contract
├── AI Provider abstraction
│   └── configurable OpenAI-compatible REST adapter
├── Generation Service
│   └── max 1 repair -> max 2 API calls
└── Validators / terminal draft output
```

## 7. Scope / Non-scope

### Scope

- Python CLI
- Git status/diff context
- AI API REST adapter
- commit/PR prompt engineering
- output validation
- safe mode / environment secret policy
- unit/integration-style tests with mocked API

### Non-scope

- git push automation
- GitHub PR creation API
- automatic commit/merge
- bonus convention config / real cross-repo PR unless separately requested

## 8. Dependency / Drift Check

- Official predecessor dependency: `NONE` found in Mission Source.
- Runtime dependencies: Git, Python 3.10+, actual AI provider credential/network only for G5.
- Control Tower drift: frozen baseline remains the execution baseline.

## 9. Agent Routing

- Primary builder: ChatGPT in this Workcell.
- Automated harness: standard-library `unittest` + real temporary Git repositories + mocked AI HTTP.
- Independent reviewer: one minimal review after G3, using root `AGENTS.md` contract.
- Human Runtime: only actual AI key/provider/network check if required.

## 10. Test Plan

- non-Git failure
- clean repo no-change / API not required
- modified + staged status/diff collection
- commit output title/body contract
- PR title/Why/What/How to Test/bullet contract
- model/temperature/max_tokens option parsing/default
- malformed AI output -> one repair call
- missing key
- HTTP auth/network/timeout errors
- safe mode masking/truncation
- `.env` ignore/placeholder policy
- README commands vs parser contract

## 11. Runtime Plan

`NEEDS-RUNTIME` only for actual provider call:

1. Create/keep one meaningful Git change.
2. Set `AI_API_KEY` without exposing it.
3. Run `commit` once.
4. Run `pr` once.
5. Confirm output contract and call count.
6. Capture sanitized evidence.

## 12. Evidence Plan

- Automated: test command/output.
- Runtime: sanitized terminal output/screenshot only.
- Never store API key/token values.

## 13. G1-G8 Checklist

- [x] G1 SOURCE - Mission VALID, Evaluation MISSING, `MISSION-LED`, MEDIUM confidence
- [ ] G2 BUILD
- [ ] G3 TEST
- [ ] G4 REVIEW
- [ ] G5 RUNTIME
- [ ] G6 EVIDENCE
- [ ] G7 LEARN
- [ ] G8 MERGE

## 14. STOP Rule

Mission requirements satisfied + BLOCKER=0 + MAJOR=0 + required tests + actual required runtime/evidence -> stop. MINOR/IMPROVEMENT does not delay completion.

## 15. Handoff Contract

After G8, repository root must contain `HANDOFF.md` and `mission-result.yaml` with final SHA/PR, Source Mode/Gap, Gate results, tests, runtime/evidence, reviewer findings, and remaining backlog. Control Tower is not modified by this Workcell.
