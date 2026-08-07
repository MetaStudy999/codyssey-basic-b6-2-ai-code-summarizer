# Automated Test Evidence - B6-2

## Execution

Actual local harness execution against the same source content committed to `mission/b6-2`:

```text
Python 3.13.5
Git 2.47.3
python -m unittest discover -v
```

Result:

```text
Ran 22 tests in 0.069s
OK
```

Additional actual checks:

```text
python -m compileall -q ai_git_assistant main.py
python main.py --help
python main.py commit --help
```

- compileall: PASS
- main help: PASS (`commit`, `pr` exposed)
- commit help: PASS (`model`, `temperature`, `max-tokens`, `safe-mode`, `timeout`, `api-url` exposed)

Non-Git directory actual check:

```text
[ERROR] Git 저장소에서 실행해야 합니다. git status --porcelain=v1 실패: fatal: not a git repository ...
EXIT:3
```

Clean repository actual test confirms:

```text
[INFO] Git status 수집 완료: 0개 파일 변경 감지
[INFO] Git diff 수집 완료: 0줄
[INFO] 변경 사항이 없습니다. 초안을 생성하지 않고 종료합니다.
```

Changed repository missing-key actual test confirms non-zero handling:

```text
[ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.
예: export AI_API_KEY="YOUR_KEY"
```

## Covered behaviors

- real temporary Git repositories: clean / modified / staged
- `git status` / `git diff` collection
- no-change guard
- CLI model / temperature / max_tokens aliases
- commit output contract validation
- PR `Why` / `What` / `How to Test` + bullet validation
- mocked AI response and maximum one repair call
- HTTP 401 / network / timeout provider errors
- safe-mode masking and 10-file / 200-line bounds
- `.env` ignore and placeholder-only example policy

## Boundary

No real AI credential was used in this automated evidence. Live provider generation remains `NEEDS-RUNTIME`; it must not be marked PASS from mocked responses alone.
