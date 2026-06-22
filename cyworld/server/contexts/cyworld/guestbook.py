# -*- coding: utf-8 -*-
"""방명록: 기존 흐름(회귀 검증 대상 shared surface). 최신순 + 비밀글 가시성.

비밀글은 미니홈피 주인과 작성자만 볼 수 있다.
"""


class GuestbookService:
    def __init__(self):
        self._entries = {}  # owner -> list[(seq, author, msg, secret)]
        self._seq = 0

    def write(self, owner, author, msg, *, secret=False):
        self._seq += 1
        self._entries.setdefault(owner, []).append((self._seq, author, msg, secret))
        return {"status": "written"}

    def entries(self, owner, viewer=None):
        """최신순. 비밀글은 주인/작성자에게만 보인다."""
        rows = sorted(self._entries.get(owner, []), reverse=True)
        out = []
        for _, author, msg, secret in rows:
            if secret and viewer not in (owner, author):
                continue
            out.append({"author": author, "msg": msg, "secret": secret})
        return out
