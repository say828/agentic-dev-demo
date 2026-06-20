package kr.elice.cyworld;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.junit.jupiter.api.Test;

import kr.elice.cyworld.domain.GuestbookService;

/** test_regression.py 포팅: 방명록 최신순 + 비밀글 가시성. */
class RegressionTest {

    @Test
    void test_guestbook_recency_and_secret() {
        GuestbookService guestbook = new GuestbookService();
        guestbook.write("owner", "친구A", "안녕!");
        guestbook.write("owner", "친구B", "또 놀러옴");
        guestbook.write("owner", "친구C", "비밀 메시지", true);

        // 외부 구경꾼: 비밀글은 숨기고 최신순.
        List<Map<String, Object>> seen = guestbook.entries("owner", "구경꾼");
        assertEquals(List.of("친구B", "친구A"), authors(seen));

        // 주인: 비밀글까지 모두 최신순.
        List<Map<String, Object>> mine = guestbook.entries("owner", "owner");
        assertEquals(List.of("친구C", "친구B", "친구A"), authors(mine));
    }

    private static List<String> authors(List<Map<String, Object>> rows) {
        List<String> out = new ArrayList<>();
        for (Map<String, Object> e : rows) {
            out.add((String) e.get("author"));
        }
        return out;
    }
}
