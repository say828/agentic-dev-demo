# 미니홈피 웹 프론트 · todos + 실행 계획

> 상위 명세: `sdd/01_planning/02_screen/minihompy_web.md` (AC-W1~AC-W4).
> 전략: "가장 빠른 프론트 먼저 띄워 디버깅 → 나머지 기능을 얹으며 SDD로 고정".

## Scope
기존 백엔드(dotori/ilchon/today/guestbook)를 **의존성 0 로컬 웹**으로 노출. 단일 HTML
페이지 + JSON API. 도메인 로직은 재구현하지 않고 위임만 한다.

- In: `/` 페이지, `/api/state`, 충전·구매·일촌·방문·방명록 API, in-process pytest 검증.
- Out: 인증/세션, 영속 DB, 멀티 유저, 실 배포(rollout 미요청).

## Acceptance Criteria
- AC-W1~AC-W4 전부 테스트 통과. 백엔드 AC-1~AC-6 회귀 무손상.
- proof 게이트 exit 0(백엔드 16 + 웹 6 = 22) = 완료.

## Execution Checklist (비중첩)
- [x] W1 @frontend-dev 페이지 서빙(`/`) — 미니홈피 풀페이지(CSS+JS)  (AC-W1)
- [x] W2 @backend-dev  상태 API(`/api/state`)  (AC-W2)
- [x] W3 @backend-dev  도토리 충전·구매 위임 + 잔액부족 에러 표면  (AC-W3)
- [x] W4 @backend-dev  일촌·방문·방명록 위임 + 잘못된 본문 400  (AC-W4)
- [x] W5 @test-dev     in-process 서버 pytest(`tests/test_web.py`) → proof 편입

## 디버깅 로그 (실시간)
- curl 로 1차 검증 중 POST 가 `UnicodeDecodeError`로 스레드 크래시 → 원인: **셸 curl 이
  한글 본문을 CP949로 전송**(서버 무결). 조치 2가지:
  1) `_body()` 예외를 400으로 흡수(스레드 비종료) — 견고성 ↑,
  2) 검증을 **UTF-8 명시 파이썬 클라이언트(urllib)** 로 전환 → `tests/test_web.py`로 고정.
- 모듈 싱글톤 때문에 테스트 간 상태 누수 → 픽스처에서 서비스 재생성으로 격리.

## Regression Scope
- direct: 웹 계층(`tests/test_web.py`)
- shared: 백엔드 도메인(`test_dotori/ilchon/today/regression`, `test_screen_parity`) 무변경 확인
- 근거: 프론트는 도메인 위에 얹은 전송 계층 → 도메인 회귀 전체를 같은 proof 게이트로 본다.

## Validation
- `python3 -m pytest tests/test_web.py -q` → 6 passed
- `python3 proof/run_proof.py` → 22/22 PASS
- 수동 시각 확인(사용자): `python3 -m server.web.app` → http://localhost:8000
