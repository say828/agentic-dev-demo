# 미니홈피 웹 프론트 · current-state

> 03_build/02_screen: Overwrite Rule(지금 상태 1벌).

## Absorbed Planning
- `01_planning/02_screen/minihompy_web.md` (AC-W1~AC-W4)
- `02_plan/02_screen/minihompy_web_todos.md` (W1~W5)

## Module
| 모듈 | 책임 | AC |
| --- | --- | --- |
| `server/web/app.py` | 의존성 0 `http.server` 앱: 페이지 + JSON API, 백엔드 위임 | W1~W4 |

## Routes
- `GET /` → 미니홈피 HTML(인라인 CSS+JS, `/api/state` 호출)
- `GET /api/state` → owner·today·total·balance·ilchons·guestbook
- `POST /api/charge` · `/api/purchase`(잔액부족=JSON 에러) · `/api/ilchon_request`
  · `/api/ilchon_accept` · `/api/visit` · `/api/guestbook`

## Current Behavior
브라우저에서 미니홈피가 뜨고, 충전/구매/일촌수락/방명록 작성이 백엔드 서비스에 위임되어
즉시 화면에 반영된다. 도메인 로직은 `contexts/cyworld/*` 그대로 재사용(재구현 없음).

## 실행
`python3 -m server.web.app` → http://localhost:8000
