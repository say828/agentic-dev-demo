# 싸이월드 미니홈피 · current-state

> 03_build: Overwrite Rule(지금 상태 1벌).

## Absorbed Planning
- `01_planning/01_feature/cyworld_feature_spec.md` (AC-1~AC-7)
- `02_plan/01_feature/cyworld_todos.md` (T1~T5)

## Runtime Assembly
- `DotoriService.charge/purchase` → 잔액 차감 + 잔액부족 거부 + 주문 멱등 + 보유 지급(`owned`)
- 웹 `room_of(owner)` → 보유 아이템을 미니룸 벽지·BGM으로 매핑(도토리↔방 꾸미기 연동)
- `IlchonService.request → accept` → 양방향 일촌(`are_ilchon`/`ilchons`)
- `TodayService.visit` → (owner, visitor, day) 멱등 카운트 / `today_count`·`total_count`
- `GuestbookService` → 방명록 최신순 + 비밀글 가시성(회귀 surface)
- 화면: `screens.render("minihompy")` → 미니홈피 메인 HTML

## Modules
| 모듈 | 책임 | AC |
| --- | --- | --- |
| `contexts/cyworld/dotori.py` | 충전·구매·잔액부족·멱등·보유지급(`owned`) | 1·2·3·7 |
| `contexts/cyworld/ilchon.py` | 일촌 신청·수락·양방향 | 4 |
| `contexts/cyworld/today.py` | 투데이 멱등 집계 | 5 |
| `contexts/cyworld/screens.py` | 미니홈피 메인 화면 | 6 |
| `contexts/cyworld/guestbook.py` | 방명록(회귀) | - |
| `shared/idem.py` | idempotency_key | 3·4·5 |

## Current Behavior
도토리 충전→구매(잔액부족 거부·이중결제 멱등·보유 지급) / 일촌 신청→수락 양방향 /
투데이는 같은 방문자·같은 날 1회 집계(TOTAL 누적). 미니홈피 메인은 승인 스냅샷과 일치.
웹 프론트에서 구매한 벽지/BGM이 미니룸에 반영되고, 일촌 수락 시 친구 미니미가 방에 등장.
기분 변경 시 창문 날씨(맑음/흐림/비)와 미니미 표정이 함께 바뀐다(`mood_of` / `/api/mood`).
