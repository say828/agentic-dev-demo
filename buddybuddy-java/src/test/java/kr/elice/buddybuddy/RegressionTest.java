package kr.elice.buddybuddy;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.List;

import org.junit.jupiter.api.Test;

import kr.elice.buddybuddy.domain.BuddyService;
import kr.elice.buddybuddy.domain.MessageService;
import kr.elice.buddybuddy.domain.PresenceService;

/**
 * 회귀(end-to-end): 현주 ↔ 민수 송수신 흐름이 presence/buddy/message 전반에서 일관되게 동작.
 * tmp/smoke.py 시나리오를 도메인 레벨로 포트. (test_regression.py 포트)
 */
class RegressionTest {

    @Test
    void endToEndConversationFlow() {
        PresenceService presence = new PresenceService();
        BuddyService buddy = new BuddyService();
        MessageService message = new MessageService();

        // 1) 두 사용자 로그인 + 버디
        presence.login("현주");
        presence.login("민수");
        buddy.add("현주", "민수");
        assertTrue(presence.isOnline("현주"));
        assertTrue(presence.isOnline("민수"));

        // 1) 현주 → 민수
        MessageService.SendResult s1 =
                message.send("현주", "민수", "민수야 테스트중 ㅋㅋ", "t1");
        assertEquals("sent", s1.status());

        // 2) 민수 unread = 1
        assertEquals(1, message.unread("민수", "현주"));

        // 3) 민수 → 현주
        message.send("민수", "현주", "오 도착했어!", "t2");

        // 4) t1 재전송 → 멱등(중복 없음)
        MessageService.SendResult s1again =
                message.send("현주", "민수", "민수야 테스트중 ㅋㅋ", "t1");
        assertTrue(s1again.replay());

        // 5) 스레드는 양쪽 동일, 총 2건
        List<MessageService.Message> th = message.thread("민수", "현주");
        assertEquals(2, th.size());
        assertEquals(message.thread("현주", "민수").size(), th.size());

        // 6) 민수 읽음 처리
        assertEquals(1, message.markRead("민수", "현주"));

        // 7) 읽음 후 unread = 0
        assertEquals(0, message.unread("민수", "현주"));

        // 8) 격리: 현주 ↔ 철수는 비어 있음
        assertTrue(message.thread("현주", "철수").isEmpty());
    }

    @Test
    void partnersAutoMergeForNewConversation() {
        // smoke2.py: 버디 추가 안 한 '지우'가 메시지를 보내면 현주의 대화 목록에 자동 노출.
        PresenceService presence = new PresenceService();
        MessageService message = new MessageService();

        presence.login("지우");
        message.send("지우", "현주", "현주야 나 지우야!", "z1");

        // 현주의 대화 상대에 지우 자동 포함(버디 추가 없이도)
        assertTrue(message.partners("현주").contains("지우"));

        message.send("현주", "지우", "오 지우야 안녕!", "h1");
        List<MessageService.Message> th = message.thread("지우", "현주");
        assertEquals(2, th.size());
    }

    @Test
    void logoutThenStateConsistent() {
        PresenceService presence = new PresenceService();
        presence.login("현주");
        presence.logout("현주");
        assertFalse(presence.isOnline("현주"));
        assertEquals("offline", presence.status("현주"));
    }
}
