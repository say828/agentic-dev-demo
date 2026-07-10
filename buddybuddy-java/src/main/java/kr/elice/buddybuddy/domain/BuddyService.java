package kr.elice.buddybuddy.domain;

import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

import kr.elice.buddybuddy.shared.Idem;

/**
 * 버디(친구) 관계: 멱등 추가, 자기추가 거부.
 * Python server/contexts/buddybuddy/buddy.py 포트.
 */
public class BuddyService {

    private final Idem.Store idem;
    // owner -> 추가된 버디들(삽입 순서 보존)
    private final Map<String, LinkedHashSet<String>> graph = new ConcurrentHashMap<>();

    public BuddyService() {
        this(new Idem.Store());
    }

    public BuddyService(Idem.Store idem) {
        this.idem = idem;
    }

    /**
     * owner 가 buddy 를 추가한다. 자기추가는 거부, 중복 추가는 멱등.
     *
     * @return 결과 상태("added" | "rejected" | "exists")와 replay 여부
     */
    public AddResult add(String owner, String buddy) {
        if (owner.equals(buddy)) {
            return new AddResult("rejected", "self_add", false);
        }
        String key = Idem.idempotencyKey(Map.of("owner", owner, "buddy", buddy));
        boolean already = graph.getOrDefault(owner, new LinkedHashSet<>()).contains(buddy);
        Idem.Result<String> r = idem.issueOnce(key, () -> {
            graph.computeIfAbsent(owner, k -> new LinkedHashSet<>()).add(buddy);
            return "added";
        });
        String status = (r.replay() || already) ? "exists" : "added";
        return new AddResult(status, "ok", r.replay());
    }

    /** owner 의 버디 목록(삽입 순서). */
    public List<String> buddies(String owner) {
        Set<String> s = graph.get(owner);
        return s == null ? List.of() : List.copyOf(s);
    }

    /** owner 가 buddy 를 가지고 있는가. */
    public boolean has(String owner, String buddy) {
        Set<String> s = graph.get(owner);
        return s != null && s.contains(buddy);
    }

    /** add() 결과. */
    public record AddResult(String status, String reason, boolean replay) {
    }
}
