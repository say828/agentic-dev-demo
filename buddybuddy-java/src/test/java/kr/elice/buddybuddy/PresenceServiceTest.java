package kr.elice.buddybuddy;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

import kr.elice.buddybuddy.domain.PresenceService;

/** 접속 상태: login/logout/isOnline/status/online. (test_presence.py 포트) */
class PresenceServiceTest {

    @Test
    void loginMakesUserOnline() {
        PresenceService p = new PresenceService();
        assertFalse(p.isOnline("현주"));
        p.login("현주");
        assertTrue(p.isOnline("현주"));
        assertEquals("online", p.status("현주"));
    }

    @Test
    void logoutMakesUserOffline() {
        PresenceService p = new PresenceService();
        p.login("현주");
        p.logout("현주");
        assertFalse(p.isOnline("현주"));
        assertEquals("offline", p.status("현주"));
    }

    @Test
    void statusOfUnknownIsOffline() {
        PresenceService p = new PresenceService();
        assertEquals("offline", p.status("nobody"));
    }

    @Test
    void onlineListsCurrentlyOnlineUsers() {
        PresenceService p = new PresenceService();
        p.login("현주");
        p.login("민수");
        p.logout("현주");
        assertTrue(p.online().contains("민수"));
        assertFalse(p.online().contains("현주"));
    }
}
