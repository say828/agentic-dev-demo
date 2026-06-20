# 99_toolchain / 01_automation

이 데모의 자동화 게이트는 표준 도구만 쓴다(의존성 0).

## 테스트 게이트
```
cd buddybuddy
python -m pytest -q      # AC-1~6 + 회귀 (18 cases)
```

## 라이브 송수신 스모크 (AC-7 보조)
서버를 띄운 뒤 송수신 시나리오를 HTTP로 실행해 증거를 캡처한다.
```
python -m server.web.app          # 터미널 1: 서버 (localhost:8010)
python tmp/smoke.py               # 터미널 2: 송수신 스모크 → 04_verify/10_test/proof_evidence.md
```

## 비고
- cyworld 템플릿의 `run_ui_parity.py`(Playwright 픽셀 패리티)에 대응하는 시각 게이트는
  원본 디자인 스냅샷이 없어 미구축. AC-7은 로컬 기동 + 송수신 + 수동 시각 확인으로 대체.
