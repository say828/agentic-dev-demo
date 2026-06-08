# -*- coding: utf-8 -*-
"""일촌: 신청→수락 양방향 성립, 수락 전 비성립, 중복 신청 멱등."""
import pytest


def test_not_ilchon_until_accept(ilchon):
    ilchon.request("a", "b")
    assert ilchon.are_ilchon("a", "b") is False  # 수락 전


def test_request_then_accept_is_mutual(ilchon):
    ilchon.request("a", "b")
    assert ilchon.accept("a", "b")["status"] == "accepted"
    assert ilchon.are_ilchon("a", "b") is True
    assert ilchon.are_ilchon("b", "a") is True   # 양방향
    assert ilchon.ilchons("a") == ["b"]
    assert ilchon.ilchons("b") == ["a"]


def test_request_idempotent(ilchon):
    r1 = ilchon.request("a", "b")
    r2 = ilchon.request("a", "b")
    assert r1["replay"] is False and r2["replay"] is True


def test_accept_without_request(ilchon):
    assert ilchon.accept("a", "b")["status"] == "no_request"


def test_self_ilchon_rejected(ilchon):
    with pytest.raises(ValueError):
        ilchon.request("a", "a")
