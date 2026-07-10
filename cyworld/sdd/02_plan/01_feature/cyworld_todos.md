# 싸이월드 미니홈피 · todos + 실행 계획

> S08 02_plan 산출물. 상위 명세: `sdd/01_planning/01_feature/cyworld_feature_spec.md`.

## Scope
미니홈피를 **도토리 경제(충전·구매·멱등) + 일촌 그래프(신청·수락 양방향) + 투데이 멱등
집계 + 미니홈피 화면 parity**까지 백엔드만 로컬로 구현·검증. 방명록은 회귀로 보호.

- In: 도토리 충전/구매/멱등, 일촌 신청·수락, 투데이 카운트, minihompy 화면.
- Out: 실 결제(PG)·실 계정·BGM 스트리밍, 사진 업로드, 배포(rollout 미요청).

## Assumptions
- 강의 데모용 가상 서비스 — 실 계정·결제 없음. 모든 상태 인메모리.
- 도토리/일촌/투데이는 순수 상태 전이 → 결정적 검증(실시간·난수·외부 PG 비의존).
- 화면 정합은 환경 제약상 Playwright exactness 대신 HTML 스냅샷 parity로 대체.

## Acceptance Criteria
- AC-1~AC-6 (`cyworld_feature_spec.md`) 전부 테스트 통과.
- 회귀(방명록) green. proof 게이트 exit 0 = 완료.

## Execution Checklist (비중첩 · 한 번에 하나만 in-progress)
- [x] T1 @backend-dev  도토리 충전·구매·잔액부족·멱등 — `server/contexts/cyworld/dotori.py` (+ `shared/idem.py`)  (AC-1·2·3)
- [x] T2 @backend-dev  일촌 신청·수락·양방향·멱등 — `server/contexts/cyworld/ilchon.py`  (AC-4)
- [x] T3 @backend-dev  투데이 멱등 방문 집계 — `server/contexts/cyworld/today.py`  (AC-5)
- [x] T4 @frontend-dev minihompy 메인 화면 — `server/contexts/cyworld/screens.py`  (AC-6)
- [x] T5 @test-dev     proof 게이트 + UI parity — `tests/`, `run_ui_parity.py`

## Regression Scope
- direct: 도토리·일촌·투데이·미니홈피 화면
- shared: 방명록(`server/contexts/cyworld/guestbook.py`) — 미니홈피 공통 surface
- 근거: `sdd/02_plan/10_test/regression_verification.md`

## Current Notes
- 도토리 구매 멱등: 성공만 캐시(잔액부족 거부는 캐시하지 않음) → 재시도 가능.
- rollout 미요청 — `05_operate`는 미수행 상태로만 기록.

## Validation
- `python3 -m compileall -q server` (build)
- `python3 proof/run_proof.py` → 전건 PASS
- `python3 sdd/99_toolchain/01_automation/run_ui_parity.py` → ui_parity 1/1
