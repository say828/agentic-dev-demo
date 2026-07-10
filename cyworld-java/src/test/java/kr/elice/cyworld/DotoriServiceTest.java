package kr.elice.cyworld;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.List;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import kr.elice.cyworld.domain.DotoriService;
import kr.elice.cyworld.domain.InsufficientDotori;
import kr.elice.cyworld.domain.PurchaseResult;

/** test_dotori.py 포팅. */
class DotoriServiceTest {

    private DotoriService dotori;

    @BeforeEach
    void setUp() {
        dotori = new DotoriService();
    }

    @Test
    void test_charge_and_balance() {
        assertEquals(100, dotori.charge("a", 100));
        assertEquals(150, dotori.charge("a", 50));
        assertEquals(150, dotori.balance("a"));
    }

    @Test
    void test_charge_rejects_nonpositive() {
        assertThrows(IllegalArgumentException.class, () -> dotori.charge("a", 0));
    }

    @Test
    void test_purchase_deducts() {
        dotori.charge("a", 200);
        PurchaseResult r = dotori.purchase("a", "미니룸스킨", 120, "o1");
        assertEquals("purchased", r.status);
        assertEquals(80, r.balance);
        assertEquals(80, dotori.balance("a"));
    }

    @Test
    void test_purchase_insufficient() {
        dotori.charge("a", 50);
        assertThrows(InsufficientDotori.class, () -> dotori.purchase("a", "BGM", 100, "o1"));
        assertEquals(50, dotori.balance("a"));
    }

    @Test
    void test_purchase_idempotent() {
        dotori.charge("a", 200);
        PurchaseResult r1 = dotori.purchase("a", "폰트", 70, "ord-1");
        PurchaseResult r2 = dotori.purchase("a", "폰트", 70, "ord-1");
        assertFalse(r1.replay);
        assertTrue(r2.replay);
        assertEquals(130, dotori.balance("a"));
    }

    @Test
    void test_purchase_grants_item() {
        dotori.charge("a", 300);
        dotori.purchase("a", "벽지:하늘", 80, "o1");
        dotori.purchase("a", "BGM:벚꽃엔딩", 50, "o2");
        assertEquals(List.of("BGM:벚꽃엔딩", "벽지:하늘"), dotori.owned("a"));
    }

    @Test
    void test_idempotent_purchase_single_grant() {
        dotori.charge("a", 300);
        dotori.purchase("a", "벽지:하늘", 80, "o1");
        dotori.purchase("a", "벽지:하늘", 80, "o1");
        assertEquals(List.of("벽지:하늘"), dotori.owned("a"));
    }
}
