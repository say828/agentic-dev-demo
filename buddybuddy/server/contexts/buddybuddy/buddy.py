# -*- coding: utf-8 -*-
"""버디(친구) 목록: 추가하면 목록에 들어가고, 중복 추가는 멱등(한 번만).

버디버디는 일촌처럼 상호 수락이 필수는 아니었다 — 내 목록에 상대를 담는 단방향 추가.
순서를 보존하기 위해 set 대신 순서 있는 list를 쓰되, 멱등은 idem 스토어로 보장한다.
"""
from server.shared.idem import IdempotencyStore, idempotency_key


class BuddyService:
    def __init__(self, idem=None):
        self.idem = idem or IdempotencyStore()
        self._buddies = {}  # owner -> [buddy, ...] (추가 순서 보존)

    def add(self, owner, buddy):
        if owner == buddy:
            raise ValueError("자기 자신은 버디로 추가할 수 없다")
        key = idempotency_key({"owner": owner, "buddy": buddy})

        def _do():
            lst = self._buddies.setdefault(owner, [])
            if buddy not in lst:
                lst.append(buddy)
            return {"status": "added", "owner": owner, "buddy": buddy}

        res, replay = self.idem.issue_once(key, _do)
        return {**res, "replay": replay}

    def buddies(self, owner):
        return list(self._buddies.get(owner, []))

    def has(self, owner, buddy):
        return buddy in self._buddies.get(owner, [])
