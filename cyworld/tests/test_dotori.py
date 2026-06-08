# -*- coding: utf-8 -*-
"""도토리: 충전·잔액·구매 차감·잔액부족 거부·이중결제 멱등."""
import pytest

from server.contexts.cyworld.dotori import InsufficientDotori


def test_charge_and_balance(dotori):
    assert dotori.charge("a", 100) == 100
    assert dotori.charge("a", 50) == 150
    assert dotori.balance("a") == 150


def test_charge_rejects_nonpositive(dotori):
    with pytest.raises(ValueError):
        dotori.charge("a", 0)


def test_purchase_deducts(dotori):
    dotori.charge("a", 200)
    r = dotori.purchase("a", "미니룸스킨", 120, order_id="o1")
    assert r.status == "purchased" and r.balance == 80
    assert dotori.balance("a") == 80


def test_purchase_insufficient(dotori):
    dotori.charge("a", 50)
    with pytest.raises(InsufficientDotori):
        dotori.purchase("a", "BGM", 100, order_id="o1")
    assert dotori.balance("a") == 50  # 잔액 보존


def test_purchase_idempotent(dotori):
    dotori.charge("a", 200)
    r1 = dotori.purchase("a", "폰트", 70, order_id="ord-1")
    r2 = dotori.purchase("a", "폰트", 70, order_id="ord-1")  # 같은 주문 재요청
    assert r1.replay is False and r2.replay is True
    assert dotori.balance("a") == 130  # 한 번만 차감
