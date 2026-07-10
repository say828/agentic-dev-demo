# -*- coding: utf-8 -*-
"""AC-2: 버디 추가·목록·멱등·자기추가 거부."""
import pytest


def test_add_appears_in_list(buddy):
    buddy.add("현주", "민수")
    assert buddy.buddies("현주") == ["민수"]
    assert buddy.has("현주", "민수") is True


def test_add_is_idempotent(buddy):
    r1 = buddy.add("현주", "민수")
    r2 = buddy.add("현주", "민수")
    assert r1["replay"] is False and r2["replay"] is True
    assert buddy.buddies("현주") == ["민수"]   # 중복 없이 한 번만


def test_add_preserves_order(buddy):
    buddy.add("현주", "민수")
    buddy.add("현주", "철수")
    assert buddy.buddies("현주") == ["민수", "철수"]


def test_self_add_rejected(buddy):
    with pytest.raises(ValueError):
        buddy.add("현주", "현주")


def test_buddy_is_directional(buddy):
    buddy.add("현주", "민수")
    assert buddy.buddies("민수") == []   # 추가는 내 목록에만
