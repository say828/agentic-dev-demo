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

# 방 꾸미기: 구매 아이템 → 미니룸 시각. 보유분 중 첫 매칭을 적용.
WALLPAPERS = {"벽지:하늘": "#bfe6ff", "벽지:노을": "#ffd9b0", "벽지:벚꽃": "#ffe3ee"}
BGMS = {"BGM:첫눈": "첫눈", "BGM:벚꽃엔딩": "벚꽃엔딩", "BGM:붉은노을": "붉은노을"}
DEFAULT_WALL = "#fdeede"
DEFAULT_BGM = "첫눈"


def room_of(owner):
    owned = dotori.owned(owner)
    wall = next((WALLPAPERS[i] for i in owned if i in WALLPAPERS), DEFAULT_WALL)
    bgm = next((BGMS[i] for i in owned if i in BGMS), DEFAULT_BGM)
    return {"wallpaper": wall, "bgm": bgm, "owned": owned}

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
        "room": room_of(owner),
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
  .room{width:200px;height:190px;margin:8px auto;border-radius:10px;overflow:hidden;
        box-shadow:inset 0 0 0 3px #fff,0 1px 5px #0002;border:1px solid #c9a}
  .room svg{display:block}
  .mini{animation:bob 2.6s ease-in-out infinite;transform-origin:center}
  @keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}
  .mininame{font-size:12px;color:#88600f;font-weight:bold;margin:4px 0 6px}
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
    <div class="room">
      <svg width="200" height="190" viewBox="0 0 200 190" aria-label="도토리네 미니룸">
        <!-- 벽지 / 바닥 (벽지는 구매 아이템으로 바뀜: id=wall) -->
        <rect id="wall" x="0" y="0" width="200" height="124" fill="#fdeede"/>
        <rect x="0" y="124" width="200" height="66" fill="#e6c590"/>
        <line x1="0" y1="124" x2="200" y2="124" stroke="#d3ad73" stroke-width="2"/>
        <line x1="0" y1="150" x2="200" y2="150" stroke="#d9b67e" stroke-width="1.4"/>
        <line x1="0" y1="173" x2="200" y2="173" stroke="#d9b67e" stroke-width="1.4"/>
        <!-- 창문 -->
        <rect x="24" y="18" width="58" height="48" rx="4" fill="#bfe6ff" stroke="#fff" stroke-width="4"/>
        <line x1="53" y1="18" x2="53" y2="66" stroke="#fff" stroke-width="3"/>
        <line x1="24" y1="42" x2="82" y2="42" stroke="#fff" stroke-width="3"/>
        <circle cx="42" cy="32" r="6" fill="#fff" opacity="0.9"/>
        <circle cx="50" cy="32" r="5" fill="#fff" opacity="0.9"/>
        <!-- 벽시계 -->
        <circle cx="110" cy="32" r="11" fill="#fff" stroke="#cbb" stroke-width="2"/>
        <line x1="110" y1="32" x2="110" y2="25" stroke="#766" stroke-width="2"/>
        <line x1="110" y1="32" x2="115" y2="34" stroke="#766" stroke-width="2"/>
        <!-- 하트 액자 -->
        <rect x="134" y="22" width="34" height="30" rx="3" fill="#fff" stroke="#caa"/>
        <path d="M151 31 q-5 -6 -9 0 q-3 5 9 12 q12 -7 9 -12 q-4 -6 -9 0 z" fill="#f48aa0"/>
        <!-- 러그 -->
        <ellipse cx="100" cy="160" rx="64" ry="18" fill="#f7c9d6"/>
        <ellipse cx="100" cy="160" rx="50" ry="13" fill="#fcdfe8"/>
        <!-- 소파 -->
        <rect x="6" y="118" width="46" height="28" rx="9" fill="#9fc4e8"/>
        <rect x="6" y="110" width="46" height="16" rx="8" fill="#b6d4f0"/>
        <!-- 화분 -->
        <rect x="168" y="126" width="22" height="22" rx="3" fill="#c98a5a"/>
        <path d="M179 126 q-12 -20 -2 -32 q6 12 2 32 z" fill="#5bb56a"/>
        <path d="M179 126 q12 -18 4 -30 q-2 14 -4 30 z" fill="#6cc97b"/>
        <path d="M179 126 q-2 -24 0 -32 q4 16 0 32 z" fill="#52a860"/>
        <!-- 일촌 미니미(수락 시 JS가 채움) -->
        <g id="friends"></g>
        <!-- 미니미 발 그림자 -->
        <ellipse cx="100" cy="164" rx="24" ry="5.5" fill="#000" opacity="0.10"/>
        <!-- 말풍선 -->
        <g>
          <rect x="104" y="60" width="78" height="26" rx="13" fill="#fff" stroke="#d9c4a0"/>
          <path d="M120 86 l-7 11 l15 -7 z" fill="#fff" stroke="#d9c4a0"/>
          <path d="M120 86 l-7 11 l15 -7" fill="#fff" stroke="#fff"/>
          <text x="143" y="77" font-size="12" text-anchor="middle" fill="#86631a">방가방가~ 🌰</text>
        </g>
        <!-- 미니미(도토리) -->
        <g transform="translate(56,62) scale(0.78)"><g class="mini">
          <rect x="50" y="14" width="10" height="16" rx="5" fill="#7a5230"/>
          <path d="M22 56 Q55 18 88 56 Q55 70 22 56 Z" fill="#9c6b3f"/>
          <path d="M22 56 Q55 70 88 56 Q72 64 55 64 Q38 64 22 56 Z" fill="#84592f"/>
          <ellipse cx="55" cy="86" rx="34" ry="36" fill="#edcb95"/>
          <ellipse cx="55" cy="86" rx="34" ry="36" fill="none" stroke="#d8b277" stroke-width="2"/>
          <circle cx="43" cy="84" r="4.6" fill="#3a2a1a"/>
          <circle cx="67" cy="84" r="4.6" fill="#3a2a1a"/>
          <circle cx="44.6" cy="82.4" r="1.5" fill="#fff"/>
          <circle cx="68.6" cy="82.4" r="1.5" fill="#fff"/>
          <circle cx="36" cy="95" r="6" fill="#f6a0b4" opacity="0.75"/>
          <circle cx="74" cy="95" r="6" fill="#f6a0b4" opacity="0.75"/>
          <path d="M48 96 Q55 103 62 96" stroke="#3a2a1a" stroke-width="2.4"
                fill="none" stroke-linecap="round"/>
        </g></g>
      </svg>
    </div>
    <p class="mininame">미니미 — 도토리네 방</p>
    <p class="mood">오늘의 기분: 🌧️</p>
    <p class="bgm" id="bgm">♪ BGM: 첫눈</p>
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

    <section class="card"><h2>🎀 방 꾸미기 상점 <small style="font-weight:normal;color:#789">(사면 방이 바뀜)</small></h2>
      <button onclick="shop('벽지:하늘',80)">벽지:하늘 (80)</button>
      <button onclick="shop('벽지:노을',80)">벽지:노을 (80)</button>
      <button onclick="shop('벽지:벚꽃',80)">벽지:벚꽃 (80)</button>
      <button onclick="shop('BGM:벚꽃엔딩',50)">BGM:벚꽃엔딩 (50)</button>
      <div class="msg" id="smsg"></div>
      <div style="font-size:12px;color:#577">보유: <span id="owned">-</span></div></section>

    <section class="card"><h2>👫 일촌 <small style="font-weight:normal;color:#789">(수락하면 방에 친구 등장)</small></h2>
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
function friendSVG(name, i){
  const caps = ['#b46b8f','#6f9bd1','#cda14a','#7bbf8a'];
  const x = 116 + i*24, y = 122, cap = caps[i % caps.length];
  return '<g transform="translate('+x+','+y+') scale(0.40)"><title>'+name+'</title>'
    + '<ellipse cx="55" cy="124" rx="30" ry="7" fill="#000" opacity="0.10"/>'
    + '<path d="M22 56 Q55 18 88 56 Q55 70 22 56 Z" fill="'+cap+'"/>'
    + '<ellipse cx="55" cy="86" rx="34" ry="36" fill="#edcb95" stroke="#d8b277" stroke-width="2"/>'
    + '<circle cx="45" cy="86" r="4" fill="#3a2a1a"/><circle cx="65" cy="86" r="4" fill="#3a2a1a"/>'
    + '<circle cx="38" cy="95" r="5" fill="#f6a0b4" opacity="0.7"/>'
    + '<circle cx="72" cy="95" r="5" fill="#f6a0b4" opacity="0.7"/>'
    + '<path d="M48 97 Q55 103 62 97" stroke="#3a2a1a" stroke-width="2.2" fill="none" stroke-linecap="round"/></g>';
}
async function refresh(){
  const s = await (await fetch('/api/state')).json();
  title.textContent = s.owner + '님의 미니홈피';
  today.textContent = s.today; total.textContent = s.total; bal.textContent = s.balance;
  ilchons.textContent = '일촌(' + s.ilchons.length + '): ' + (s.ilchons.join(', ') || '아직 없음');
  gb.innerHTML = s.guestbook.map(e =>
    '<li'+(e.secret?' class="secret"':'')+'><b>'+e.author+'</b>: '+e.msg+(e.secret?' 🔒':'')+'</li>').join('');
  // 방 꾸미기 반영: 벽지·BGM·보유·일촌 미니미
  document.getElementById('wall').setAttribute('fill', s.room.wallpaper);
  document.getElementById('bgm').textContent = '♪ BGM: ' + s.room.bgm;
  document.getElementById('owned').textContent = s.room.owned.join(', ') || '없음';
  document.getElementById('friends').innerHTML = s.ilchons.slice(0,4).map(friendSVG).join('');
}
async function shop(item, price){
  const r = await api('/api/purchase',{user:'도토리',item:item,price:price});
  smsg.textContent = r.error ? ('구매 실패: '+r.error) : (item+' 적용! 잔액 '+r.balance);
  refresh();
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
