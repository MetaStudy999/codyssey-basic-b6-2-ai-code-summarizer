# B6-2 Mission Work Packet

## 1. Identity

- Mission: `B6-2`
- Title: 내가 고친 코드 설명을 AI가 대신 써주는 도우미 만들기
- Mission repository: `MetaStudy999/codyssey-basic-b6-2-ai-code-summarizer`
- Work branch: `mission/b6-2`
- Control Tower: `MetaStudy999/codyssey-basic` — **READ ONLY**
- Frozen Control Tower baseline: `0d1581b3e82366988f57e1d76da311c028b8e15e`
- Mission repository baseline: `8e12cbcc80956f0192469462ddf015e1b6055ce5`
- Active wave: `20260808-01`

## 2. Source Inventory

| Source | State | Use |
|---|---|---|
| `b6-2-mission.pdf` (8 pages) | VALID | Primary Mission Source |
| `b6-2-mission.md` | VALID / DUPLICATE transcription | Secondary Mission Source |
| Dedicated B6-2 official Evaluation/rubric in mission repo | MISSING | Source Gap |
| Dedicated B6-2 Evaluation in Control Tower search | MISSING | Source Gap |
| Dedicated B6-2 Evaluation in available uploaded-file search | MISSING | Source Gap |
| 2026 Orientation material | VALID, high-level only | Confirms B6-2 required/40h; not Evaluation substitute |

### Source decision

- Mode: `MISSION-LED`
- Confidence: `MEDIUM`
- Evaluation status: `UNVERIFIED / MISSING`
- Gap: dedicated official Evaluation/평가문항 was not located.
- Rule: Evaluation criteria are not inferred. If an official Evaluation appears, G1 mapping is reopened only as needed.

## 3. Mission Contract / Requirement Traceability

| ID | Confirmed requirement | Implementation / evidence |
|---|---|---|
| REQ-B6-2-001 | Git-initialized root에서 CLI 실행 | `git_context.py`; non-Git actual check |
| REQ-B6-2-002 | `git status` 수집 | `collect_git_context`; temp-repo tests |
| REQ-B6-2-003 | `git diff` 수집 | unstaged + staged diff; temp-repo tests |
| REQ-B6-2-004 | 변경 없음 안내 후 종료 | clean-repo actual test, API key 불필요 |
| REQ-B6-2-005 | API key 환경변수 / 하드코딩 금지 | `AI_API_KEY`; `.gitignore`; `.env.example` |
| REQ-B6-2-006 | API 실패 원인 안내 | HTTP/network/timeout/provider errors + tests |
| REQ-B6-2-007 | model/temperature/max_tokens CLI options | aliases/defaults + parser tests |
| REQ-B6-2-008 | `commit` -> 변경 기반 1줄 title | prompt + validator + mocked generation test |
| REQ-B6-2-009 | commit body 사용 시 품질 기준 | 1–2 bullets required by this implementation |
| REQ-B6-2-010 | `pr` -> 1줄 title + body | prompt + validator + mocked generation test |
| REQ-B6-2-011 | PR Why/What/How to Test + bullets | exact headers/order/bullet validation |
| REQ-B6-2-012 | title/PR 형식 및 길이 검증 | commit <=72, PR <=80, repair once |
| REQ-B6-2-013 | 검토 가능한 구분 출력 | terminal headers/separators |
| REQ-B6-2-014 | README 필수 항목 | install/env/commands/output/security/cost/runtime |
| REQ-B6-2-015 | Python 3.10+, terminal | Python CLI; standard library runtime |
| REQ-B6-2-016 | draft까지만; 원격 자동 반영 금지 | no push/PR creation implementation |
| REQ-B6-2-017 | Safe Mode 1개 이상 | masking + 10-file metadata / 200-line diff bound |
| REQ-B6-2-018 | 사람 최종 검토 | prompt/output/README explicitly preserve human review |

## 4. Evaluation Mapping

Dedicated official Evaluation source is missing. Evaluation mapping remains `UNVERIFIED`; no invented criteria are used as PASS evidence.

## 5. Repository Baseline

At G1 the root contained only:

```text
README.md
b6-2-mission.md
b6-2-mission.pdf
```

There was no existing Python CLI, Git integration layer, AI provider abstraction, prompts, tests, or `.env` policy. G2 therefore created a minimum-sufficient implementation from scratch.

