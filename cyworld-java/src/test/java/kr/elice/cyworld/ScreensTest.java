package kr.elice.cyworld;

import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

import kr.elice.cyworld.domain.Screens;

/** test_screen_parity.py 의 essentials 체크 포팅 (스냅샷 파일 비교는 제외). */
class ScreensTest {

    @Test
    void test_minihompy_screen_essentials() {
        String html = Screens.render("minihompy");
        assertTrue(html.contains("님의 미니홈피"));
        assertTrue(html.contains("TODAY"));
        assertTrue(html.contains("BGM"));
    }
}
