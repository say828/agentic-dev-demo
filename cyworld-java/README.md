# 미니홈피 (Cyworld) — Java 포팅

Python 데모(`agentic-dev-demo/cyworld`)의 충실한 Java 포팅. 표준 JDK만 사용한다
(웹은 `com.sun.net.httpserver`, JSON은 직접 구현). 외부 런타임 의존성 0.

## 구조

```
src/main/java/kr/elice/cyworld/
  shared/   IdempotencyStore, Idem (멱등 키 = sha256(canonical json))
  domain/   DotoriService, IlchonService, TodayService, GuestbookService,
            Screens, PurchaseResult, InsufficientDotori
  web/      App (HttpServer + JSON API + 미니홈피 페이지), Json
src/main/resources/kr/elice/cyworld/web/page.html   # 미니홈피 HTML (SVG 미니룸/기분/방꾸미기)
src/test/java/kr/elice/cyworld/                      # JUnit 5 (pytest 케이스 미러)
sdd/01_planning/01_feature/cyworld_feature_spec.md   # EARS 인수 기준
```

## 테스트 실행

```bash
# JDK 17 (PATH에 없으면 export)
export JAVA_HOME="/c/code/_jdk/jdk-17.0.19+10"; export PATH="$JAVA_HOME/bin:$PATH"
./gradlew test --console=plain
```

테스트는 도메인 서비스(도토리/일촌/투데이/방명록·회귀) 단위 테스트와, 실제
`HttpServer`를 임의 포트로 띄워 JSON API를 검증하는 웹 통합 테스트(`WebAppTest`)로 구성된다.
웹 테스트는 Python의 module-scope fixture처럼 시드된 서버 하나에 대해 선언 순서대로 상태를
누적하며 검증한다.

## 웹 앱 실행

```bash
export JAVA_HOME="/c/code/_jdk/jdk-17.0.19+10"; export PATH="$JAVA_HOME/bin:$PATH"
./gradlew classes        # 또는: ./gradlew build
java -cp "build/classes/java/main:build/resources/main" kr.elice.cyworld.web.App
# → 미니홈피: http://localhost:8000  (포트 인자: java ... App 9000)
```

브라우저로 `http://localhost:8000` 에 접속하면 SVG 미니룸, 도토리 충전/구매, 방 꾸미기
상점, 일촌, 오늘의 기분, 방명록을 조작할 수 있다.

## API

- `GET  /`            — 미니홈피 HTML
- `GET  /api/state`   — `{owner,today,total,balance,ilchons,guestbook,room,mood}` (쿼리: owner/viewer/day)
- `POST /api/charge`            `{user, amount}`
- `POST /api/purchase`          `{user, item, price, order_id?}`
- `POST /api/ilchon_request`    `{frm, to}`
- `POST /api/ilchon_accept`     `{frm, to}`
- `POST /api/visit`             `{owner, visitor, day?}`
- `POST /api/mood`              `{mood}` (맑음/흐림/비/행복)
- `POST /api/guestbook`         `{owner, author, msg, secret?}`
