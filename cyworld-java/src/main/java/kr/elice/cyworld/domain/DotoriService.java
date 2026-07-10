package kr.elice.cyworld.domain;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeSet;

import kr.elice.cyworld.shared.Idem;
import kr.elice.cyworld.shared.IdempotencyStore;

/**
 * 도토리(가상화폐): 충전·잔액·아이템 구매(차감) + 잔액부족 거부 + 이중결제 멱등.
 *
 * <p>순수 산술 + 멱등 → 결정적으로 검증된다(외부 PG·실시간 비의존).
 */
public final class DotoriService {

    private final IdempotencyStore idem;
    private final Map<String, Integer> balance = new HashMap<>();
    private final Map<String, TreeSet<String>> owned = new HashMap<>();

    public DotoriService() {
        this(null);
    }

    public DotoriService(IdempotencyStore idem) {
        this.idem = idem != null ? idem : new IdempotencyStore();
    }

    /** 도토리 충전 (양수만 허용). 새 잔액을 반환한다. */
    public int charge(String user, int amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("충전액은 양수여야 한다");
        }
        int next = balance.getOrDefault(user, 0) + amount;
        balance.put(user, next);
        return next;
    }

    public int balance(String user) {
        return balance.getOrDefault(user, 0);
    }

    /** 아이템 구매 (차감 + 멱등). order_id 가 없으면 (user,item) 기반 키를 만든다. */
    public PurchaseResult purchase(String user, String item, int price) {
        return purchase(user, item, price, null);
    }

    public PurchaseResult purchase(String user, String item, int price, String orderId) {
        String key;
        if (orderId != null && !orderId.isEmpty()) {
            key = orderId;
        } else {
            Map<String, Object> payload = new LinkedHashMap<>();
            payload.put("user", user);
            payload.put("item", item);
            key = Idem.idempotencyKey(payload);
        }

        IdempotencyStore.Issued<PurchaseResult> issued = idem.issueOnce(key, () -> {
            int bal = balance.getOrDefault(user, 0);
            if (bal < price) {
                throw new InsufficientDotori("잔액 부족: balance=" + bal + " < price=" + price);
            }
            balance.put(user, bal - price);
            owned.computeIfAbsent(user, k -> new TreeSet<>()).add(item);
            return new PurchaseResult("purchased", item, price, balance.get(user), key, false);
        });

        return issued.result.withReplay(issued.replay);
    }

    /** 보유 아이템 (정렬된 목록). */
    public List<String> owned(String user) {
        TreeSet<String> set = owned.get(user);
        return set == null ? new ArrayList<>() : new ArrayList<>(set);
    }
}
