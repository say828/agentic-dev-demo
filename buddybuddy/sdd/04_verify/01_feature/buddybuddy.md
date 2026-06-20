# 버디버디 메신저 · 검증 (retained)

> 04_verify: 명령 수준 증거로만 완료를 주장한다.

## 자동화 검증 (pytest)
실행: `python -m pytest -q` (buddybuddy 디렉토리) → **19 passed**.

| AC | 테스트 | 결과 |
| --- | --- | --- |
| AC-1 로그인/오프라인 | `tests/test_presence.py` (4) | pass |
| AC-2 버디 추가·멱등 | `tests/test_buddy.py` (5) | pass |
| AC-3 송수신/양쪽 동일 | `tests/test_message.py::test_send_records_in_thread`,`::test_both_sides_see_same_thread` | pass |
| AC-4 전송 멱등 | `tests/test_message.py::test_send_idempotent`,`::test_same_text_distinct_ids_both_recorded` | pass |
| AC-5 읽음/안읽음 | `tests/test_message.py::test_mark_read_clears_unread` | pass |
| AC-6 대화 격리 | `tests/test_message.py::test_threads_are_isolated` | pass |
| AC-7 대화상대 자동노출 | `tests/test_message.py::test_partners_lists_conversation_others` | pass |
| 회귀 | `tests/test_regression.py::test_end_to_end_two_users` | pass |

## 라이브 송수신 검증 (AC-7, AC-3·4·5·6)
서버 기동(`python -m server.web.app`) 후 두 스모크로 실제 HTTP 검증 — `04_verify/10_test/proof_evidence.md`에 출력 캡처.
- `tmp/smoke.py`(단일 인스턴스 송수신): 현주→민수(seq3) → 안읽음 2 → 응답(seq4) → t1 재전송 replay=True(중복 미기록)
  → 대화 4건 양방향 동일·순번 보존 → 읽음 2 → 안읽음 0 → 다른 상대 대화 분리.
- `tmp/smoke2.py`(두 프론트 라우팅): `/` 로비·`/?me=현주` 단일클라이언트(ME 주입)·`/demo` 라우팅 확인 →
  새 사용자 '지우' 접속·송신 → **버디 미추가인데 현주의 대화 목록에 지우 자동 노출** → 지우↔현주 양방향 대화 일치.

## 선정된 회귀 범위
`02_plan/10_test/regression_verification.md` 기준: message(직접)·buddy/presence(인접)·shared/idem(공유 유틸)
모두 자동화로 커버. `test_regression.py`가 세 서비스 통합 시나리오를 한 번에 검증.

## 잔여 리스크
- UI **픽셀 패리티 미적용**: 원본 디자인 스냅샷 이미지가 없어 AC-7은 "로컬 기동 + 송수신 + 수동 시각 확인"으로 대체.
  cyworld의 Playwright/스냅샷 게이트에 해당하는 자동 시각 게이트는 미구축(데모 범위 밖).
- "실시간"은 1초 폴링으로 흉내 — 표준 라이브러리만 사용(웹소켓 미도입)이라는 의도된 단순화.
- 영속성 없음(프로세스 인메모리) → 재시작 시 대화 초기화. DEV/PROD·스키마 검증은 비대상(로컬 데모).
