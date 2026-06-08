# 싸이월드 미니홈피 · Acceptance Criteria (EARS)

> 01_planning: 요구사항을 검증 가능한 EARS로 정제. 이 명세가 가드레일.

**AC-1** When 사용자가 도토리를 충전하면, the system shall 충전액(양수)을 잔액에 더한다.

**AC-2** While 잔액이 가격 이상일 때, when 아이템을 구매하면, the system shall 가격만큼
차감한다. 잔액이 부족하면 the system shall 구매를 거부하고 잔액을 보존한다.

**AC-3** When 같은 주문(order_id)이 재요청되면, the system shall 멱등성을 보장해
한 번만 결제한다(재요청은 replay).

**AC-4** When A가 B에게 일촌을 신청하고 B가 수락하면, the system shall 양방향 일촌을
성립시킨다. 수락 전에는 the system shall 일촌으로 보지 않는다. 같은 신청 반복은 멱등.

**AC-5** When 같은 방문자가 같은 날 미니홈피를 방문하면, the system shall TODAY를 한 번만
집계한다(누적 TOTAL은 별도로 증가하지 않는다).

**AC-6(화면)** The minihompy 메인 화면은 shall 승인된 디자인 스냅샷과 일치한다(UI parity).

## 검증 매핑

| AC | 테스트 |
| --- | --- |
| AC-1 | `tests/test_dotori.py::test_charge_and_balance` |
| AC-2 | `tests/test_dotori.py::test_purchase_deducts`, `::test_purchase_insufficient` |
| AC-3 | `tests/test_dotori.py::test_purchase_idempotent` |
| AC-4 | `tests/test_ilchon.py` |
| AC-5 | `tests/test_today.py` |
| AC-6 | `tests/test_screen_parity.py` + `99_toolchain/01_automation/run_ui_parity.py` |
| 회귀 | `tests/test_regression.py` (방명록) |
