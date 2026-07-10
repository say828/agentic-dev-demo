package kr.elice.cyworld;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.List;
import java.util.Map;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import kr.elice.cyworld.domain.IlchonService;

/** test_ilchon.py 포팅. */
class IlchonServiceTest {

    private IlchonService ilchon;

    @BeforeEach
    void setUp() {
        ilchon = new IlchonService();
    }

    @Test
    void test_not_ilchon_until_accept() {
        ilchon.request("a", "b");
        assertFalse(ilchon.areIlchon("a", "b"));
    }

    @Test
    void test_request_then_accept_is_mutual() {
        ilchon.request("a", "b");
        assertEquals("accepted", ilchon.accept("a", "b").get("status"));
        assertTrue(ilchon.areIlchon("a", "b"));
        assertTrue(ilchon.areIlchon("b", "a"));
        assertEquals(List.of("b"), ilchon.ilchons("a"));
        assertEquals(List.of("a"), ilchon.ilchons("b"));
    }

    @Test
    void test_request_idempotent() {
        Map<String, Object> r1 = ilchon.request("a", "b");
        Map<String, Object> r2 = ilchon.request("a", "b");
        assertEquals(Boolean.FALSE, r1.get("replay"));
        assertEquals(Boolean.TRUE, r2.get("replay"));
    }

    @Test
    void test_accept_without_request() {
        assertEquals("no_request", ilchon.accept("a", "b").get("status"));
    }

    @Test
    void test_self_ilchon_rejected() {
        assertThrows(IllegalArgumentException.class, () -> ilchon.request("a", "a"));
    }
}
