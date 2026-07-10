package kr.elice.buddybuddy;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.List;

import org.junit.jupiter.api.Test;

import kr.elice.buddybuddy.domain.MessageService;

/** 메시지 핵심: 멱등 전송, 스레드 격리, 읽음 처리, 대화상대. (test_message.py 포트) */
class MessageServiceTest {

    @Test
    void sendIdempotentViaClientMsgId() {
        MessageService m = new MessageService();
        MessageService.SendResult r1 = m.send("현주", "민수", "안녕", "c1");
        MessageService.SendResult r2 = m.send("현주", "민수", "안녕", "c1"); // 재전송
        assertEquals("sent", r1.status());
        assertTrue(r2.replay());
        assertEquals(r1.seq(), r2.seq());
        assertEquals(1, m.thread("현주", "민수").size()); // 한 건만 기록
    }

    @Test
    void sameTextDistinctIdsBothRecorded() {
        MessageService m = new MessageService();
        m.send("현주", "민수", "ㅋㅋ", "c1");
        m.send("현주", "민수", "ㅋㅋ", "c2"); // 같은 텍스트, 다른 id
        assertEquals(2, m.thread("현주", "민수").size());
    }

    @Test
    void contentHashFallbackWhenNoClientMsgId() {
        MessageService m = new MessageService();
        m.send("현주", "민수", "동일내용", null);
        MessageService.SendResult r2 = m.send("현주", "민수", "동일내용", null); // content-hash 멱등
        assertTrue(r2.replay());
        assertEquals(1, m.thread("현주", "민수").size());
    }

    @Test
    void threadUnorderedPair() {
        MessageService m = new MessageService();
        m.send("현주", "민수", "하이", "c1");
        m.send("민수", "현주", "오 안녕", "c2");
        // thread(a,b) == thread(b,a)
        List<MessageService.Message> ab = m.thread("현주", "민수");
        List<MessageService.Message> ba = m.thread("민수", "현주");
        assertEquals(2, ab.size());
        assertEquals(ab.size(), ba.size());
        assertEquals(ab.get(0).seq, ba.get(0).seq);
    }

    @Test
    void threadsIsolated() {
        MessageService m = new MessageService();
        m.send("현주", "민수", "비밀", "c1");
        assertEquals(1, m.thread("현주", "민수").size());
        assertTrue(m.thread("현주", "철수").isEmpty()); // 다른 쌍은 비어 있음
    }

    @Test
    void markReadClearsUnread() {
        MessageService m = new MessageService();
        m.send("민수", "현주", "메시지1", "c1");
        m.send("민수", "현주", "메시지2", "c2");
        assertEquals(2, m.unread("현주", "민수"));
        int cleared = m.markRead("현주", "민수");
        assertEquals(2, cleared);
        assertEquals(0, m.unread("현주", "민수"));
    }

    @Test
    void unreadCountsOnlyIncomingUnread() {
        MessageService m = new MessageService();
        m.send("현주", "민수", "내가보낸것", "c1"); // 현주 입장에선 보낸 것 → unread 아님
        m.send("민수", "현주", "받은것", "c2");
        assertEquals(1, m.unread("현주", "민수")); // 현주는 민수가 보낸 1건만 unread
        assertEquals(1, m.unread("민수", "현주")); // 민수는 현주가 보낸 1건만 unread
    }

    @Test
    void partnersListsConversationOthers() {
        MessageService m = new MessageService();
        m.send("현주", "민수", "하이", "c1");
        m.send("철수", "현주", "안녕", "c2");
        List<String> p = m.partners("현주");
        assertTrue(p.contains("민수"));
        assertTrue(p.contains("철수"));
    }

    @Test
    void selfMessageRejected() {
        MessageService m = new MessageService();
        MessageService.SendResult r = m.send("현주", "현주", "혼잣말", "c1");
        assertEquals("rejected", r.status());
        assertTrue(m.thread("현주", "현주").isEmpty());
    }

    @Test
    void emptyMessageRejected() {
        MessageService m = new MessageService();
        assertEquals("rejected", m.send("현주", "민수", "", "c1").status());
        assertEquals("rejected", m.send("현주", "민수", "   ", "c2").status());
        assertTrue(m.thread("현주", "민수").isEmpty());
    }
}
