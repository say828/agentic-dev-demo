# -*- coding: utf-8 -*-
"""AC-1: 로그인→온라인, 로그아웃→오프라인."""


def test_login_makes_online(presence):
    presence.login("현주")
    assert presence.is_online("현주") is True
    assert presence.status("현주") == "online"


def test_logout_makes_offline(presence):
    presence.login("현주")
    presence.logout("현주")
    assert presence.is_online("현주") is False
    assert presence.status("현주") == "offline"


def test_unknown_user_is_offline(presence):
    assert presence.status("아무개") == "offline"


def test_online_list_sorted(presence):
    presence.login("민수")
    presence.login("현주")
    assert presence.online() == ["민수", "현주"]
