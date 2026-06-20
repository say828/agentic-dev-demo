package kr.elice.buddybuddy.web;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

import kr.elice.buddybuddy.domain.BuddyService;
import kr.elice.buddybuddy.domain.MessageService;
import kr.elice.buddybuddy.domain.PresenceService;

/**
 * 의존성 제로 웹 프론트: JDK 내장 HttpServer 로 JSON API + HTML 페이지 제공.
 * Python server/web/app.py 포트 (http.server 미러).
 *
 * 라우트:
 *   GET  /              로비(?me 없으면) 또는 단일 클라이언트(?me=현주)
 *   GET  /demo          두 패널 데모
 *   GET  /api/state?me= 대화 상태(버디 + partners 병합, online/unread 포함)
 *   GET  /api/thread?a=&b=  순서 무관 스레드
 *   POST /api/login     {user}
 *   POST /api/logout    {user}
 *   POST /api/buddy_add {owner, buddy}
 *   POST /api/send      {frm, to, text, client_msg_id}
 *   POST /api/read      {reader, other}
 */
public class App {

    private final PresenceService presence = new PresenceService();
    private final BuddyService buddy = new BuddyService();
    private final MessageService message = new MessageService();

    public PresenceService presence() {
        return presence;
    }

    public BuddyService buddy() {
        return buddy;
    }

    public MessageService message() {
        return message;
    }

    // ------------------------------------------------------------------
    // 서버 부트스트랩
    // ------------------------------------------------------------------

    public static void main(String[] args) throws IOException {
        int port = 8010;
        if (args.length > 0) {
            port = Integer.parseInt(args[0]);
        }
        App app = new App();
        app.seedDemo();
        HttpServer server = HttpServer.create(new InetSocketAddress(port), 0);
        server.createContext("/", app::route);
        server.setExecutor(null);
        server.start();
        System.out.println("버디버디 메신저 running at http://localhost:" + port
                + "  (try /?me=현주 and /?me=민수, or /demo)");
    }

    /** 데모 시작 시 현주/민수를 온라인·버디로 시드. */
    private void seedDemo() {
        presence.login("현주");
        presence.login("민수");
        buddy.add("현주", "민수");
        buddy.add("민수", "현주");
    }

    // ------------------------------------------------------------------
    // 라우팅
    // ------------------------------------------------------------------

    void route(HttpExchange ex) throws IOException {
        try {
            String path = ex.getRequestURI().getPath();
            Map<String, String> q = parseQuery(ex.getRequestURI().getRawQuery());
            switch (path) {
                case "/" -> {
                    String me = q.get("me");
                    if (me != null && !me.isEmpty()) {
                        sendHtml(ex, Pages.client(me));
                    } else {
                        sendHtml(ex, Pages.lobby(presence.online()));
                    }
                }
                case "/demo" -> sendHtml(ex, Pages.demo());
                case "/api/state" -> apiState(ex, q);
                case "/api/thread" -> apiThread(ex, q);
                case "/api/login" -> apiLogin(ex);
                case "/api/logout" -> apiLogout(ex);
                case "/api/buddy_add" -> apiBuddyAdd(ex);
                case "/api/send" -> apiSend(ex);
                case "/api/read" -> apiRead(ex);
                default -> sendText(ex, 404, "not found");
            }
        } catch (Exception e) {
            sendText(ex, 500, "error: " + e.getMessage());
        }
    }

    // ------------------------------------------------------------------
    // JSON API
    // ------------------------------------------------------------------

    /** 대화 상태: 버디 + 대화상대(partners)를 병합, 각 상대의 online/unread 포함. */
    private void apiState(HttpExchange ex, Map<String, String> q) throws IOException {
        String me = q.getOrDefault("me", "");
        Set<String> names = new LinkedHashSet<>(buddy.buddies(me));
        names.addAll(message.partners(me)); // 대화한 적 있으면 자동 노출
        List<Map<String, Object>> buddies = new ArrayList<>();
        for (String name : names) {
            Map<String, Object> b = new LinkedHashMap<>();
            b.put("name", name);
            b.put("online", presence.isOnline(name));
            b.put("unread", message.unread(me, name));
            buddies.add(b);
        }
        Map<String, Object> out = new LinkedHashMap<>();
        out.put("me", me);
        out.put("online", presence.isOnline(me));
        out.put("buddies", buddies);
        sendJson(ex, out);
    }

