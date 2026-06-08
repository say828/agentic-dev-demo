# proof 증거 (retained)

```
python3 -m compileall -q server          # build OK
python3 proof/run_proof.py               # 16 passed → [proof] PASS · 16/16
python3 sdd/99_toolchain/01_automation/run_ui_parity.py   # ui_parity 1/1 · PASS
```

- 게이트: pytest 결정적(AC-1~AC-6 + 회귀)
- 산출물: `tmp/proof-results.json` (exit_code 0, failed 0)
- 회귀 범위: `sdd/02_plan/10_test/regression_verification.md` 참조(direct: 도토리·일촌·투데이 / shared: 방명록)
