# -*- coding: utf-8 -*-
"""접속 상태: 로그인하면 온라인, 로그아웃하면 오프라인.

인메모리 집합 하나로 상태를 들고, 메시지 기록과 독립적으로 동작한다(AC-1).
"""


class PresenceService:
    def __init__(self):
        self._online = set()

    def login(self, user):
        self._online.add(user)
        return {"user": user, "status": "online"}

    def logout(self, user):
        self._online.discard(user)
        return {"user": user, "status": "offline"}

    def is_online(self, user):
        return user in self._online

    def status(self, user):
        return "online" if user in self._online else "offline"

    def online(self):
        return sorted(self._online)
