# signup_otp 화면 · current-state (build)

> 03_build/02_screen: 지금 구현된 화면 1벌 요약입니다(Overwrite Rule).

## Absorbed Planning
- `01_planning/02_screen/signup_otp_screen.md`
- `01_planning/01_feature/auth_feature_spec.md` (AC-6)

## 구현 요약
- 런타임은 Spring Boot와 Thymeleaf 서버 렌더링입니다.
- 라우트는 `GET /`(이메일) → `POST /issue`(발급·인증번호 입력) → `POST /verify`(검증·결과)입니다.
- 컨트롤러 `SignupPageController`가 REST(`/auth/*`)와 동일한 `OtpService`·`SignupService`를 재사용합니다.
- 뷰 `templates/signup.html` 한 장에서 `step` 값으로 3단계를 전환합니다.
- 화면은 동작 흐름과 함께 기획 산출물(AC-1~AC-6, SDD 산출물 체인) 패널을 나란히 표시합니다.

## Modules
| 모듈 | 책임 | AC |
| --- | --- | --- |
| `controller/SignupPageController.java` | 화면 라우트(발급·검증·결과) | 6 |
| `resources/templates/signup.html` | 3단계 화면 + 기획 산출물 패널 | 6 |
| `service/OtpService.java` | OTP 발급·검증(재사용) | 1·3·4 |
| `service/SignupService.java` | 가입·멱등(재사용) | 2·5 |

## 현재 사용자 동작
이메일을 입력해 인증번호를 발급받고, 6자리를 입력하면 가입이 완료됩니다.
틀리거나 만료·잠금·멱등이면 거부 사유를 한국어 문장으로 표시합니다.
'인증번호 입력' 화면 요소는 승인된 스냅샷(`signup_otp.html`)과 일치합니다.

## 데모 편의
실제 서비스는 인증번호를 이메일로 전송하지만, 이 데모는 발급 코드를 화면에 함께 표시해
브라우저만으로 전체 흐름을 끝까지 실행할 수 있게 했습니다.
