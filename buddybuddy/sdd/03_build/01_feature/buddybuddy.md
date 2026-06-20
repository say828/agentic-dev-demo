# 버디버디 메신저 · current-state

> 03_build: Overwrite Rule(지금 상태 1벌).

## Absorbed Planning
- `01_planning/01_feature/buddybuddy_feature_spec.md` (AC-1~AC-7)
- `02_plan/01_feature/buddybuddy_todos.md` (T1~T7)

## Runtime Assembly
- `PresenceService.login/logout` → 온라인/오프라인 집합 (메시지와 독립)
- `BuddyService.add` → 내 버디 목록(순서 보존) + 중복 추가 멱등
- `MessageService.send` → (frm,to) 쌍 frozenset 대화에 순번 기록 + client_msg_id 멱등
- `MessageService.thread/mark_read/unread` → 양쪽 동일 대화 조회 / 읽음 처리 / 안읽음 집계
- `MessageService.partners` → 대화 이력 있는 상대 목록(버디 미추가여도 노출)
- 웹 `app.py` 라우팅:
  - `/`          → 로비(누구로 접속할지 선택)
  - `/?me=<이름>` → **단일 사용자 클라이언트**(프론트 1개 = 사용자 1명, 1초 폴링)
  - `/demo`      → 두 창 한 페이지(보조 보기)
  - `state(me)` = 버디 ∪ partners 병합 → 두 프론트가 서로 자동 인식. `screens.MASCOT_SVG` 재사용.

## Modules
| 모듈 | 책임 | AC |
| --- | --- | --- |
| `contexts/buddybuddy/presence.py` | 로그인·로그아웃·온라인 상태 | 1 |
| `contexts/buddybuddy/buddy.py` | 버디 추가·목록·멱등 | 2 |
| `contexts/buddybuddy/message.py` | 송신·대화조회·전송멱등·읽음·대화격리·대화상대(partners) | 3·4·5·6·7 |
| `contexts/buddybuddy/screens.py` | 메신저 창 chrome + 마스코트 SVG | 7 |
| `server/web/app.py` | JSON API + 로비/단일클라이언트/데모 라우팅, 폴링 채팅 | 3·5·7 |
| `shared/idem.py` | idempotency_key (cyworld·auth 재사용) | 2·4 |

## Current Behavior
브라우저 창 2개를 각각 `/?me=현주`, `/?me=민수` 로 열면 두 프론트가 같은 서버를 통해
대화한다. 접속 시 해당 사용자가 온라인이 되고, 한쪽에서 보낸 메시지는 다른 창이 1초
폴링으로 받아 말풍선으로 표시한다(주고받는 모습). 같은 client_msg_id 재전송은 한 번만
기록(replay). 창을 열고 있으면 상대 메시지를 읽음 처리해 안읽음 배지가 0이 된다. 버디로
추가 안 한 새 상대도 메시지를 보내면 대화 목록에 자동으로 뜬다(partners 병합). 서로 다른
상대와의 대화는 분리된다. `/demo` 는 두 창을 한 페이지에 나란히 보여준다.
실행: `python -m server.web.app` → http://localhost:8010
