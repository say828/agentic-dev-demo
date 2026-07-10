# -*- coding: utf-8 -*-
"""메시지: A→B 송신을 (A,B) 대화에 순번대로 기록하고 양쪽이 같은 대화를 본다.

설계 포인트
- 대화는 방향 없는 쌍 frozenset({a,b})로 식별 → A→B 와 B→A 가 같은 대화(AC-3·6).
- 전송 멱등: client_msg_id 우선, 없으면 (frm,to,text) 내용 해시 폴백(AC-4).
  성공만 캐시하는 idem 스토어라 빈 메시지 등 거부는 재시도 가능.
- 안읽음: "받는 사람 앞으로 온, 아직 안 읽은 메시지" 기준 집계 → 읽으면 0(AC-5).
"""
from dataclasses import dataclass

from server.shared.idem import IdempotencyStore, idempotency_key


@dataclass
class Message:
    seq: int      # 전역 단조 증가 순번(대화 내 정렬 안정성)
    frm: str
    to: str
    text: str
    read: bool = False


class MessageService:
    def __init__(self, idem=None):
        self.idem = idem or IdempotencyStore()
        self._threads = {}  # frozenset({a,b}) -> [Message, ...]
        self._seq = 0

    @staticmethod
    def _pair(a, b):
        return frozenset((a, b))

    def send(self, frm, to, text, *, client_msg_id=None):
        if frm == to:
            raise ValueError("자기 자신에게는 보낼 수 없다")
        text = (text or "").strip()
        if not text:
            raise ValueError("빈 메시지는 보낼 수 없다")
        key = client_msg_id or idempotency_key({"frm": frm, "to": to, "text": text})

        def _do():
            self._seq += 1
            m = Message(seq=self._seq, frm=frm, to=to, text=text)
            self._threads.setdefault(self._pair(frm, to), []).append(m)
            return m

        res, replay = self.idem.issue_once(key, _do)
        return {"seq": res.seq, "frm": res.frm, "to": res.to,
                "text": res.text, "replay": replay}

    def thread(self, a, b):
        """(a,b) 대화의 메시지를 순번대로. 방향 무관하게 같은 대화를 돌려준다."""
        msgs = sorted(self._threads.get(self._pair(a, b), []), key=lambda m: m.seq)
        return [{"seq": m.seq, "frm": m.frm, "to": m.to, "text": m.text, "read": m.read}
                for m in msgs]

    def mark_read(self, reader, other):
        """reader 가 (reader,other) 대화를 읽음 — reader 앞으로 온 안읽음만 읽음 처리."""
        n = 0
        for m in self._threads.get(self._pair(reader, other), []):
            if m.to == reader and not m.read:
                m.read = True
                n += 1
        return {"read": n}

    def unread(self, user, other):
        """(user,other) 대화에서 user 가 아직 안 읽은 수신 메시지 수."""
        return sum(1 for m in self._threads.get(self._pair(user, other), [])
                   if m.to == user and not m.read)

    def partners(self, user):
        """user 가 한 번이라도 메시지를 주고받은 상대 목록(정렬).

        버디로 명시 추가하지 않았어도 대화가 있으면 상대를 노출 → 두 프론트가
        서로를 자동으로 대화 목록에 띄운다(AC-7).
        """
        out = set()
        for pair, msgs in self._threads.items():
            if user in pair and msgs:
                out |= {u for u in pair if u != user}
        return sorted(out)
