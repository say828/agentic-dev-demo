package kr.elice.cyworld.shared;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Map;
import java.util.TreeMap;

/**
 * 멱등 키 생성 헬퍼.
 *
 * <p>Python 의 {@code idempotency_key(payload)} 와 동등:
 * payload 를 키 정렬(sort_keys) + 비ASCII 보존(ensure_ascii=False)된 JSON 으로 직렬화한 뒤
 * sha256 hexdigest 를 반환한다.
 */
public final class Idem {

    private Idem() {
    }

    /** payload(dict) 를 결정적 JSON 으로 직렬화하고 sha256 hexdigest 를 반환한다. */
    public static String idempotencyKey(Map<String, Object> payload) {
        String raw = canonicalJson(payload);
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] digest = md.digest(raw.getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder(digest.length * 2);
            for (byte b : digest) {
                sb.append(Character.forDigit((b >> 4) & 0xF, 16));
                sb.append(Character.forDigit(b & 0xF, 16));
            }
            return sb.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException(e);
        }
    }

    /** json.dumps(payload, sort_keys=True, ensure_ascii=False) 와 같은 출력을 만든다. */
    private static String canonicalJson(Map<String, Object> payload) {
        // sort_keys: 키를 사전순 정렬한다.
        Map<String, Object> sorted = new TreeMap<>(payload);
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
        if (v instanceof String) {
            return "\"" + escape((String) v) + "\"";
        }
        if (v instanceof Boolean) {
            return ((Boolean) v) ? "true" : "false";
        }
        return String.valueOf(v);
    }

    private static String escape(String s) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch (c) {
                case '"':
                    sb.append("\\\"");
                    break;
                case '\\':
                    sb.append("\\\\");
                    break;
                default:
                    sb.append(c);
            }
        }
        return sb.toString();
    }
}
