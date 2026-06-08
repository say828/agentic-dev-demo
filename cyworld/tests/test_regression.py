# -*- coding: utf-8 -*-
"""회귀: 기존 방명록(shared surface)이 도토리·일촌 추가로 깨지지 않는다."""


def test_guestbook_recency_and_secret(guestbook):
    guestbook.write("owner", "친구A", "안녕!")
    guestbook.write("owner", "친구B", "또 놀러옴")
    guestbook.write("owner", "친구C", "비밀 메시지", secret=True)

    # 외부 방문자: 최신순, 비밀글 숨김
    seen = guestbook.entries("owner", viewer="구경꾼")
    assert [e["author"] for e in seen] == ["친구B", "친구A"]

    # 주인: 비밀글까지 최신순 전체
    mine = guestbook.entries("owner", viewer="owner")
    assert [e["author"] for e in mine] == ["친구C", "친구B", "친구A"]
