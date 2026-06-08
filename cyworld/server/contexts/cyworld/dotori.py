# -*- coding: utf-8 -*-
"""도토리(가상화폐): 충전·잔액·아이템 구매(차감) + 잔액부족 거부 + 이중결제 멱등.

순수 산술 + 멱등 → 결정적으로 검증된다(외부 PG·실시간 비의존).
"""
from dataclasses import dataclass, replace

from server.shared.idem import IdempotencyStore, idempotency_key


class InsufficientDotori(Exception):
    """잔액 부족: 구매 거부. 멱등 캐시에 남기지 않는다."""


@dataclass
class PurchaseResult:
    status: str  # purchased
    item: str = ""
    price: int = 0
    balance: int = 0
    order_id: str = ""
    replay: bool = False


class DotoriService:
    def __init__(self, idem=None):
        self.idem = idem or IdempotencyStore()
        self._balance = {}
        self._owned = {}  # user -> set(item) 구매로 지급된 보유 아이템

    def charge(self, user, amount):
        if amount <= 0:
            raise ValueError("충전액은 양수여야 한다")
        self._balance[user] = self._balance.get(user, 0) + amount
        return self._balance[user]

    def balance(self, user):
        return self._balance.get(user, 0)

    def purchase(self, user, item, price, *, order_id=None):
        key = order_id or idempotency_key({"user": user, "item": item})

        def _do():
            bal = self._balance.get(user, 0)
            if bal < price:
                raise InsufficientDotori(
                    f"잔액 부족: balance={bal} < price={price}")
            self._balance[user] = bal - price
            self._owned.setdefault(user, set()).add(item)  # 구매 = 보유 지급
            return PurchaseResult("purchased", item=item, price=price,
                                  balance=self._balance[user], order_id=key)

        res, replay = self.idem.issue_once(key, _do)
        return replace(res, replay=replay)

    def owned(self, user):
        """보유 아이템 목록(정렬). 멱등 재구매는 중복 지급되지 않는다."""
        return sorted(self._owned.get(user, set()))
