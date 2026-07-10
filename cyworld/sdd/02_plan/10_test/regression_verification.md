# 회귀 검증 범위 (retained)

| 표면 | 분류 | 검증 |
| --- | --- | --- |
| 도토리·일촌·투데이 | direct | `test_dotori.py`, `test_ilchon.py`, `test_today.py` |
| 방명록(기존) | shared | `test_regression.py` |
| 미니홈피 화면 | direct | `test_screen_parity.py` + `run_ui_parity.py` |

선정 근거: 도토리·일촌·투데이·방명록은 모두 미니홈피라는 공통 화면/소유자 컨텍스트를
공유하므로, 신규 기능 추가가 기존 방명록 흐름을 깨지 않는지 회귀로 본다.
