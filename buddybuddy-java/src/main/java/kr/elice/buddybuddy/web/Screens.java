package kr.elice.buddybuddy.web;

/**
 * 화면 에셋: 버디버디 마스코트 SVG + 윈도우 크롬(타이틀바) 조각.
 * Python server/contexts/buddybuddy/screens.py 포트.
 */
public final class Screens {

    private Screens() {
    }

    /** 버디버디 병아리 마스코트(노란 새). 인라인 SVG. */
    public static final String MASCOT_SVG =
            "<svg class=\"mascot\" viewBox=\"0 0 64 64\" width=\"40\" height=\"40\" "
            + "xmlns=\"http://www.w3.org/2000/svg\" aria-hidden=\"true\">"
            + "<ellipse cx=\"32\" cy=\"38\" rx=\"22\" ry=\"20\" fill=\"#ffd83d\"/>"
            + "<ellipse cx=\"32\" cy=\"20\" rx=\"16\" ry=\"15\" fill=\"#ffe14d\"/>"
            + "<circle cx=\"26\" cy=\"18\" r=\"2.4\" fill=\"#3a2a00\"/>"
            + "<circle cx=\"38\" cy=\"18\" r=\"2.4\" fill=\"#3a2a00\"/>"
            + "<path d=\"M28 23 L36 23 L32 28 Z\" fill=\"#ff8a00\"/>"
            + "<path d=\"M14 40 q-8 2 -10 8 q9 -1 12 -4 Z\" fill=\"#ffd83d\"/>"
            + "<path d=\"M50 40 q8 2 10 8 q-9 -1 -12 -4 Z\" fill=\"#ffd83d\"/>"
            + "<ellipse cx=\"23\" cy=\"24\" rx=\"3\" ry=\"2\" fill=\"#ffb3c1\" opacity=\".7\"/>"
            + "<ellipse cx=\"41\" cy=\"24\" rx=\"3\" ry=\"2\" fill=\"#ffb3c1\" opacity=\".7\"/>"
            + "</svg>";

    /**
     * 메신저 윈도우 크롬(타이틀바 + 닫기/최소화 버튼). title 을 넣어 한 창을 감싼다.
     * 본문은 {@code <div class="win-body">...</div>} 안에 채운다.
     */
    public static String windowChrome(String title, String bodyHtml) {
        return "<div class=\"win\">"
                + "<div class=\"win-title\">" + MASCOT_SVG
                + "<span class=\"win-name\">" + title + "</span>"
                + "<span class=\"win-btns\"><i>_</i><i>□</i><i>×</i></span>"
                + "</div>"
                + "<div class=\"win-body\">" + bodyHtml + "</div>"
                + "</div>";
    }
}
