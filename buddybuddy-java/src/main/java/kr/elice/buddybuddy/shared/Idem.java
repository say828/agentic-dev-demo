package kr.elice.buddybuddy.shared;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Map;
import java.util.TreeMap;
import java.util.function.Supplier;

/**
 * 멱등 처리: idempotency_key로 중복 처리를 차단한다.
 * Python server/shared/idem.py 의 IdempotencyStore + idempotency_key 포트.
 */
public final class Idem {

    private Idem() {
    }

    /**
     * payload(키 정렬 + UTF-8 보존)를 SHA-256으로 해싱한 멱등키.
     * Python: hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False)).hexdigest()
     */
    public static String idempotencyKey(Map<String, ?> payload) {
        String raw = canonicalJson(payload);
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] hash = md.digest(raw.getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder(hash.length * 2);
            for (byte b : hash) {
                sb.append(Character.forDigit((b >> 4) & 0xF, 16));
                sb.append(Character.forDigit(b & 0xF, 16));
            }
            return sb.toString();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    /** 키 정렬된, ensure_ascii=False 와 동일하게 비ASCII 보존하는 작은 JSON 직렬화. */
    private static String canonicalJson(Map<String, ?> payload) {
        TreeMap<String, Object> sorted = new TreeMap<>();
        for (Map.Entry<String, ?> e : payload.entrySet()) {
            sorted.put(e.getKey(), e.getValue());
        }
        StringBuilder sb = new StringBuilder("{");
        boolean first = true;
        for (Map.Entry<String, Object> e : sorted.entrySet()) {
            if (!first) {
                sb.append(", ");
            }
            first = false;
            sb.append('"').append(escape(e.getKey())).append("\": ");
            sb.append(jsonValue(e.getValue()));
        }
        sb.append('}');
        return sb.toString();
    }

    private static String jsonValue(Object v) {
        if (v == null) {
            return "null";
        }
        if (v instanceof Number || v instanceof Boolean) {
            return v.toString();
        }
        return '"' + escape(v.toString()) + '"';
    }

    private static String escape(String s) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch (c) {
                case '"' -> sb.append("\\\"");
                case '\\' -> sb.append("\\\\");
                default -> sb.append(c);
            }
        }
        return sb.toString();
    }

    /** issue_once(key, fn): 처음이면 fn 실행·기억, 재요청이면 기억된 값을 replay=true 로 반환. */
    public static final class Store {
        private final Map<String, Object> seen = new java.util.HashMap<>();

        /** @return Result(value, replay) */
        @SuppressWarnings("unchecked")
        public <T> Result<T> issueOnce(String key, Supplier<T> fn) {
            if (seen.containsKey(key)) {
                return new Result<>((T) seen.get(key), true);
            }
            T result = fn.get();
            seen.put(key, result);
            return new Result<>(result, false);
        }
    }

    /** (값, replay) 페어. */
    public record Result<T>(T value, boolean replay) {
    }
}
