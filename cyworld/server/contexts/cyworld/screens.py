# -*- coding: utf-8 -*-
"""화면 렌더: 미니홈피 메인. UI parity(스냅샷 일치)의 대상.

실 강의 데모는 Playwright exactness gate로 픽셀을 비교하지만, 이 환경
(브라우저·compose 비가용)에서는 결정적 HTML 스냅샷 parity로 대체한다.
캐노니컬 데모 상태(고정값)로 결정적 HTML을 만든다.
"""

OWNER = "도토리"
TODAY = 3
TOTAL = 1024
MOOD = "🌧️"
BGM = "첫눈"
MENU = ["홈", "프로필", "다이어리", "사진첩", "방명록"]


def _render_minihompy():
    menu = "".join(f'<a>{m}</a>' for m in MENU)
    return (
        '<main class="minihompy">'
        '<aside class="miniroom">'
        '<div class="avatar">미니미</div>'
        f'<p class="mood">오늘의 기분: {MOOD}</p>'
        '</aside>'
        '<section class="home">'
        f'<h1>{OWNER}님의 미니홈피</h1>'
        f'<p class="today">TODAY <b>{TODAY}</b> · TOTAL <b>{TOTAL}</b></p>'
        f'<nav class="menu">{menu}</nav>'
        f'<p class="bgm">♪ BGM: {BGM}</p>'
        '</section>'
        '</main>'
    )


SCREENS = {"minihompy": _render_minihompy()}


def render(screen):
    return SCREENS[screen]
