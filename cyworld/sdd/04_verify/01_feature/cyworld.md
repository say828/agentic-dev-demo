# 싸이월드 미니홈피 · 검증 (retained): 회귀 4분면

> proof: `python3 proof/run_proof.py` → 27/27 PASS (백엔드 18 + 웹 9, exit 0).

| 분면 | 검증 대상 | 수용기준 | 결과 |
| --- | --- | --- | --- |
| 경제 | 도토리 충전→구매 차감 | AC-1·AC-2 | PASS |
| 보안/정합 | 잔액부족 거부(잔액 보존) | AC-2 | PASS |
| 멱등 | 같은 주문 이중결제 방지 | AC-3 | PASS · replay |
| 보유 | 구매 시 아이템 지급(멱등 단일) | AC-7 | PASS |
| 그래프 | 일촌 신청→수락 양방향 | AC-4 | PASS |
| 집계 | 투데이 멱등(방문자·날짜) | AC-5 | PASS |
| 화면 | minihompy 스냅샷 일치 | AC-6 | PASS · ui_parity 1/1 |
| 방꾸미기 | 벽지·BGM 구매가 미니룸 반영 | AC-W5·W6 | PASS |
| 기분 | 기분 변경이 창문 날씨·미니미 표정 반영 | AC-W7 | PASS |
| 회귀 | 방명록 최신순·비밀글 무손상 | shared | PASS |

## Residual Risk
- 실 브라우저(Playwright) 픽셀 비교·compose 부팅은 데모 범위 밖: HTML parity로 대체.
- 실 PG 결제·실 계정·BGM 스트리밍·사진 업로드는 미구현(가상 상태로 대체).
