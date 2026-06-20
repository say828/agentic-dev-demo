package kr.elice.buddybuddy;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

import kr.elice.buddybuddy.domain.BuddyService;

/** 버디: 멱등 추가, has, 자기추가 거부. (test_buddy.py 포트) */
class BuddyServiceTest {

    @Test
    void addThenHas() {
        BuddyService b = new BuddyService();
        BuddyService.AddResult r = b.add("현주", "민수");
        assertEquals("added", r.status());
        assertTrue(b.has("현주", "민수"));
        assertTrue(b.buddies("현주").contains("민수"));
    }

    @Test
    void addIsIdempotent() {
        BuddyService b = new BuddyService();
        b.add("현주", "민수");
        BuddyService.AddResult r2 = b.add("현주", "민수"); // 재요청
        assertTrue(r2.replay());
        assertEquals(1, b.buddies("현주").size()); // 중복 없음
    }

    @Test
    void selfAddRejected() {
        BuddyService b = new BuddyService();
        BuddyService.AddResult r = b.add("현주", "현주");
        assertEquals("rejected", r.status());
        assertEquals("self_add", r.reason());
        assertFalse(b.has("현주", "현주"));
    }

    @Test
    void buddiesEmptyForUnknown() {
        BuddyService b = new BuddyService();
        assertTrue(b.buddies("아무도").isEmpty());
    }
}
