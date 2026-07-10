# 미니홈피(Cyworld) 기능 명세 — EARS Acceptance Criteria

> Java 포팅판. 원본 Python 데모(server/contexts/cyworld + server/web/app.py)의 동작을
> 그대로 옮긴 표준 JDK 기반(`com.sun.net.httpserver`) 구현이다. 외부 런타임 의존성 0.

## 0. 범위 / 결정성 원칙

- 도메인 로직(도토리·일촌·투데이·방명록)은 순수 인메모리 + 멱등 처리로 **결정적**이다.
  (외부 PG·실시간·난수 비의존)
- 웹 프론트는 의존성 0의 단일 HTML 페이지(미니홈피)와 JSON API로 도메인을 노출한다.

## 1. 도토리 (가상화폐) — DotoriService

- **EARS-DOT-1 (Ubiquitous):** The 도토리 service shall track each user's balance starting at 0.
- **EARS-DOT-2 (Event):** When `charge(user, amount)` is called with `amount > 0`, the service shall
  increase the user's balance by `amount` and return the new balance.
- **EARS-DOT-3 (Unwanted):** If `charge` is called with `amount <= 0`, then the service shall reject it
  with an error (`IllegalArgumentException`, "충전액은 양수여야 한다").
- **EARS-DOT-4 (Event):** When `purchase(user, item, price, orderId)` is called and balance ≥ price,
  the service shall deduct `price`, grant `item` to the user, and return `status="purchased"` with the
  remaining balance.
- **EARS-DOT-5 (Unwanted):** If `purchase` is called and balance < price, then the service shall raise
  `InsufficientDotori` and shall NOT change balance, grant the item, or cache the result (재시도 가능).
- **EARS-DOT-6 (State/Idempotency):** While an `orderId` (or derived `(user,item)` key) has already
  succeeded, repeated `purchase` calls shall return the cached result with `replay=true` and shall
  deduct/grant only once.
- **EARS-DOT-7 (Ubiquitous):** The service shall expose `owned(user)` as a sorted list of granted items.

## 2. 일촌 (관계) — IlchonService

- **EARS-ILC-1 (Event):** When `request(frm, to)` is called, the service shall record a directed pending
  request and return `status="requested"`.
- **EARS-ILC-2 (Unwanted):** If `request` is called with `frm == to`, then the service shall reject it
  with an error ("자기 자신과는 일촌을 맺을 수 없다").
- **EARS-ILC-3 (State/Idempotency):** While the same `(frm, to)` request was already issued, a repeated
  `request` shall return `replay=true`.
- **EARS-ILC-4 (Event):** When `accept(frm, to)` is called and a matching pending request exists, the
  service shall establish an **undirected** 일촌 relationship and return `status="accepted"`.
- **EARS-ILC-5 (Unwanted):** If `accept` is called with no matching pending request, then the service
  shall return `status="no_request"` and shall not create a relationship.
- **EARS-ILC-6 (Ubiquitous):** The service shall report `areIlchon(a, b)` symmetrically and `ilchons(user)`
  as a sorted list of partners. 수락 전에는 일촌이 아니다.

## 3. 투데이 (방문 집계) — TodayService

- **EARS-TOD-1 (Event):** When `visit(owner, visitor, day)` is called, the service shall add `visitor`
  to that owner+day's unique set and increment the owner's TOTAL.
- **EARS-TOD-2 (State/Idempotency):** While the same `(owner, visitor, day)` was already counted, a
  repeated `visit` shall return `replay=true` and shall NOT increment TODAY or TOTAL again.
- **EARS-TOD-3 (Ubiquitous):** TODAY (`todayCount(owner, day)`) shall be the unique visitor count for
  that day; TOTAL (`totalCount(owner)`) shall accumulate across days.

## 4. 방명록 — GuestbookService

- **EARS-GB-1 (Event):** When `write(owner, author, msg, secret)` is called, the service shall append the
  entry with an increasing sequence number.
- **EARS-GB-2 (Ubiquitous):** `entries(owner, viewer)` shall return entries in **recency order**
  (newest first).
- **EARS-GB-3 (State):** While an entry is secret, it shall be visible only to the 미니홈피 owner and the
  entry's author; other viewers shall not see it.

## 5. 웹 프론트 — App (com.sun.net.httpserver)

- **EARS-WEB-1 (Event):** When `GET /` is requested, the server shall return the 미니홈피 HTML page
  (SVG 미니룸, 기분, 방 꾸미기 포함).
- **EARS-WEB-2 (Event):** When `GET /api/state` is requested, the server shall return JSON with
  `owner, today, total, balance, ilchons, guestbook, room{wallpaper,bgm,owned}, mood{name,emoji,sky,weather,face}`.
- **EARS-WEB-3 (Event):** The server shall expose POST endpoints `/api/charge`, `/api/purchase`,
  `/api/ilchon_request`, `/api/ilchon_accept`, `/api/visit`, `/api/mood`, `/api/guestbook`, delegating to
  the matching domain services.
- **EARS-WEB-4 (Unwanted):** If a purchase is insufficient, then `/api/purchase` shall return HTTP 200
  with an `{"error": ...}` body (구매 실패 메시지). If a request key/value is malformed, the server shall
  return HTTP 400 `{"error":"bad_request: ..."}`.
- **EARS-WEB-5 (State):** The server shall seed the demo on startup (owner 도토리, balance 500, two
  guestbook entries, two TODAY visits, a pending 일촌 request from 친구B), and the default mood is 비.
- **EARS-WEB-6 (State):** While an owner owns a `벽지:*` / `BGM:*` shop item, `room.wallpaper` / `room.bgm`
  shall reflect that purchase; otherwise defaults apply. `/api/mood` shall change the room's window
  weather and 미니미 표정 only for the four known moods (맑음/흐림/비/행복).
