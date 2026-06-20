# -*- coding: utf-8 -*-
"""버디버디 화면 조각: 2000년대 메신저 창(chrome) + 마스코트 SVG.

웹 프론트(app.py)가 재사용한다. 화면 텍스트/마크업을 도메인 밖 한 곳에 모아
AC-7(두 사용자가 주고받는 모습)의 시각 요소를 일관되게 그린다.
"""

# 버디버디 하면 떠오르는 동글동글한 캐릭터(가상 재현). 머리 위 하트 안테나.
MASCOT_SVG = (
    '<svg class="bud" width="34" height="34" viewBox="0 0 60 60" aria-hidden="true">'
    '<path d="M30 6 q-4 -5 -7 -1 q-2 3 7 9 q9 -6 7 -9 q-3 -4 -7 1 z" fill="#ff5d8f"/>'
    '<line x1="30" y1="14" x2="30" y2="20" stroke="#ffb400" stroke-width="2"/>'
    '<ellipse cx="30" cy="36" rx="20" ry="18" fill="#ffd200" stroke="#e6a900" stroke-width="2"/>'
    '<circle cx="23" cy="34" r="3" fill="#3a2a1a"/><circle cx="37" cy="34" r="3" fill="#3a2a1a"/>'
    '<circle cx="24" cy="33" r="1" fill="#fff"/><circle cx="38" cy="33" r="1" fill="#fff"/>'
    '<circle cx="20" cy="40" r="3.4" fill="#ff9db0" opacity="0.8"/>'
    '<circle cx="40" cy="40" r="3.4" fill="#ff9db0" opacity="0.8"/>'
    '<path d="M25 42 q5 5 10 0" stroke="#3a2a1a" stroke-width="2" fill="none" stroke-linecap="round"/>'
    '</svg>'
)


def window_chrome(title):
    """메신저 창 타이틀바 HTML. 닫기/최소화 버튼은 장식(데모)."""
    return (
        f'<div class="titlebar">{MASCOT_SVG}<span class="tt">{title}</span>'
        '<span class="winbtns"><i>_</i><i>□</i><i>×</i></span></div>'
    )
