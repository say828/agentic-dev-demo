# -*- coding: utf-8 -*-
"""웹 프론트 API 검증(결정적): 서버를 임시 포트로 띄워 UTF-8 JSON으로 호출한다.

브라우저 비가용 환경의 프론트 검증 = HTTP 계약을 in-process 로 실제 호출해 확인.
"""
import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from server.web import app


@pytest.fixture
def base_url():
    # 모듈 싱글톤을 테스트마다 초기화(격리) 후 시드
    app.dotori = app.DotoriService()
    app.ilchon = app.IlchonService()
    app.today = app.TodayService()
    app.guestbook = app.GuestbookService()
    app._seed()
    srv = ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def _get(url):
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read())


def _post(url, payload):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")  # UTF-8 명시
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def test_page_served(base_url):
    with urllib.request.urlopen(base_url + "/") as r:
        html = r.read().decode("utf-8")
    assert "님의 미니홈피" in html
    assert "/api/state" in html  # JS가 상태 API를 부른다


def test_state_has_seed(base_url):
    s = _get(base_url + "/api/state")
    assert s["owner"] == "도토리"
    assert s["balance"] == 500          # 시드 충전
    assert s["today"] == 2              # 친구A·친구B 방문
    assert len(s["guestbook"]) == 2


def test_charge_then_purchase(base_url):
    assert _post(base_url + "/api/charge", {"user": "도토리", "amount": 100})["balance"] == 600
    r = _post(base_url + "/api/purchase",
              {"user": "도토리", "item": "미니룸스킨", "price": 120, "order_id": "w1"})
    assert r["status"] == "purchased" and r["balance"] == 480


def test_purchase_insufficient_returns_error(base_url):
    r = _post(base_url + "/api/purchase",
              {"user": "도토리", "item": "고가템", "price": 999999})
    assert "error" in r  # 잔액부족 → 에러 표면(서버는 살아있음)


def test_ilchon_accept_flow(base_url):
    # 시드: 친구B → 도토리 신청 상태. 수락하면 양방향.
    assert _post(base_url + "/api/ilchon_accept",
                 {"frm": "친구B", "to": "도토리"})["status"] == "accepted"
    assert "친구B" in _get(base_url + "/api/state")["ilchons"]


def test_guestbook_post(base_url):
    _post(base_url + "/api/guestbook",
          {"owner": "도토리", "author": "방문자", "msg": "다녀가요", "secret": False})
    authors = [e["author"] for e in _get(base_url + "/api/state")["guestbook"]]
    assert authors[0] == "방문자"  # 최신순 맨 앞
