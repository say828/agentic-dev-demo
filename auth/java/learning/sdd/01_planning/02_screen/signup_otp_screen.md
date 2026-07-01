# signup_otp 화면 · 기획 (screen spec)

> 01_planning/02_screen: 회원가입 OTP 입력 화면(signup_otp)의 기획입니다.
> 가드레일 feature 명세는 `sdd/01_planning/01_feature/auth_feature_spec.md`(AC-6)입니다.

## 목적
회원가입은 이메일로 받은 6자리 인증번호를 입력해야 완료됩니다.
signup_otp 화면은 그 인증번호 입력 단계를 사용자에게 보여 주는 화면입니다.
이 화면이 승인된 디자인 스냅샷과 일치해야 한다는 것이 AC-6입니다.

## 화면 흐름 (3단계)
- 1단계(이메일): 사용자가 이메일을 입력하고 인증번호를 요청합니다. (AC-1 발급)
- 2단계(인증번호 입력): '인증번호 입력' 화면에서 6자리 코드를 입력하고 확인합니다. (AC-2 검증·가입)
- 3단계(결과): 가입 완료 또는 거부 사유(만료·잠금·불일치·멱등)를 표시합니다. (AC-3·AC-4·AC-5)

## 화면 요소 (캐노니컬 스냅샷)
- 제목은 '인증번호 입력'입니다.
- 안내문은 '이메일로 받은 6자리 인증번호를 입력하세요.'입니다.
- 입력칸은 6자리 숫자 입력(`maxlength="6"`, `inputmode="numeric"`)입니다.
- 버튼은 '확인'입니다.
- 스냅샷 기준 파일은 `sdd/04_verify/10_test/ui_parity/signup_otp.html`입니다.

## 구현·검증 위치
- 구현(Thymeleaf)은 `auth/java/complete`의 `templates/signup.html`과 `SignupPageController`입니다.
- 실행은 `./gradlew bootRun` 후 브라우저에서 http://localhost:8080 으로 확인합니다.
- 검증 기록은 `sdd/04_verify/02_screen/platform/signup.md`입니다.

## 왜 이 화면을 기획 단계에서 정의하나
화면을 코드로 만들기 전에, 어떤 요소가 어떤 순서로 보여야 하는지 문서로 먼저 확정합니다.
이렇게 하면 구현과 검증이 같은 기준(스냅샷)을 바라보게 되고, 화면이 계획에서 벗어나지 않습니다.
7강 플래닝 실습에서는 이 기획서를 읽으며, 왜 이 화면이 필요한지를 코드보다 먼저 이해합니다.
