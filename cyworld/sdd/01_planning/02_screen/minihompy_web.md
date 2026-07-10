# 미니홈피 웹 프론트 · Acceptance Criteria (EARS)

> 01_planning/02_screen: 백엔드 서비스를 로컬 웹으로 노출하는 프론트 계층의 가드레일.
> 의존성 0(파이썬 표준 `http.server`). 브라우저 비가용 환경이라 HTTP 계약을 결정적
> pytest(in-process 서버 + UTF-8 호출)로 검증한다.

**AC-W1** When 사용자가 `/` 를 요청하면, the system shall 미니홈피 단일 페이지(HTML)를
반환하고, 그 안의 JS가 상태 API(`/api/state`)를 호출한다.

**AC-W2** When `/api/state` 를 조회하면, the system shall 소유자·TODAY·TOTAL·도토리 잔액·
일촌 목록·방명록(가시성 적용)을 JSON으로 반환한다.

**AC-W3** When 도토리 충전/구매 API가 호출되면, the system shall 백엔드 `DotoriService`에
위임하고 결과(잔액·replay)를 반환한다. 잔액 부족이면 the system shall 서버를 유지한 채
에러를 JSON으로 표면화한다(스레드 비종료).

**AC-W4** When 일촌 신청/수락·방문·방명록 API가 호출되면, the system shall 각 백엔드
서비스에 위임하고, 잘못된 본문(UTF-8 디코드/JSON 실패)은 400으로 거부한다.

## 검증 매핑
| AC | 테스트 |
| --- | --- |
| AC-W1 | `tests/test_web.py::test_page_served` |
| AC-W2 | `tests/test_web.py::test_state_has_seed` |
| AC-W3 | `tests/test_web.py::test_charge_then_purchase`, `::test_purchase_insufficient_returns_error` |
| AC-W4 | `tests/test_web.py::test_ilchon_accept_flow`, `::test_guestbook_post` |

> 백엔드 도메인 AC-1~AC-6 은 변경 없음(`01_feature/cyworld_feature_spec.md`). 프론트는
> 그 위에 얹은 얇은 전송 계층이며, 도메인 로직을 재구현하지 않는다.
