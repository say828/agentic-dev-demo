# -*- coding: utf-8 -*-
"""AC-3·4·5·6: 송수신 기록 / 양쪽 동일 대화 / 전송 멱등 / 읽음 / 대화 격리."""
import pytest


def test_send_records_in_thread(message):
    message.send("현주", "민수", "안녕")
    th = message.thread("현주", "민수")
    assert len(th) == 1
    m = th[0]
    assert m["frm"] == "현주" and m["to"] == "민수" and m["text"] == "안녕"
    assert m["seq"] == 1


def test_both_sides_see_same_thread(message):
    message.send("현주", "민수", "ㅎㅇ")
    message.send("민수", "현주", "ㅇㅇ ㅎㅇ")
    # 방향과 무관하게 같은 대화를 본다(AC-3)
    assert message.thread("현주", "민수") == message.thread("민수", "현주")
    texts = [m["text"] for m in message.thread("현주", "민수")]
    assert texts == ["ㅎㅇ", "ㅇㅇ ㅎㅇ"]   # 순번 보존


def test_send_idempotent(message):
    r1 = message.send("현주", "민수", "재시도?", client_msg_id="c1")
    r2 = message.send("현주", "민수", "재시도?", client_msg_id="c1")
    assert r1["replay"] is False and r2["replay"] is True
    assert len(message.thread("현주", "민수")) == 1   # 한 번만 기록(AC-4)


def test_same_text_distinct_ids_both_recorded(message):
    message.send("현주", "민수", "ㅋㅋ", client_msg_id="a")
    message.send("현주", "민수", "ㅋㅋ", client_msg_id="b")
    assert len(message.thread("현주", "민수")) == 2   # 의도된 중복은 통과


def test_mark_read_clears_unread(message):
    message.send("현주", "민수", "읽어줘")
    assert message.unread("민수", "현주") == 1     # 민수 앞으로 온 안읽음
    assert message.unread("현주", "민수") == 0     # 현주가 보낸 건 현주의 안읽음 아님
    message.mark_read("민수", "현주")
    assert message.unread("민수", "현주") == 0     # 읽으면 0(AC-5)


def test_threads_are_isolated(message):
    message.send("현주", "민수", "민수에게")
    message.send("현주", "철수", "철수에게")
    assert [m["text"] for m in message.thread("현주", "민수")] == ["민수에게"]
    assert [m["text"] for m in message.thread("현주", "철수")] == ["철수에게"]  # 안 섞임(AC-6)


def test_partners_lists_conversation_others(message):
    message.send("현주", "민수", "hi")
    message.send("지우", "현주", "안녕 현주야")
    # 현주는 민수·지우와 대화 이력이 있다(버디 추가 없이도 노출 → 두 프론트 자동 인식)
    assert message.partners("현주") == ["민수", "지우"]
    assert message.partners("민수") == ["현주"]
    assert message.partners("아무도") == []


def test_empty_message_rejected(message):
    with pytest.raises(ValueError):
        message.send("현주", "민수", "   ")


def test_self_message_rejected(message):
    with pytest.raises(ValueError):
        message.send("현주", "현주", "혼잣말")