## 6. Architecture / Mission-specific TOC

```text
CLI
├── Git Context Collector
│   ├── git status
│   ├── git diff / git diff --cached
│   └── no-change guard
├── Safe Mode
│   ├── secret/email masking
│   └── 10 files / 200 lines bound
├── Prompt Builder
│   ├── Commit contract
│   └── PR contract
├── AI Provider abstraction
│   └── configurable OpenAI-compatible REST adapter
├── Generation Service
│   └── one initial call + max one repair
└── Validators / terminal draft output
```

## 7. Scope / Non-scope

### Scope

- Python CLI
- Git status/diff context
- AI REST provider adapter
- commit/PR prompt engineering
- output validation/repair
- safe mode / environment secret policy
- unit/integration-style tests with real temporary Git repos and mocked AI HTTP
- README / learning / evidence documentation

### Non-scope

- `git push` automation
- GitHub PR creation API from the B6-2 tool
- automatic commit/merge
- bonus convention configuration or cross-repo PR

## 8. Dependency / Drift Check

- Official predecessor dependency: `NONE` found in Mission Source.
- Runtime dependency: Git, Python 3.10+, and an actual AI provider credential/network for G5.
- Control Tower drift: frozen baseline retained; Control Tower was not modified.

## 9. Agent Routing / Review

- Primary builder: ChatGPT Workcell.
- Automated harness: stdlib `unittest`, temporary real Git repositories, mocked HTTP/provider responses.
- ChatGPT self review: `BLOCKER=0`, `MAJOR=0`; see `docs/review.md`.
- Independent reviewer: **not executed** because no separate Codex/Copilot reviewer surface is available in this session. This is recorded rather than fabricated.
- Human Runtime: required only for real provider generation.

## 10. Test Result

Actual local harness:

```text
python -m unittest discover -v
Ran 22 tests in 0.069s
OK
```

Additional actual checks:

- `python -m compileall -q ai_git_assistant main.py` — PASS
- `python main.py --help` — PASS
- `python main.py commit --help` — PASS
- non-Git directory — expected error, exit 3
- clean Git repo — no-change exit 0, no API key required
- changed Git repo with missing key — expected error, exit 2

Evidence: `docs/evidence/automated-test.md`.

## 11. Runtime Plan

State: `NEEDS-RUNTIME`.

A real AI credential is intentionally not stored or requested in repository content. Required final smoke flow:

1. Keep one meaningful local Git modification.
2. Set `AI_API_KEY` locally without exposing it.
3. Run `python main.py commit --model <MODEL>`.
4. Run `python main.py pr --model <MODEL>`.
5. Confirm title/section/bullet contract and API call count <=2.
6. Capture sanitized evidence only.

## 12. Evidence Plan / Current Evidence

- Automated evidence: **TESTED** — `docs/evidence/automated-test.md`
- Review evidence: **PARTIAL** — `docs/review.md`
- Live provider evidence: **NEEDS-RUNTIME**
- Secret values must never appear in evidence.

## 13. G1-G8 Status

| Gate | State | Note |
|---|---|---|
| G1 SOURCE | PASS | Mission VALID; Evaluation MISSING; MISSION-LED / MEDIUM |
| G2 BUILD | TESTED | minimum-sufficient implementation complete |
| G3 TEST | PASS | 22 tests + compile/help/runtime-negative checks |
| G4 REVIEW | PARTIAL | self-review BLOCKER=0/MAJOR=0; independent agent not available |
| G5 RUNTIME | NEEDS-RUNTIME | real AI provider key/network needed |
| G6 EVIDENCE | PARTIAL | automated evidence complete, live generation evidence pending |
| G7 LEARN | PASS | `docs/learning.md` complete and implementation-aligned |
| G8 MERGE | TODO | Draft PR #1 remains open until completion gates close |

## 14. STOP Rule

Stop only after confirmed Mission requirements + required runtime/evidence + `BLOCKER=0` + `MAJOR=0`. Do not delay for MINOR/IMPROVEMENT. Do not claim Evaluation PASS while the official Evaluation remains missing.

## 15. Handoff Contract

After G8, create root `HANDOFF.md` and `mission-result.yaml` with final commit/PR/merge state, Source Mode/Gap, G1–G8 results, tests, runtime/evidence, review findings, and remaining risks. The Control Tower remains untouched by this Workcell.
