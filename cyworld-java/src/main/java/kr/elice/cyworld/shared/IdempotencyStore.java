package kr.elice.cyworld.shared;

import java.util.HashMap;
import java.util.Map;
import java.util.function.Supplier;

/**
 * 멱등 처리: idempotency_key로 이중 결제·중복 신청을 차단한다.
 *
 * <p>auth 데모의 shared/idem.py와 동일 패턴(컨텍스트 간 재사용).
 * 성공 결과만 캐시한다 — fn()이 예외를 던지면 캐시하지 않으므로 재시도가 가능하다.
 */
public final class IdempotencyStore {

    /** issue_once 의 반환값: 결과 + replay 여부. */
    public static final class Issued<T> {
        public final T result;
        public final boolean replay;

        public Issued(T result, boolean replay) {
            this.result = result;
            this.replay = replay;
        }
    }

    private final Map<String, Object> seen = new HashMap<>();

    /**
     * key 가 처음이면 fn() 을 실행해 결과를 캐시하고 (result, false) 를 반환한다.
     * 이미 본 key 면 캐시된 결과와 (result, true) 를 반환한다.
     * fn() 이 예외를 던지면 캐시하지 않는다 — 재시도 가능.
     */
    @SuppressWarnings("unchecked")
    public <T> Issued<T> issueOnce(String key, Supplier<T> fn) {
        if (seen.containsKey(key)) {
            return new Issued<>((T) seen.get(key), true);
        }
        T result = fn.get();
        seen.put(key, result);
        return new Issued<>(result, false);
    }
}
