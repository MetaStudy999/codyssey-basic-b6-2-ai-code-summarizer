# Evidence Plan

실제 실행하지 않은 출력은 PASS evidence로 사용하지 않는다.

## Automated evidence

- `python -m unittest discover -v`
- 테스트 결과는 Git parsing, prompt construction, mocked AI response, CLI option, error handling, Safe Mode, secret policy를 검증한다.

## Human Runtime evidence - pending

실제 API key/네트워크/비용 승인이 필요한 아래 항목은 `NEEDS-RUNTIME`이다.

1. 실제 변경이 있는 Git repo에서 `python main.py commit --model <model>` 실행
2. 실제 변경이 있는 Git repo에서 `python main.py pr --model <model>` 실행
3. commit title/body 형식 확인
4. PR Why/What/How to Test + 각 bullet 확인
5. API 호출 실패 또는 잘못된 key 상황의 사용자 오류 메시지 확인
6. 출력/스크린샷에 API key/token이 노출되지 않았는지 확인

Evidence를 추가할 때 secret 값 자체는 절대 기록하지 않는다.
