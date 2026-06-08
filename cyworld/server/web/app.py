# -*- coding: utf-8 -*-
"""미니홈피 로컬 웹 프론트 (의존성 0, 파이썬 표준 http.server).

기존 백엔드 서비스(dotori/ilchon/today/guestbook)를 JSON API로 노출하고,
단일 HTML 페이지(미니홈피)에서 호출한다. 이 환경은 브라우저 비가용이라
서버 로직은 curl 로 검증하고, 시각 확인은 사용자가 localhost 에서 한다.

실행:  python3 -m server.web.app   # → http://localhost:8000
"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from server.contexts.cyworld.dotori import DotoriService, InsufficientDotori
from server.contexts.cyworld.guestbook import GuestbookService
from server.contexts.cyworld.ilchon import IlchonService
from server.contexts.cyworld.today import TodayService

OWNER = "도토리"
DAY = "2026-06-08"

# 데모 단일 인스턴스(인메모리). 초기 시드로 화면이 비지 않게 한다.
dotori = DotoriService()
ilchon = IlchonService()
today = TodayService()
guestbook = GuestbookService()


def _seed():
    dotori.charge(OWNER, 500)
    guestbook.write(OWNER, "친구A", "미니홈피 개설 축하해~")
    guestbook.write(OWNER, "친구B", "일촌 신청했어!")
    today.visit(OWNER, "친구A", DAY)
    today.visit(OWNER, "친구B", DAY)
    ilchon.request("친구B", OWNER)


def state(owner=OWNER, viewer=OWNER, day=DAY):
    return {
        "owner": owner,
        "today": today.today_count(owner, day),
        "total": today.total_count(owner),
        "balance": dotori.balance(owner),
        "ilchons": ilchon.ilchons(owner),
        "guestbook": guestbook.entries(owner, viewer=viewer),
    }


PAGE = """<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>도토리님의 미니홈피</title>
<style>
  body{margin:0;background:#cfe3f7;font-family:'맑은 고딕',sans-serif;color:#234}
  .wrap{max-width:820px;margin:24px auto;background:#fff;border:1px solid #9bbad6;
        border-radius:6px;display:flex;overflow:hidden;box-shadow:0 2px 8px #0002}
  .miniroom{width:240px;background:#eaf3fb;border-right:1px solid #cdddee;padding:18px;text-align:center}
  .avatar{width:120px;height:140px;margin:8px auto;background:#dff;border:1px solid #9cf;
          border-radius:8px;line-height:140px;color:#69c}
  .mood{font-size:13px;color:#577}
  .home{flex:1;padding:18px 22px}
  h1{font-size:18px;margin:0 0 6px;color:#15406b}
  .today{font-size:13px;color:#477;margin:0 0 12px}
  .today b{color:#d35}
  nav.menu a{display:inline-block;margin-right:8px;padding:3px 10px;background:#15406b;color:#fff;
             border-radius:12px;font-size:12px;text-decoration:none}
  .bgm{color:#787;font-size:12px}
  section.card{border:1px solid #d6e3f0;border-radius:6px;padding:12px;margin:14px 0;background:#fafdff}
  section.card h2{font-size:14px;margin:0 0 8px;color:#15406b}
  input,button{font-size:13px;padding:4px 6px;margin:2px}
  button{background:#15406b;color:#fff;border:0;border-radius:4px;cursor:pointer}
  ul{margin:6px 0;padding-left:18px;font-size:13px}
  .msg{font-size:12px;color:#c33;min-height:16px}
  .secret{color:#a6a}
</style></head>
<body><div class="wrap">
  <aside class="miniroom">
    <div class="avatar">미니미</div>
    <p class="mood">오늘의 기분: 🌧️</p>
    <p class="bgm">♪ BGM: 첫눈</p>
  </aside>
  <section class="home">
    <h1 id="title"></h1>
    <p class="today">TODAY <b id="today">-</b> · TOTAL <b id="total">-</b> · 🌰 도토리 <b id="bal">-</b></p>
    <nav class="menu"><a href="#">홈</a><a href="#">프로필</a><a href="#">다이어리</a>
      <a href="#">사진첩</a><a href="#">방명록</a></nav>

    <section class="card"><h2>🌰 도토리</h2>
      <input id="amt" type="number" value="100" style="width:70px"><button onclick="charge()">충전</button>
      <input id="item" value="미니룸스킨" style="width:90px">
      <input id="price" type="number" value="120" style="width:60px"><button onclick="buy()">구매</button>
      <div class="msg" id="dmsg"></div></section>

    <section class="card"><h2>👫 일촌</h2>
      <span id="ilchons"></span><br>
      <input id="who" value="친구C" style="width:80px"><button onclick="ilreq()">신청</button>
      <button onclick="ilacc()">친구B 수락</button>
      <div class="msg" id="imsg"></div></section>

    <section class="card"><h2>📖 방명록</h2>
      <input id="gauthor" value="방문자" style="width:70px">
      <input id="gmsg" value="다녀가요~" style="width:140px">
      <label><input id="gsecret" type="checkbox">비밀</label>
      <button onclick="sign()">남기기</button>
      <ul id="gb"></ul></section>
  </section>
</div>
<script>
async function api(path, body){
  const r = await fetch(path, {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify(body)});
  return r.json();
}
async function refresh(){
  const s = await (await fetch('/api/state')).json();
  title.textContent = s.owner + '님의 미니홈피';
  today.textContent = s.today; total.textContent = s.total; bal.textContent = s.balance;
  ilchons.textContent = '일촌(' + s.ilchons.length + '): ' + (s.ilchons.join(', ') || '아직 없음');
  gb.innerHTML = s.guestbook.map(e =>
    '<li'+(e.secret?' class="secret"':'')+'><b>'+e.author+'</b>: '+e.msg+(e.secret?' 🔒':'')+'</li>').join('');
}
async function charge(){ await api('/api/charge',{user:'도토리',amount:+amt.value}); dmsg.textContent=''; refresh(); }
async function buy(){ const r=await api('/api/purchase',{user:'도토리',item:item.value,price:+price.value});
  dmsg.textContent = r.error ? ('구매 실패: '+r.error) : ('구매 완료 · 잔액 '+r.balance); refresh(); }
async function ilreq(){ await api('/api/ilchon_request',{frm:'도토리',to:who.value}); imsg.textContent='신청 보냄: '+who.value; refresh(); }
async function ilacc(){ const r=await api('/api/ilchon_accept',{frm:'친구B',to:'도토리'});
  imsg.textContent = r.status==='accepted' ? '친구B 와 일촌!' : '수락할 신청 없음'; refresh(); }
async function sign(){ await api('/api/guestbook',{owner:'도토리',author:gauthor.value,msg:gmsg.value,secret:gsecret.checked}); refresh(); }
refresh();
</script>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode("utf-8")
        if ctype.startswith("text"):
            data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _body(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n) or b"{}") if n else {}

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/":
            return self._send(200, PAGE, "text/html")
        if u.path == "/api/state":
            q = parse_qs(u.query)
            return self._send(200, state(
                q.get("owner", [OWNER])[0], q.get("viewer", [OWNER])[0], q.get("day", [DAY])[0]))
        return self._send(404, {"error": "not_found"})

    def do_POST(self):
        u = urlparse(self.path)
        try:
            b = self._body()
            if u.path == "/api/charge":
                return self._send(200, {"balance": dotori.charge(b["user"], int(b["amount"]))})
            if u.path == "/api/purchase":
                r = dotori.purchase(b["user"], b["item"], int(b["price"]), order_id=b.get("order_id"))
                return self._send(200, {"status": r.status, "balance": r.balance, "replay": r.replay})
            if u.path == "/api/ilchon_request":
                return self._send(200, ilchon.request(b["frm"], b["to"]))
            if u.path == "/api/ilchon_accept":
                return self._send(200, ilchon.accept(b["frm"], b["to"]))
            if u.path == "/api/visit":
                return self._send(200, today.visit(b["owner"], b["visitor"], b.get("day", DAY)))
            if u.path == "/api/guestbook":
                return self._send(200, guestbook.write(
                    b["owner"], b["author"], b["msg"], secret=bool(b.get("secret"))))
        except InsufficientDotori as e:
            return self._send(200, {"error": str(e)})
        except (KeyError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as e:
            return self._send(400, {"error": f"bad_request: {e}"})
        return self._send(404, {"error": "not_found"})

    def log_message(self, *a):  # 조용히
        pass


def main(port=8000):
    _seed()
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"미니홈피: http://localhost:{port}  (Ctrl+C 종료)")
    srv.serve_forever()


if __name__ == "__main__":
    main()
