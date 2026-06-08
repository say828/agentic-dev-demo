# -*- coding: utf-8 -*-
"""일촌: 신청 → 수락으로 양방향 성립. 수락 전엔 일촌 아님. 중복 신청 멱등.

방향 있는 신청(pending)과 방향 없는 일촌 관계(edges)를 분리해 상태 전이를 명확히 한다.
"""
from server.shared.idem import IdempotencyStore, idempotency_key


class IlchonService:
    def __init__(self, idem=None):
        self.idem = idem or IdempotencyStore()
        self._pending = set()  # (frm, to) 방향 있는 신청
        self._edges = set()    # frozenset({a, b}) 방향 없는 일촌

    def request(self, frm, to):
        if frm == to:
            raise ValueError("자기 자신과는 일촌을 맺을 수 없다")
        key = idempotency_key({"frm": frm, "to": to})

        def _do():
            self._pending.add((frm, to))
            return {"status": "requested", "frm": frm, "to": to}

        res, replay = self.idem.issue_once(key, _do)
        return {**res, "replay": replay}

    def accept(self, frm, to):
        """to 가 frm 의 신청을 수락한다."""
        if (frm, to) not in self._pending:
            return {"status": "no_request"}
        self._pending.discard((frm, to))
        self._edges.add(frozenset((frm, to)))
        return {"status": "accepted", "a": frm, "b": to}

    def are_ilchon(self, a, b):
        return frozenset((a, b)) in self._edges

    def ilchons(self, user):
        return sorted(other for e in self._edges if user in e
                      for other in e if other != user)
