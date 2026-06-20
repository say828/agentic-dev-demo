package kr.elice.cyworld.domain;

import java.util.List;

/**
 * 화면 렌더: 미니홈피 메인. UI parity(스냅샷 일치)의 대상.
 *
 * <p>캐노니컬 데모 상태(고정값)로 결정적 HTML 을 만든다 (screens.py 포팅).
 */
public final class Screens {

    public static final String OWNER = "도토리";
    public static final int TODAY = 3;
    public static final int TOTAL = 1024;
    public static final String MOOD = "🌧️"; // 🌧️
    public static final String BGM = "첫눈";
    public static final List<String> MENU = List.of("홈", "프로필", "다이어리", "사진첩", "방명록");

    private Screens() {
    }

    private static String renderMinihompy() {
        StringBuilder menu = new StringBuilder();
        for (String m : MENU) {
            menu.append("<a>").append(m).append("</a>");
        }
        return "<main class=\"minihompy\"><aside class=\"miniroom\"><div class=\"avatar\">미니미</div>"
                + "<p class=\"mood\">오늘의 기분: " + MOOD + "</p></aside>"
                + "<section class=\"home\"><h1>" + OWNER + "님의 미니홈피</h1>"
                + "<p class=\"today\">TODAY <b>" + TODAY + "</b> · TOTAL <b>" + TOTAL + "</b></p>"
                + "<nav class=\"menu\">" + menu + "</nav>"
                + "<p class=\"bgm\">♪ BGM: " + BGM + "</p></section></main>";
    }

    public static String render(String screen) {
        if ("minihompy".equals(screen)) {
            return renderMinihompy();
        }
        throw new IllegalArgumentException(screen);
    }
}