    /** 순서 무관 스레드. */
    private void apiThread(HttpExchange ex, Map<String, String> q) throws IOException {
        String a = q.getOrDefault("a", "");
        String b = q.getOrDefault("b", "");
        List<Map<String, Object>> out = new ArrayList<>();
        for (MessageService.Message m : message.thread(a, b)) {
            out.add(m.toMap());
        }
        sendJson(ex, out);
    }

    private void apiLogin(HttpExchange ex) throws IOException {
        Map<String, Object> body = readJson(ex);
        String user = str(body.get("user"));
        presence.login(user);
        sendJson(ex, Map.of("ok", true, "user", user, "status", presence.status(user)));
    }

    private void apiLogout(HttpExchange ex) throws IOException {
        Map<String, Object> body = readJson(ex);
        String user = str(body.get("user"));
        presence.logout(user);
        sendJson(ex, Map.of("ok", true, "user", user, "status", presence.status(user)));
    }

    private void apiBuddyAdd(HttpExchange ex) throws IOException {
        Map<String, Object> body = readJson(ex);
        BuddyService.AddResult r = buddy.add(str(body.get("owner")), str(body.get("buddy")));
        sendJson(ex, Map.of("status", r.status(), "reason", r.reason(), "replay", r.replay()));
    }

    private void apiSend(HttpExchange ex) throws IOException {
        Map<String, Object> body = readJson(ex);
        MessageService.SendResult r = message.send(
                str(body.get("frm")), str(body.get("to")),
                str(body.get("text")), str(body.get("client_msg_id")));
        Map<String, Object> out = new LinkedHashMap<>();
        out.put("status", r.status());
        out.put("seq", r.seq());
        out.put("replay", r.replay());
        sendJson(ex, out);
    }

    private void apiRead(HttpExchange ex) throws IOException {
        Map<String, Object> body = readJson(ex);
        int n = message.markRead(str(body.get("reader")), str(body.get("other")));
        sendJson(ex, Map.of("ok", true, "read", n));
    }

    // ------------------------------------------------------------------
    // HTTP 헬퍼
    // ------------------------------------------------------------------

    private static String str(Object o) {
        return o == null ? null : o.toString();
    }

    private Map<String, Object> readJson(HttpExchange ex) throws IOException {
        byte[] raw = ex.getRequestBody().readAllBytes();
        String s = new String(raw, StandardCharsets.UTF_8);
        if (s.isBlank()) {
            return new LinkedHashMap<>();
        }
        return Json.parseObject(s);
    }

    private static Map<String, String> parseQuery(String raw) {
        Map<String, String> q = new LinkedHashMap<>();
        if (raw == null || raw.isEmpty()) {
            return q;
        }
        for (String pair : raw.split("&")) {
            int eq = pair.indexOf('=');
            if (eq < 0) {
                q.put(dec(pair), "");
            } else {
                q.put(dec(pair.substring(0, eq)), dec(pair.substring(eq + 1)));
            }
        }
        return q;
    }

    private static String dec(String s) {
        return URLDecoder.decode(s, StandardCharsets.UTF_8);
    }

    private void sendJson(HttpExchange ex, Object value) throws IOException {
        byte[] body = Json.write(value).getBytes(StandardCharsets.UTF_8);
        ex.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
        ex.sendResponseHeaders(200, body.length);
        try (OutputStream os = ex.getResponseBody()) {
            os.write(body);
        }
    }

    private void sendHtml(HttpExchange ex, String html) throws IOException {
        byte[] body = html.getBytes(StandardCharsets.UTF_8);
        ex.getResponseHeaders().set("Content-Type", "text/html; charset=utf-8");
        ex.sendResponseHeaders(200, body.length);
        try (OutputStream os = ex.getResponseBody()) {
            os.write(body);
        }
    }

    private void sendText(HttpExchange ex, int code, String text) throws IOException {
        byte[] body = text.getBytes(StandardCharsets.UTF_8);
        ex.getResponseHeaders().set("Content-Type", "text/plain; charset=utf-8");
        ex.sendResponseHeaders(code, body.length);
        try (OutputStream os = ex.getResponseBody()) {
            os.write(body);
        }
    }
}
