# -*- coding: utf-8 -*-
"""멱등 처리: idempotency_key로 이중 결제·중복 신청을 차단한다.

auth 데모의 shared/idem.py와 동일 패턴(컨텍스트 간 재사용).
성공 결과만 캐시한다 — fn()이 예외를 던지면 캐시하지 않으므로 재시도가 가능하다.
"""
import hashlib
import json


def idempotency_key(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class IdempotencyStore:
    def __init__(self):
        self._seen = {}

    def issue_once(self, key, fn):
        if key in self._seen:
            return self._seen[key], True
        result = fn()  # 예외 시 아래 캐시에 도달하지 않음 = 실패는 멱등 캐시 안 함
        self._seen[key] = result
        return result, False
