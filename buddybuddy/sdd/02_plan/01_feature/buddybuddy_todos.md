# 버디버디 메신저 · 작업 계획 (02_plan)

## Scope
2000년대 PC 메신저 "버디버디"의 백엔드를 로컬·인메모리로 클론하고, 의존성 0 웹
프론트에서 **두 사용자가 메시지를 주고받는 모습**을 보이게 한다. 실계정·실서버 없음.

## Assumptions
- 인메모리 단일 프로세스. 실시간·난수·외부 PG 비의존 → 결정적으로 검증 가능.
- "실시간"은 브라우저 폴링(1s)으로 흉내 낸다(웹소켓 미사용 — 표준 라이브러리만).
- 대화는 순서 없는 쌍 frozenset({a,b})로 식별 → 방향과 무관하게 같은 대화.

## Acceptance Criteria
`01_planning/01_feature/buddybuddy_feature_spec.md` AC-1~AC-7 + 회귀.

## Execution Checklist
- [x] T1 `shared/idem.py` — idempotency_key / IdempotencyStore (cyworld·auth와 동일 패턴 재사용)
- [x] T2 `contexts/buddybuddy/presence.py` — 로그인/로그아웃/온라인 (AC-1)
- [x] T3 `contexts/buddybuddy/buddy.py` — 버디 추가·목록·멱등 (AC-2)
- [x] T4 `contexts/buddybuddy/message.py` — 송신·대화 조회·전송 멱등·읽음·대화 격리 (AC-3·4·5·6)
- [x] T5 `contexts/buddybuddy/screens.py` — 버디버디 메인 화면 HTML (AC-7 보조)
- [x] T6 `server/web/app.py` — JSON API + 두 사용자 대화 페이지(폴링) (AC-7)
- [x] T7 `tests/` — presence/buddy/message/regression pytest (전 AC)

## Current Notes
- 메시지 멱등 키: `client_msg_id` 우선, 없으면 (frm,to,text) 내용 해시로 폴백(dotori.purchase와 동형).
  웹 프론트는 전송마다 카운터 기반 client_msg_id를 부여해 동일 문구 재전송도 별개로 보낸다.
- 안읽음(unread)은 "받는 사람 앞으로 온, 아직 안 읽은 메시지" 기준으로 집계.

## Validation
- `python -m pytest -q` (buddybuddy 디렉토리에서) → 전 케이스 green.
- `python -m server.web.app` 기동 후 curl 로 send→thread 송수신 확인, 브라우저로 두 패널 시각 확인.
