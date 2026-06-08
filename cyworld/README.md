# 싸이월드 미니홈피 데모 (백엔드-온리 · 로컬 · SDD)

> 강의 데모용 **가상** 싸이월드 미니홈피 클론. 실 계정·결제 없음.
> 화면 캡쳐(미니홈피 메인)에서 출발해 **백엔드만 로컬로** SDD 방식으로 클론한다.
> `auth`·`pinterest` 형제 데모와 같은 SDD 스캐폴드를 따른다.

## 실행
```bash
pip install -r requirements.txt
python3 -m compileall -q server                              # build
python3 proof/run_proof.py                                   # proof → 16/16 PASS
python3 sdd/99_toolchain/01_automation/run_ui_parity.py      # verify_dev (UI parity 1/1)
```

## 무엇을 클론했나 (auth·finance·pinterest 패턴 종합)
| 백엔드 핵심 | 모듈 | 결 | AC |
| --- | --- | --- | --- |
| 도토리 충전·구매·잔액부족·이중결제 멱등 | `server/contexts/cyworld/dotori.py` | 결제(finance)+멱등(auth) | AC-1·2·3 |
| 일촌 신청→수락 양방향 그래프 | `server/contexts/cyworld/ilchon.py` | 상태머신(신규) | AC-4 |
| 투데이 멱등 방문 집계 | `server/contexts/cyworld/today.py` | 멱등(OTP) | AC-5 |
| 미니홈피 메인 화면 parity | `server/contexts/cyworld/screens.py` | 화면 parity | AC-6 |
| 방명록(기존 흐름, 회귀 surface) | `server/contexts/cyworld/guestbook.py` | 회귀 | 회귀 |

## SDD 트레일
- `sdd/00_sources` 요구사항 원문 → `01_planning` EARS 명세 → `02_plan` todos
- `03_build` 구현 요약 → `04_verify` 회귀 4분면 + proof 증거 → `05_operate` 배포 상태(미수행)

## 환경 경계 (정직)
실 강의 데모의 Playwright exactness·compose 부팅·CI 배포는 브라우저/Docker/CI를 요구한다.
이 환경엔 없으므로 **백엔드 로직은 결정적 pytest로 실제 검증**하고, **화면 정합은 HTML
스냅샷 parity**로, **배포는 로컬 스텁/미수행**으로 대체한다.
