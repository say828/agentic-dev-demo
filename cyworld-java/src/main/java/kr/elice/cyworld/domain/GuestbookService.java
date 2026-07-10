package kr.elice.cyworld.domain;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 방명록: 기존 흐름(회귀 검증 대상 shared surface). 최신순 + 비밀글 가시성.
 *
 * <p>비밀글은 미니홈피 주인과 작성자만 볼 수 있다.
 */
public final class GuestbookService {

    private static final class Entry {
        final int seq;
        final String author;
        final String msg;
        final boolean secret;

        Entry(int seq, String author, String msg, boolean secret) {
            this.seq = seq;
            this.author = author;
            this.msg = msg;
            this.secret = secret;
        }
    }

    private final Map<String, List<Entry>> entries = new HashMap<>();
    private int seq = 0;

    public Map<String, Object> write(String owner, String author, String msg) {
        return write(owner, author, msg, false);
    }

    public Map<String, Object> write(String owner, String author, String msg, boolean secret) {
        seq += 1;
        entries.computeIfAbsent(owner, k -> new ArrayList<>()).add(new Entry(seq, author, msg, secret));
        Map<String, Object> res = new LinkedHashMap<>();
        res.put("status", "written");
        return res;
    }

    public List<Map<String, Object>> entries(String owner) {
        return entries(owner, null);
    }

    /** 최신순 + 비밀글 가시성. viewer 가 owner/author 가 아니면 비밀글은 숨긴다. */
    public List<Map<String, Object>> entries(String owner, String viewer) {
        List<Entry> rows = new ArrayList<>(entries.getOrDefault(owner, new ArrayList<>()));
        // reverse=True: seq 내림차순(최신순).
        rows.sort((x, y) -> Integer.compare(y.seq, x.seq));

        List<Map<String, Object>> out = new ArrayList<>();
        for (Entry e : rows) {
            if (e.secret && !(owner.equals(viewer) || e.author.equals(viewer))) {
                continue;
            }
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("author", e.author);
            m.put("msg", e.msg);
            m.put("secret", e.secret);
            out.add(m);
        }
        return out;
    }
}
