package kr.elice.buddybuddy;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.junit.jupiter.api.Test;

import kr.elice.buddybuddy.web.Json;
import kr.elice.buddybuddy.web.Pages;

/** 웹 페이지 마커 + JSON 헬퍼 라운드트립. (smoke2.py 라우팅 검증 포트) */
class WebTest {

    @Test
    void lobbyHasLogin() {
        String lobby = Pages.lobby(new java.util.TreeSet<>(List.of("현주")));
        assertTrue(lobby.contains("로그인"), "로비에 '로그인' 버튼이 있어야 한다");
    }

    @Test
    void clientEmbedsMe() {
        String client = Pages.client("현주");
        assertTrue(client.contains("const ME = \"현주\""), "단일 클라이언트에 ME=현주가 박혀야 한다");
        assertTrue(client.contains("setInterval(refresh,1000)"), "1초 폴링이 있어야 한다");
    }

    @Test
    void demoHasStage() {
        String demo = Pages.demo();
        assertTrue(demo.contains("id=\"stage\""), "데모 페이지에 stage 가 있어야 한다");
    }

    @Test
    void jsonRoundTrip() {
        Map<String, Object> in = new LinkedHashMap<>();
        in.put("frm", "현주");
        in.put("to", "민수");
        in.put("text", "안녕 \"따옴표\" 와 줄바꿈\n포함");
        in.put("client_msg_id", "t1");
        String s = Json.write(in);
        Map<String, Object> out = Json.parseObject(s);
        assertEquals("현주", out.get("frm"));
        assertEquals("민수", out.get("to"));
        assertEquals("안녕 \"따옴표\" 와 줄바꿈\n포함", out.get("text"));
        assertEquals("t1", out.get("client_msg_id"));
    }

    @Test
    void jsonParsesNestedAndNumbers() {
        Object v = Json.parse("{\"a\":[1,2,3],\"b\":true,\"c\":null,\"d\":1.5}");
        assertTrue(v instanceof Map);
        @SuppressWarnings("unchecked")
        Map<String, Object> m = (Map<String, Object>) v;
        assertEquals(3, ((List<?>) m.get("a")).size());
        assertEquals(Boolean.TRUE, m.get("b"));
        assertEquals(1.5, m.get("d"));
    }
}
