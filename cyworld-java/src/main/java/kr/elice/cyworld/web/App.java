package kr.elice.cyworld.web;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;

import kr.elice.cyworld.domain.DotoriService;
import kr.elice.cyworld.domain.GuestbookService;
import kr.elice.cyworld.domain.IlchonService;
import kr.elice.cyworld.domain.InsufficientDotori;
import kr.elice.cyworld.domain.PurchaseResult;
import kr.elice.cyworld.domain.TodayService;

/**
 * 미니홈피 로컬 웹 프론트 (의존성 0, JDK 내장 com.sun.net.httpserver).
 *
 * <p>기존 백엔드 서비스(dotori/ilchon/today/guestbook)를 JSON API로 노출하고,
 * 단일 HTML 페이지(미니홈피)에서 호출한다. Python 의 server/web/app.py 를 포팅했다.
 *
 * <p>실행:  java kr.elice.cyworld.web.App   # → http://localhost:8000
 */
public final class App {

    public static final String OWNER = "도토리";
    public static final String DAY = "2026-06-08";

    // 방 꾸미기 상점: 구매 아이템 → 방 변화 (벽지 색 / BGM 곡명)
    public static final Map<String, String> WALLPAPERS = Map.of(
            "벽지:하늘", "#bfe6ff",
            "벽지:노을", "#ffd9b0",
            "벽지:벚꽃", "#ffe3ee");
    public static final Map<String, String> BGMS = Map.of(
            "BGM:첫눈", "첫눈",
            "BGM:벚꽃엔딩", "벚꽃엔딩",
            "BGM:붉은노을", "붉은노을");
    public static final String DEFAULT_WALL = "#fdeede";
    public static final String DEFAULT_BGM = "첫눈";

    // 오늘의 기분: 창문 날씨 + 미니미 표정
    public static final Map<String, Map<String, Object>> MOODS = buildMoods();
    public static final String DEFAULT_MOOD = "비";

    private static Map<String, Map<String, Object>> buildMoods() {
        Map<String, Map<String, Object>> m = new LinkedHashMap<>();
        m.put("맑음", mood("☀️", "#bfe6ff", "sun", "smile"));
        m.put("흐림", mood("☁️", "#d7dee6", "cloud", "neutral"));
        m.put("비", mood("🌧️", "#9fb4c8", "rain", "sad"));
        m.put("행복", mood("😊", "#cdefff", "sun", "smile"));
        return m;
    }

