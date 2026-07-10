# 회귀 검증 범위 (02_plan / 10_test)

## 변경 표면
신규 컨텍스트 `buddybuddy`(presence/buddy/message/screens) + 웹 프론트. 기존 모듈 수정 없음.

## 회귀 대상 선정
| 표면 | 영향 | 검증 |
| --- | --- | --- |
| message 송수신(직접 대상) | 핵심 흐름 | `tests/test_message.py` |
| buddy 추가(인접) | 버디 추가가 송수신 상태를 오염시키지 않아야 함 | `tests/test_regression.py` |
| presence(공유 상태) | 온라인 표시가 메시지 기록과 독립 | `tests/test_presence.py` |
| shared/idem(공유 유틸) | 멱등 캐시가 buddy·message 양쪽에서 정상 | `tests/test_buddy.py` + `tests/test_message.py` |

## 정당화된 제외
- DEV/PROD 롤아웃 없음(로컬 데모) → schema·스테이징 게이트 비대상.
- UI 픽셀 패리티 스냅샷 원본 이미지 없음 → AC-7은 로컬 기동 + curl 송수신 + 수동 시각 확인으로 대체(잔여 리스크는 04_verify에 기록).
