# 버디버디 메신저 · Acceptance Criteria (EARS)

> 01_planning: 요구사항을 검증 가능한 EARS로 정제. 이 명세가 가드레일.

**AC-1** When 사용자가 로그인하면, the system shall 그 사용자를 온라인으로 표시한다.
When 로그아웃하면, the system shall 오프라인으로 표시한다.

**AC-2** When A가 B를 버디로 추가하면, the system shall A의 버디 목록에 B를 넣는다.
같은 버디를 반복 추가하면 the system shall 목록에 한 번만 유지한다(멱등). 자기 자신은 거부.

**AC-3** When A가 B에게 메시지를 보내면, the system shall 그 메시지를 (A,B) 대화에 순번대로
기록하고, 보낸 사람·받는 사람·내용·순번을 보존하여 A와 B 양쪽이 같은 대화를 조회하게 한다.

**AC-4** When 같은 메시지(client_msg_id)가 재전송되면, the system shall 한 번만
기록한다(중복 전송 방지, 재전송은 replay).

**AC-5** When 받는 사람이 대화를 읽으면, the system shall 그 사람에게 온 안읽음 메시지를
읽음으로 바꾸고, 그 사람의 해당 대화 안읽음 수를 0으로 만든다.

**AC-6** While 한 사용자가 여러 상대와 대화 중일 때, the system shall 서로 다른 쌍의
대화를 분리한다 — (A,B) 대화는 (A,C) 대화와 섞이지 않는다.

**AC-7(화면)** The 버디버디 화면은 shall **프론트 1개 = 사용자 1명**으로 동작한다 —
`/?me=<이름>` 으로 접속하면 그 사용자의 메신저 창(버디 리스트 + 대화창)이 뜨고,
두 개의 창(예: `/?me=현주`, `/?me=민수`)이 같은 서버를 통해 메시지를 주고받는다.
버디로 명시 추가하지 않은 상대라도 대화 이력이 생기면 대화 목록에 자동 노출된다.
(`/demo` 는 두 창을 한 페이지에 나란히 보여주는 보조 화면.)

## 검증 매핑

| AC | 테스트 |
| --- | --- |
| AC-1 | `tests/test_presence.py` |
| AC-2 | `tests/test_buddy.py` |
| AC-3 | `tests/test_message.py::test_send_records_in_thread`, `::test_both_sides_see_same_thread` |
| AC-4 | `tests/test_message.py::test_send_idempotent` |
| AC-5 | `tests/test_message.py::test_mark_read_clears_unread` |
| AC-6 | `tests/test_message.py::test_threads_are_isolated` |
| AC-7 | `tests/test_message.py::test_partners_lists_conversation_others` + `tmp/smoke2.py` (라우팅·두 프론트 송수신) + 로컬 시각 확인 |
| 회귀 | `tests/test_regression.py` (버디 추가 후에도 송수신 유지) |
