package kr.elice.cyworld;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.Map;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import kr.elice.cyworld.domain.TodayService;

/** test_today.py 포팅. */
class TodayServiceTest {

    private TodayService today;

    @BeforeEach
    void setUp() {
        today = new TodayService();
    }

    @Test
    void test_today_counts_unique_visitor_once() {
        Map<String, Object> r1 = today.visit("owner", "guest", "2026-06-08");
        Map<String, Object> r2 = today.visit("owner", "guest", "2026-06-08");
        assertFalse((Boolean) r1.get("replay"));
        assertTrue((Boolean) r2.get("replay"));
        assertEquals(1, today.todayCount("owner", "2026-06-08"));
    }

    @Test
    void test_today_distinct_visitors() {
        today.visit("owner", "g1", "2026-06-08");
        today.visit("owner", "g2", "2026-06-08");
        assertEquals(2, today.todayCount("owner", "2026-06-08"));
    }

    @Test
    void test_today_resets_per_day_total_accumulates() {
        today.visit("owner", "g1", "2026-06-08");
        today.visit("owner", "g1", "2026-06-09");
        assertEquals(1, today.todayCount("owner", "2026-06-08"));
        assertEquals(1, today.todayCount("owner", "2026-06-09"));
        assertEquals(2, today.totalCount("owner"));
    }
}
