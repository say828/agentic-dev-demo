# -*- coding: utf-8 -*-
"""투데이: 미니홈피 방문 집계. 같은 방문자·같은 날은 TODAY 1회만(멱등). TOTAL은 누적.

멱등 키 = (owner, visitor, day) → OTP 멱등과 같은 결.
"""
from server.shared.idem import IdempotencyStore, idempotency_key


class TodayService:
    def __init__(self, idem=None):
        self.idem = idem or IdempotencyStore()
        self._today = {}  # (owner, day) -> set(visitor)
        self._total = {}  # owner -> int

    def visit(self, owner, visitor, day):
        key = idempotency_key({"owner": owner, "visitor": visitor, "day": day})

        def _do():
            self._today.setdefault((owner, day), set()).add(visitor)
            self._total[owner] = self._total.get(owner, 0) + 1
            return {"status": "counted", "owner": owner, "day": day}

        res, replay = self.idem.issue_once(key, _do)
        return {**res, "replay": replay}

    def today_count(self, owner, day):
        return len(self._today.get((owner, day), set()))

    def total_count(self, owner):
        return self._total.get(owner, 0)
