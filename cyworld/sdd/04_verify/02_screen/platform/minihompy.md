# minihompy 화면 · 검증 (retained)

> 화면 캡쳐(싸이월드 미니홈피 메인)에서 출발한 좌측 미니룸 + 우측 홈 레이아웃.

- 캐노니컬 스냅샷: `sdd/04_verify/10_test/ui_parity/minihompy.html`
- 게이트: `python3 sdd/99_toolchain/01_automation/run_ui_parity.py` → ui_parity 1/1 PASS
- 렌더 소스: `server/contexts/cyworld/screens.py` (고정 데모 상태)
- 핵심 요소: `.miniroom`(미니미·기분) · `.home`(소유자·TODAY/TOTAL·메뉴·BGM)

## Residual Risk
- 픽셀 단위 exactness는 브라우저 비가용으로 미검증 → HTML 구조 parity로 대체.
