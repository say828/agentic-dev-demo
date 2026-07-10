# 버디버디 메신저 (Java 포트)

Python 데모 `agentic-dev-demo/buddybuddy`를 충실히 옮긴 **표준 Gradle / JDK 17** 프로젝트.
외부 런타임 의존성 없이 JDK 내장 `com.sun.net.httpserver.HttpServer`로 JSON API + HTML
페이지를 제공한다(파이썬의 `http.server` 미러). JSON은 손수 만든 작은 헬퍼로 처리한다
(Jackson/Spring 미사용).

## 구조

```
src/main/java/kr/elice/buddybuddy/
  shared/Idem.java          멱등키(SHA-256) + IdempotencyStore
  domain/PresenceService.java   로그인/로그아웃/온라인 상태
  domain/BuddyService.java      버디 추가(멱등)·자기추가 거부
  domain/MessageService.java    1:1 메시지(핵심): 멱등 전송·순서무관 스레드·읽음·대화상대
  web/Json.java             의존성 제로 JSON 직렬화/역직렬화
  web/Screens.java          마스코트 SVG + 윈도우 크롬
  web/Pages.java            로비 / 단일 클라이언트 / 데모 HTML+CSS+JS
  web/App.java              HttpServer + 라우팅 + JSON API (main)
src/test/java/kr/elice/buddybuddy/   JUnit 5 테스트(파이썬 pytest 포트)
sdd/01_planning/01_feature/buddybuddy_feature_spec.md   EARS 인수 기준
```

## 테스트 실행

JDK가 PATH에 없으면 portable JDK를 먼저 잡는다(Bash):

```bash
export JAVA_HOME="/c/code/_jdk/jdk-17.0.19+10"; export PATH="$JAVA_HOME/bin:$PATH"
cd /c/code/agentic-dev-demo-java/buddybuddy && ./gradlew test --console=plain
```

## 웹 데모 실행

```bash
export JAVA_HOME="/c/code/_jdk/jdk-17.0.19+10"; export PATH="$JAVA_HOME/bin:$PATH"
./gradlew classes
java -cp build/classes/java/main kr.elice.buddybuddy.web.App
# 또는 포트 지정: java -cp build/classes/java/main kr.elice.buddybuddy.web.App 8010
```

서버는 `http://localhost:8010`에서 뜬다. 브라우저 창 두 개를 열어 대화한다(1초 폴링):

- `http://localhost:8010/?me=현주`
- `http://localhost:8010/?me=민수`

`/`는 로비(이름으로 로그인), `/demo`는 두 패널(현주 ↔ 민수)을 한 화면에 띄운다.

## API 요약

| 메서드 | 경로 | 바디/쿼리 | 설명 |
| --- | --- | --- | --- |
| GET | `/api/state?me=` | — | 버디+대화상대 병합(online/unread 포함) |
| GET | `/api/thread?a=&b=` | — | 순서 무관 스레드 |
| POST | `/api/login` | `{user}` | 로그인 |
| POST | `/api/logout` | `{user}` | 로그아웃 |
| POST | `/api/buddy_add` | `{owner, buddy}` | 버디 추가(멱등) |
| POST | `/api/send` | `{frm, to, text, client_msg_id}` | 메시지 전송(멱등) |
| POST | `/api/read` | `{reader, other}` | 읽음 처리 |
