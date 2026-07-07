# signup_otp 화면 · 검증 (retained)

- 캐노니컬 스냅샷은 `sdd/04_verify/10_test/ui_parity/signup_otp.html`입니다.
- 스냅샷 게이트는 `python3 sdd/99_toolchain/01_automation/run_ui_parity.py`이며 ui_parity 1/1 PASS 기준입니다.
- 실 강의 데모는 Playwright exactness gate로 픽셀을 비교하며, 본 환경은 결정적 HTML parity로 대체합니다.

## Surface
- 요소는 제목('인증번호 입력'), 안내문, 6자리 입력(`maxlength="6"`), 확인 버튼입니다.
- 흐름은 이메일(`GET /`) → 발급·인증번호 입력(`POST /issue`) → 검증·결과(`POST /verify`)입니다.

## 런타임 렌더 검증 (Thymeleaf)
- 실행은 `./gradlew bootRun`이며, 검증 시 8080 점유로 `--server.port=8081`을 사용했습니다.
- 확인한 동작은 다음과 같습니다.
  - `GET /`은 200이며, 이메일 입력 화면과 기획 산출물 패널(AC-1~AC-6)이 렌더됩니다.
  - `POST /issue`는 200이며, '인증번호 입력' 화면과 6자리 입력칸·확인 버튼이 렌더됩니다.
  - `POST /verify`(정답)는 200이며, '가입 완료'(status=created, reason=ok)가 표시됩니다.
  - `POST /verify`(멱등 재요청)는 200이며, replay=true '중복 차단'이 표시됩니다.
  - `POST /verify`(미발급 이메일)는 200이며, '가입 거부'(reason=no_otp)가 표시됩니다.
- 캡처 증거는 `assets/step1-home.png`, `assets/step2-otp.png`, `assets/step3-result.png`입니다.

## Regression Scope
- direct는 화면 3단계 흐름(발급·검증·결과)입니다.
- shared는 `OtpService`·`SignupService`이며, 백엔드 회귀는 `./gradlew test`(JUnit)로 계속 보호합니다.
- 화면 추가가 기존 REST 계약(`/auth/*`)을 바꾸지 않았음을 서비스 재사용으로 확인했습니다.

## Residual Risk
- 반응형 레이아웃(모바일 폭)과 크로스 브라우저 렌더는 데스크톱 폭 1회 캡처로만 확인했습니다.
- 스냅샷 parity 게이트(run_ui_parity.py)는 파이썬 참조 구현 기준이며, Thymeleaf 뷰는 요소 일치로 갈음했습니다.
