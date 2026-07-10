# 버디버디 메신저 · Acceptance Criteria (EARS)

> 01_planning: 요구사항을 검증 가능한 EARS로 정제. 이 명세가 가드레일.
> Python 데모(`agentic-dev-demo/buddybuddy`)를 Java(JDK 17)로 충실히 포트한 버전.

## 도메인 AC

**AC-1 (접속)** When 사용자가 로그인하면, the system shall 해당 사용자를 온라인 집합에
추가하고 `status`를 `online`으로 보고한다. logout 시 `offline`으로 되돌린다.

**AC-2 (버디 추가)** When 사용자가 버디를 추가하면, the system shall (owner, buddy)에
묶인 멱등키로 중복 추가를 차단한다. 재요청은 replay 로 처리되고 목록은 1건만 유지한다.

**AC-3 (자기추가 거부)** When 자기 자신을 버디로 추가하면, the system shall `rejected`
(reason `self_add`)로 거부한다.

**AC-4 (메시지 멱등 — client_msg_id)** When 같은 `client_msg_id`로 메시지가 재전송되면,
the system shall 멱등성을 보장해 스레드에 중복 기록하지 않는다(replay).

**AC-5 (메시지 멱등 — content-hash 폴백)** While `client_msg_id`가 없을 때,
when 동일한 (frm, to, text)로 재전송되면, the system shall content-hash 멱등으로 중복을
차단한다. 단, 같은 텍스트라도 `client_msg_id`가 다르면 별개 메시지로 둘 다 기록한다.

**AC-6 (자기/빈 메시지 거부)** When frm == to 이거나 text 가 공백이면, the system shall
메시지를 `rejected`로 거부하고 스레드에 기록하지 않는다.

**AC-7 (스레드 — 순서 무관 쌍)** The system shall 두 사용자 사이의 대화를 정렬된 쌍 키로
저장해 `thread(a, b) == thread(b, a)`가 성립하게 한다. 서로 다른 쌍의 대화는 격리된다.

**AC-8 (읽음 처리)** When 사용자가 상대와의 대화를 읽으면, the system shall 받은
메시지를 모두 읽음 처리하고 안 읽음 카운트를 0으로 만든다.

**AC-9 (대화 상대)** The system shall 사용자가 대화한 적 있는 상대를 `partners`로 노출한다.
버디로 추가하지 않았어도 메시지를 주고받으면 대화 목록에 자동 병합된다.

## 화면/웹 AC

**AC-10 (라우팅)** The web 프론트는 shall `/`(로비 — "로그인" 포함), `/?me=<name>`
(단일 클라이언트 — `const ME = "<name>"` 임베드 + 1초 폴링), `/demo`(두 패널 — `id="stage"`)
를 제공한다. JSON API는 `/api/state`, `/api/thread`, `/api/login`, `/api/logout`,
`/api/buddy_add`, `/api/send`, `/api/read`.

**AC-11 (제로 의존성 · UTF-8)** The web 프론트는 shall JDK 내장 `HttpServer`만 사용하고
(Jackson/Spring 미사용) 한글 텍스트를 UTF-8로 일관 처리한다.

## 검증 매핑

| AC | 테스트 |
| --- | --- |
| AC-1 | `PresenceServiceTest` |
| AC-2 | `BuddyServiceTest::addIsIdempotent` |
| AC-3 | `BuddyServiceTest::selfAddRejected` |
| AC-4 | `MessageServiceTest::sendIdempotentViaClientMsgId`, `sameTextDistinctIdsBothRecorded` |
| AC-5 | `MessageServiceTest::contentHashFallbackWhenNoClientMsgId` |
| AC-6 | `MessageServiceTest::selfMessageRejected`, `emptyMessageRejected` |
| AC-7 | `MessageServiceTest::threadUnorderedPair`, `threadsIsolated` |
| AC-8 | `MessageServiceTest::markReadClearsUnread` |
| AC-9 | `MessageServiceTest::partnersListsConversationOthers`, `RegressionTest::partnersAutoMergeForNewConversation` |
| AC-10 | `WebTest` (lobby/client/demo 마커) |
| AC-11 | `WebTest::jsonRoundTrip` + `web/Json.java`, `web/App.java` |
| 회귀(E2E) | `RegressionTest::endToEndConversationFlow` |
