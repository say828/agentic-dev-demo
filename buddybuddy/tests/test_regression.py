# -*- coding: utf-8 -*-
"""회귀: 버디 추가가 끼어들어도 메시지 송수신·읽음 흐름이 깨지지 않는다.

presence/buddy/message 가 같은 시나리오에서 서로 간섭 없이 동작하는지 본다.
"""
from server.contexts.buddybuddy.buddy import BuddyService
from server.contexts.buddybuddy.message import MessageService
from server.contexts.buddybuddy.presence import PresenceService


def test_end_to_end_two_users():
    presence, buddy, message = PresenceService(), BuddyService(), MessageService()

    # 1) 둘 다 접속
    presence.login("현주")
    presence.login("민수")
    assert presence.online() == ["민수", "현주"]

    # 2) 서로 버디 추가(중복 추가 섞어도 멱등)
    buddy.add("현주", "민수")
    buddy.add("현주", "민수")
    buddy.add("민수", "현주")
    assert buddy.buddies("현주") == ["민수"]
    assert buddy.buddies("민수") == ["현주"]

    # 3) 주고받기
    message.send("현주", "민수", "민수야 뭐해?")
    message.send("민수", "현주", "겜함 ㅋㅋ 너는?")
    message.send("현주", "민수", "나도 ㄱㄱ")
    th = message.thread("현주", "민수")
    assert [m["text"] for m in th] == ["민수야 뭐해?", "겜함 ㅋㅋ 너는?", "나도 ㄱㄱ"]

    # 4) 안읽음 → 읽음
    assert message.unread("민수", "현주") == 2   # 현주가 보낸 2건
    message.mark_read("민수", "현주")
    assert message.unread("민수", "현주") == 0

    # 5) 로그아웃해도 대화 기록은 보존
    presence.logout("민수")
    assert presence.status("민수") == "offline"
    assert len(message.thread("현주", "민수")) == 3
