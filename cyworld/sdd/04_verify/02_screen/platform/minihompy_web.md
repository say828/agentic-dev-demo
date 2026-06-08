# 미니홈피 웹 프론트 · 검증 (retained)

> proof: `python3 proof/run_proof.py` → 26/26 PASS (백엔드 18 + 웹 8).

| AC | 검증 | 결과 |
| --- | --- | --- |
| AC-W1 | 페이지 서빙 + JS의 `/api/state` 참조 | PASS |
| AC-W2 | 상태 JSON(시드: 잔액 500·today 2·방명록 2) | PASS |
| AC-W3 | 충전→구매 차감 / 잔액부족 에러 표면(서버 유지) | PASS |
| AC-W4 | 일촌 수락 양방향 / 방명록 최신순 / 잘못된 본문 400 | PASS |
| AC-W5 | 방 꾸미기: 벽지 구매가 `room.wallpaper`·보유에 반영 | PASS |
| AC-W6 | 방 꾸미기: BGM 구매가 `room.bgm`에 반영 | PASS |

## 방 꾸미기 ↔ 도토리 연동 (이번 개선)
- 구매 성공 = 보유 지급(AC-7) → `/api/state.room`이 벽지색·BGM·보유목록을 산출.
- 프론트는 `room.wallpaper`로 벽지 `rect#wall` 채움, `room.bgm`으로 BGM 표시,
  `ilchons`로 친구 미니미(`g#friends`)를 방에 렌더. 멱등 재구매는 중복 미반영.

## 검증 방식(정직)
- 브라우저 비가용 → **in-process 서버를 임시 포트로 띄워 UTF-8 urllib 로 호출**하는
  결정적 pytest(`tests/test_web.py`)로 HTTP 계약을 확인.
- 셸 `curl` 은 한글 본문을 CP949로 보내 디코드 실패하므로 검증 클라이언트로 부적합 →
  UTF-8 명시 클라이언트로 대체(디버깅 로그: `02_plan/02_screen/minihompy_web_todos.md`).
- **시각(픽셀) 확인은 사용자 브라우저 책임**(`localhost:8000`). 자동 픽셀 게이트 없음 = 잔여 리스크.

## Residual Risk
- 페이지 HTML 자체의 시각 회귀는 자동 검증 안 함(텍스트 요소 존재만 확인).
- 단일 인메모리 인스턴스 = 멀티 유저/영속 미지원(데모 경계).