    private static Map<String, Object> mood(String emoji, String sky, String weather, String face) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("emoji", emoji);
        m.put("sky", sky);
        m.put("weather", weather);
        m.put("face", face);
        return m;
    }

    private static final String PAGE = loadPage();

    private static String loadPage() {
        try (InputStream in = App.class.getResourceAsStream("page.html")) {
            if (in == null) {
                throw new IllegalStateException("page.html resource not found");
            }
            return new String(in.readAllBytes(), StandardCharsets.UTF_8);
        } catch (IOException e) {
            throw new IllegalStateException(e);
        }
    }

    // ---- 가변 상태: 서비스 + 기분 ----
    public DotoriService dotori = new DotoriService();
    public IlchonService ilchon = new IlchonService();
    public TodayService today = new TodayService();
    public GuestbookService guestbook = new GuestbookService();
    private final Map<String, String> moodState = new LinkedHashMap<>();

    public App() {
        moodState.put("mood", DEFAULT_MOOD);
        seed();
    }

    /** 데모 시드 데이터 (app.py 의 _seed). */
    public void seed() {
        dotori.charge(OWNER, 500);
        guestbook.write(OWNER, "친구A", "미니홈피 개설 축하해~");
        guestbook.write(OWNER, "친구B", "일촌 신청했어!");
        today.visit(OWNER, "친구A", DAY);
        today.visit(OWNER, "친구B", DAY);
        ilchon.request("친구B", OWNER);
    }

    /** 방 상태: 보유 아이템에서 벽지·BGM 을 결정. */
    public Map<String, Object> roomOf(String owner) {
        List<String> owned = dotori.owned(owner);
        String wall = DEFAULT_WALL;
        for (String i : owned) {
            if (WALLPAPERS.containsKey(i)) {
                wall = WALLPAPERS.get(i);
                break;
            }
        }
        String bgm = DEFAULT_BGM;
        for (String i : owned) {
            if (BGMS.containsKey(i)) {
                bgm = BGMS.get(i);
                break;
            }
        }
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("wallpaper", wall);
        m.put("bgm", bgm);
        m.put("owned", owned);
        return m;
    }

    /** 현재 기분 정보: name + MOODS[name] 의 필드들. */
    public Map<String, Object> moodOf() {
        String name = moodState.get("mood");
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("name", name);
        m.putAll(MOODS.get(name));
        return m;
    }

    /** /api/state 의 응답을 만든다. */
    public Map<String, Object> state(String owner, String viewer, String day) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("owner", owner);
        m.put("today", today.todayCount(owner, day));
        m.put("total", today.totalCount(owner));
        m.put("balance", dotori.balance(owner));
        m.put("ilchons", ilchon.ilchons(owner));
        m.put("guestbook", guestbook.entries(owner, viewer));
        m.put("room", roomOf(owner));
        m.put("mood", moodOf());
        return m;
    }

    // ---------- HTTP ----------

    private void handleGet(HttpExchange ex) throws IOException {
        String path = ex.getRequestURI().getPath();
        if ("/".equals(path)) {
            send(ex, 200, PAGE, "text/html");
            return;
        }
        if ("/api/state".equals(path)) {
            Map<String, List<String>> q = parseQuery(ex.getRequestURI().getRawQuery());
            String owner = first(q, "owner", OWNER);
            String viewer = first(q, "viewer", OWNER);
            String day = first(q, "day", DAY);
            sendJson(ex, 200, state(owner, viewer, day));
            return;
        }
        sendJson(ex, 404, error("not_found"));
    }

    private void handlePost(HttpExchange ex) throws IOException {
        String path = ex.getRequestURI().getPath();
        Map<String, Object> b;
        try {
            b = readBody(ex);
            switch (path) {
                case "/api/charge": {
                    int bal = dotori.charge(str(b, "user"), toInt(b.get("amount")));
                    Map<String, Object> res = new LinkedHashMap<>();
                    res.put("balance", bal);
                    sendJson(ex, 200, res);
                    return;
                }
                case "/api/purchase": {
                    PurchaseResult r = dotori.purchase(str(b, "user"), str(b, "item"),
                            toInt(b.get("price")), b.get("order_id") == null ? null : str(b, "order_id"));
                    Map<String, Object> res = new LinkedHashMap<>();
                    res.put("status", r.status);
                    res.put("balance", r.balance);
                    res.put("replay", r.replay);
                    sendJson(ex, 200, res);
                    return;
                }
                case "/api/ilchon_request":
                    sendJson(ex, 200, ilchon.request(str(b, "frm"), str(b, "to")));
                    return;
                case "/api/ilchon_accept":
                    sendJson(ex, 200, ilchon.accept(str(b, "frm"), str(b, "to")));
                    return;
                case "/api/visit":
                    sendJson(ex, 200, today.visit(str(b, "owner"), str(b, "visitor"),
                            b.get("day") == null ? DAY : str(b, "day")));
                    return;
                case "/api/mood": {
                    Object m = b.get("mood");
                    if (m != null && MOODS.containsKey(m)) {
                        moodState.put("mood", (String) m);
                    }
                    sendJson(ex, 200, moodOf());
                    return;
                }
                case "/api/guestbook":
                    sendJson(ex, 200, guestbook.write(str(b, "owner"), str(b, "author"),
                            str(b, "msg"), toBool(b.get("secret"))));
                    return;
                default:
                    sendJson(ex, 404, error("not_found"));
                    return;
            }
        } catch (InsufficientDotori e) {
            sendJson(ex, 200, error(e.getMessage()));
        } catch (RuntimeException e) {
            sendJson(ex, 400, error("bad_request: " + e));
        }
    }

    // ---------- 헬퍼 ----------

    private static Map<String, Object> error(String msg) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("error", msg);
        return m;
    }

    private Map<String, Object> readBody(HttpExchange ex) throws IOException {
        byte[] raw = ex.getRequestBody().readAllBytes();
        if (raw.length == 0) {
            return new LinkedHashMap<>();
        }
        return Json.loadsObject(new String(raw, StandardCharsets.UTF_8));
    }

    private static String str(Map<String, Object> b, String key) {
        Object v = b.get(key);
        if (v == null) {
            throw new IllegalArgumentException("missing key: " + key);
        }
        return v.toString();
    }

    private static int toInt(Object v) {
        if (v instanceof Number) {
            return ((Number) v).intValue();
        }
        return Integer.parseInt(v.toString());
    }

    private static boolean toBool(Object v) {
        if (v == null) {
            return false;
        }
        if (v instanceof Boolean) {
            return (Boolean) v;
        }
        return Boolean.parseBoolean(v.toString());
    }

    private static String first(Map<String, List<String>> q, String key, String dflt) {
        List<String> vs = q.get(key);
        return (vs == null || vs.isEmpty()) ? dflt : vs.get(0);
    }

    private static Map<String, List<String>> parseQuery(String raw) {
        Map<String, List<String>> out = new LinkedHashMap<>();
        if (raw == null || raw.isEmpty()) {
            return out;
        }
        for (String pair : raw.split("&")) {
            int eq = pair.indexOf('=');
            String k = eq >= 0 ? pair.substring(0, eq) : pair;
            String v = eq >= 0 ? pair.substring(eq + 1) : "";
            out.computeIfAbsent(urlDecode(k), x -> new ArrayList<>()).add(urlDecode(v));
        }
        return out;
    }

    private static String urlDecode(String s) {
        try {
            return java.net.URLDecoder.decode(s, StandardCharsets.UTF_8);
        } catch (RuntimeException e) {
            return s;
        }
    }

    private void sendJson(HttpExchange ex, int code, Object body) throws IOException {
        send(ex, code, Json.dumps(body), "application/json");
    }

    private void send(HttpExchange ex, int code, String body, String ctype) throws IOException {
        byte[] data = body.getBytes(StandardCharsets.UTF_8);
        ex.getResponseHeaders().set("Content-Type", ctype + "; charset=utf-8");
        ex.sendResponseHeaders(code, data.length);
        try (OutputStream os = ex.getResponseBody()) {
            os.write(data);
        }
    }

    /** HttpServer 를 만들고 핸들러를 등록한다 (start 는 호출자가). */
    public HttpServer createServer(int port) throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", port), 0);
        HttpHandler handler = ex -> {
            try {
                if ("GET".equalsIgnoreCase(ex.getRequestMethod())) {
                    handleGet(ex);
                } else if ("POST".equalsIgnoreCase(ex.getRequestMethod())) {
                    handlePost(ex);
                } else {
                    sendJson(ex, 404, error("not_found"));
                }
            } catch (IOException io) {
                ex.close();
            }
        };
        server.createContext("/", handler);
        server.setExecutor(null);
        return server;
    }

    public static void main(String[] args) throws IOException {
        int port = args.length > 0 ? Integer.parseInt(args[0]) : 8000;
        App app = new App();
        HttpServer server = app.createServer(port);
        server.start();
        System.out.println("미니홈피: http://localhost:" + port + "  (Ctrl+C 종료)");
    }
}
