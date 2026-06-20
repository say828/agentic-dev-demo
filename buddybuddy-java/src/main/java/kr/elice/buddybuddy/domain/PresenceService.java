package kr.elice.buddybuddy.domain;

import java.util.Set;
import java.util.TreeSet;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 접속 상태: login/logout 으로 온라인 집합을 관리한다.
 * Python server/contexts/buddybuddy/presence.py 포트.
 */
public class PresenceService {

    private final Set<String> onlineUsers =
            ConcurrentHashMap.newKeySet();

    /** 로그인: 온라인 집합에 추가. */
    public void login(String user) {
        onlineUsers.add(user);
    }

    /** 로그아웃: 온라인 집합에서 제거. */
    public void logout(String user) {
        onlineUsers.remove(user);
    }

    /** 해당 사용자가 온라인인가. */
    public boolean isOnline(String user) {
        return onlineUsers.contains(user);
    }

    /** "online" | "offline" 문자열 상태. */
    public String status(String user) {
        return isOnline(user) ? "online" : "offline";
    }

    /** 현재 온라인인 사용자들(정렬된 사본). */
    public Set<String> online() {
        return new TreeSet<>(onlineUsers);
    }
}
