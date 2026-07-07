# 01_planning: INDEX (1단 진입점)

## 이 실습을 왜 하나 · 끝까지 하면 무엇을 보나

이 폴더(01_planning)는 회원가입 OTP 기능을 코드로 만들기 전에, 무엇을 왜 만드는지
기획 문서(md)로 먼저 확정하는 단계입니다. 7강 플래닝 실습에서는 이 폴더의 문서만 둘러봅니다.
그래서 지금은 눈에 보이는 화면이 아직 없습니다.

하지만 여기서 확정한 계획(AC-1~AC-6)은 뒤 단계(02_plan → 03_build → 04_verify)를 거쳐
실제로 동작하는 회원가입 OTP 화면이 됩니다. 실습을 끝까지 마치면 `auth/java/complete`에서
`./gradlew bootRun`을 실행한 뒤 브라우저 http://localhost:8080 에서 아래 화면과 산출물을 직접 볼 수 있습니다.

- 화면은 이메일 입력 → 인증번호 입력 → 가입 결과의 3단계로 동작합니다.
- '인증번호 입력' 화면은 이 폴더의 화면 기획서(`02_screen/signup_otp_screen.md`)를 그대로 구현한 것입니다.
- 화면 오른쪽 패널에는 지금 읽는 기획(AC-1~AC-6)과 SDD 산출물 체인이 함께 표시됩니다.
- 완성 화면 미리보기는 `auth/java/complete/sdd/04_verify/02_screen/assets/`의 캡처(step1~step3)에서 확인합니다.

> 정리하면, 지금 읽는 기획 문서가 마지막에 이 화면 한 장으로 이어집니다. 그 연결을 미리 알고
> 문서를 읽으면, 각 AC가 왜 필요한지가 화면 동작으로 설명됩니다.

## 명세 목록

| 영역 | 파일 | 상태 |
| --- | --- | --- |
| feature · 회원가입 OTP | `01_feature/auth_feature_spec.md` | 계획 수립(02_plan 작성, build 대기) |
| screen · signup_otp 화면 | `02_screen/signup_otp_screen.md` | 계획 수립(complete에 구현 완료) |
| feature · 알림 | `01_feature/alerts_feature_spec.md` | 계획(예시) |

> 폴더를 열면 이 INDEX가 먼저 보인다: 어떤 명세가 있고 어디까지 됐는지 1단으로.
> 회원가입 OTP 실행 계획: `sdd/02_plan/01_feature/auth_todos.md`.
