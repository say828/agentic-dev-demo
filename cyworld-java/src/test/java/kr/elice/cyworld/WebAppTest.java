package kr.elice.cyworld;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URI;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;

import com.sun.net.httpserver.HttpServer;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.MethodOrderer.OrderAnnotation;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;
import org.junit.jupiter.api.TestMethodOrder;

import kr.elice.cyworld.web.App;
import kr.elice.cyworld.web.Json;

/**
 * test_web.py 포팅. Python 의 module-scope fixture 처럼 하나의 시드된 서버를
 * 띄우고 (인메모리 상태 누적) 선언 순서대로 검증한다.
 */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
@TestMethodOrder(OrderAnnotation.class)
class WebAppTest {

    private static HttpServer server;
    private static String baseUrl;

    @BeforeAll
    void start() throws IOException {
        App app = new App(); // 생성자가 _seed 까지 수행
        server = app.createServer(0); // 임의 포트
        server.start();
        baseUrl = "http://127.0.0.1:" + server.getAddress().getPort();
    }

    @AfterAll
    void stop() {
        server.stop(0);
    }

    // ---------- HTTP 헬퍼 ----------

    private static HttpURLConnection open(String url) throws IOException {
        try {
            return (HttpURLConnection) new URI(url).toURL().openConnection();
        } catch (java.net.URISyntaxException e) {
            throw new IOException(e);
        }
    }

    private static String getText(String url) throws IOException {
        HttpURLConnection c = open(url);
        c.setRequestMethod("GET");
        try (var in = c.getInputStream()) {
            return new String(in.readAllBytes(), StandardCharsets.UTF_8);
        }
    }

    @SuppressWarnings("unchecked")
    private static Map<String, Object> get(String url) throws IOException {
        return Json.loadsObject(getText(url));
    }

    @SuppressWarnings("unchecked")
    private static Map<String, Object> post(String url, Map<String, Object> payload) throws IOException {
        HttpURLConnection c = open(url);
        c.setRequestMethod("POST");
        c.setDoOutput(true);
        c.setRequestProperty("Content-Type", "application/json");
        byte[] data = Json.dumps(payload).getBytes(StandardCharsets.UTF_8);
        try (OutputStream os = c.getOutputStream()) {
            os.write(data);
        }
        try (var in = c.getInputStream()) {
            return Json.loadsObject(new String(in.readAllBytes(), StandardCharsets.UTF_8));
        }
    }

    private static Map<String, Object> map(Object... kv) {
        java.util.LinkedHashMap<String, Object> m = new java.util.LinkedHashMap<>();
        for (int i = 0; i < kv.length; i += 2) {
            m.put((String) kv[i], kv[i + 1]);
        }
        return m;
    }

    // ---------- 테스트 ----------

    @Test
    @Order(1)
    void test_page_served() throws IOException {
        String html = getText(baseUrl + "/");
        assertTrue(html.contains("님의 미니홈피"));
        assertTrue(html.contains("/api/state"));
    }

    @Test
    @Order(2)
    void test_state_has_seed() throws IOException {
        Map<String, Object> s = get(baseUrl + "/api/state");
        assertEquals("도토리", s.get("owner"));
        assertEquals(500, s.get("balance"));
        assertEquals(2, s.get("today"));
        assertEquals(2, ((List<?>) s.get("guestbook")).size());
    }

    @Test
    @Order(3)
    void test_charge_then_purchase() throws IOException {
        assertEquals(600, post(baseUrl + "/api/charge", map("user", "도토리", "amount", 100)).get("balance"));
        Map<String, Object> r = post(baseUrl + "/api/purchase",
                map("user", "도토리", "item", "미니룸스킨", "price", 120, "order_id", "w1"));
        assertEquals("purchased", r.get("status"));
        assertEquals(480, r.get("balance"));
    }

    @Test
    @Order(4)
    void test_purchase_insufficient_returns_error() throws IOException {
        Map<String, Object> r = post(baseUrl + "/api/purchase",
                map("user", "도토리", "item", "고가템", "price", 999999));
        assertTrue(r.containsKey("error"));
    }

    @Test
    @Order(5)
    void test_ilchon_accept_flow() throws IOException {
        Map<String, Object> r = post(baseUrl + "/api/ilchon_accept", map("frm", "친구B", "to", "도토리"));
        assertEquals("accepted", r.get("status"));
        Map<String, Object> s = get(baseUrl + "/api/state");
        assertTrue(((List<?>) s.get("ilchons")).contains("친구B"));
    }

    @Test
    @Order(6)
    void test_guestbook_post() throws IOException {
        post(baseUrl + "/api/guestbook", map("owner", "도토리", "author", "방문자", "msg", "다녀가요", "secret", false));
        Map<String, Object> s = get(baseUrl + "/api/state");
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> gb = (List<Map<String, Object>>) s.get("guestbook");
        assertEquals("방문자", gb.get(0).get("author"));
    }

    @Test
    @Order(7)
    void test_room_reflects_purchase() throws IOException {
        @SuppressWarnings("unchecked")
        Map<String, Object> s0 = (Map<String, Object>) get(baseUrl + "/api/state").get("room");
        assertEquals(App.DEFAULT_WALL, s0.get("wallpaper"));
        assertTrue(!((List<?>) s0.get("owned")).contains("벽지:하늘"));

        post(baseUrl + "/api/purchase",
                map("user", "도토리", "item", "벽지:하늘", "price", 80, "order_id", "wp1"));

        @SuppressWarnings("unchecked")
        Map<String, Object> s1 = (Map<String, Object>) get(baseUrl + "/api/state").get("room");
        assertEquals(App.WALLPAPERS.get("벽지:하늘"), s1.get("wallpaper"));
        assertTrue(((List<?>) s1.get("owned")).contains("벽지:하늘"));
    }

    @Test
    @Order(8)
    void test_room_bgm_from_purchase() throws IOException {
        post(baseUrl + "/api/purchase",
                map("user", "도토리", "item", "BGM:벚꽃엔딩", "price", 50, "order_id", "bg1"));
        @SuppressWarnings("unchecked")
        Map<String, Object> room = (Map<String, Object>) get(baseUrl + "/api/state").get("room");
        assertEquals("벚꽃엔딩", room.get("bgm"));
    }

    @Test
    @Order(9)
    void test_mood_change() throws IOException {
        @SuppressWarnings("unchecked")
        Map<String, Object> mood0 = (Map<String, Object>) get(baseUrl + "/api/state").get("mood");
        assertEquals(App.DEFAULT_MOOD, mood0.get("name"));

        Map<String, Object> r = post(baseUrl + "/api/mood", map("mood", "맑음"));
        assertEquals("맑음", r.get("name"));
        assertEquals("sun", r.get("weather"));
        assertEquals("smile", r.get("face"));

        @SuppressWarnings("unchecked")
        Map<String, Object> mood1 = (Map<String, Object>) get(baseUrl + "/api/state").get("mood");
        assertEquals("맑음", mood1.get("name"));
    }
}
