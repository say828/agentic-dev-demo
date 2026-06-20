# -*- coding: utf-8 -*-
"""버디버디 로컬 웹 프론트 (의존성 0, 파이썬 표준 http.server).

도메인 서비스(presence/buddy/message)를 JSON API로 노출한다. 화면은 세 가지:
- `/`               → 로비(누구로 접속할지 고름)
- `/?me=현주`       → **그 사용자 1명**의 메신저 창(프론트 1개 = 사용자 1명)
- `/demo`           → 현주·민수 두 창을 한 페이지에 나란히(한눈에 보기용)

두 개의 브라우저 창을 각각 `/?me=현주`, `/?me=민수` 로 열면 같은 서버를 통해
서로 메시지를 주고받는다. 각 창은 1초마다 폴링해 상대가 보낸 메시지를 받는다.
웹소켓 없이 표준 라이브러리만 쓰며 "실시간"은 폴링으로 흉내 낸다.

실행:  python -m server.web.app   # → http://localhost:8010
"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from server.contexts.buddybuddy.buddy import BuddyService
from server.contexts.buddybuddy.message import MessageService
from server.contexts.buddybuddy.presence import PresenceService
from server.contexts.buddybuddy.screens import MASCOT_SVG

# 데모 단일 인스턴스(인메모리).
presence = PresenceService()
buddy = BuddyService()
message = MessageService()

# 로비에 띄울 추천 사용자(서로 버디 + 시드 대화).
USERS = ["현주", "민수"]


def _seed():
    for u in USERS:
        presence.login(u)
    buddy.add("현주", "민수")
    buddy.add("민수", "현주")
    message.send("현주", "민수", "민수야 접속했어? 🐤", client_msg_id="seed-1")
    message.send("민수", "현주", "어 현주야! 방가방가~", client_msg_id="seed-2")


def state(me):
    # 버디(명시 추가) ∪ 대화 상대(메시지 주고받은 사람) — 순서 보존, 중복 제거.
    names = list(dict.fromkeys(buddy.buddies(me) + message.partners(me)))
    return {
        "me": me,
        "status": presence.status(me),
        "online": presence.online(),
        "buddies": [
            {"name": n, "status": presence.status(n),
             "unread": message.unread(me, n)}
            for n in names
        ],
    }


# ──────────────────────────────── 화면 공통 ────────────────────────────────
HEAD = """<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>버디버디 — 로컬 데모</title>
<style>
  body{margin:0;background:#2b6cb0 url('data:image/svg+xml;utf8,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%2240%22 height=%2240%22><circle cx=%2220%22 cy=%2220%22 r=%221.5%22 fill=%22%23ffffff22%22/></svg>');
       font-family:'맑은 고딕','Malgun Gothic',sans-serif;color:#1a2a3a}
  h1.brand{color:#fff;text-align:center;margin:18px 0 4px;font-size:22px;text-shadow:0 1px 2px #0005}
  p.sub{color:#dbeafe;text-align:center;margin:0 0 16px;font-size:13px}
  .stage{display:flex;gap:22px;justify-content:center;align-items:flex-start;flex-wrap:wrap;padding-bottom:30px}
  .client{width:300px;background:#eef4fb;border:1px solid #5a86b8;border-radius:8px;
          box-shadow:0 6px 16px #0004;overflow:hidden}
  .single{margin:26px auto}
  .titlebar{display:flex;align-items:center;gap:6px;padding:5px 8px;
            background:linear-gradient(#4a90d9,#2f6db5);color:#fff;font-weight:bold;font-size:13px}
  .titlebar .tt{flex:1}
  .winbtns i{display:inline-block;width:16px;height:14px;line-height:14px;text-align:center;
             background:#ffffff33;border-radius:2px;margin-left:2px;font-style:normal;font-size:10px}
  .me{display:flex;align-items:center;gap:8px;padding:8px 10px;background:#dce8f6;border-bottom:1px solid #c2d6ee}
  .me .nm{font-weight:bold;font-size:14px}
  .dot{width:9px;height:9px;border-radius:50%;display:inline-block;margin-left:4px}
  .on{background:#36c06a;box-shadow:0 0 4px #36c06a}
  .off{background:#b6bcc4}
  .cols{display:flex;height:330px}
  .buddies{width:104px;background:#f6f9fd;border-right:1px solid #d6e2f0;overflow-y:auto}
  .buddies .grp{font-size:11px;color:#6b87a8;padding:5px 8px 2px}
  .buddies .b{display:flex;align-items:center;gap:5px;padding:5px 8px;cursor:pointer;font-size:13px}
  .buddies .b:hover{background:#e4eefb}
  .buddies .b.sel{background:#d3e6ff;font-weight:bold}
  .buddies .b .badge{margin-left:auto;background:#ff4d6d;color:#fff;font-size:10px;
                     min-width:16px;height:16px;line-height:16px;text-align:center;border-radius:9px}
  .chat{flex:1;display:flex;flex-direction:column}
  .partner{font-size:12px;color:#345;padding:5px 8px;border-bottom:1px solid #e0e9f4;background:#fff}
  .thread{flex:1;overflow-y:auto;padding:8px;background:#ffffff}
  .row{display:flex;margin:4px 0}
  .row.mine{justify-content:flex-end}
  .bubble{max-width:78%;padding:6px 9px;border-radius:12px;font-size:13px;line-height:1.35;
          word-break:break-word;box-shadow:0 1px 1px #0001}
  .row.theirs .bubble{background:#eef1f5;border:1px solid #e0e4ea;border-top-left-radius:3px}
  .row.mine .bubble{background:#fee36b;border:1px solid #f3d54e;border-top-right-radius:3px}
  .who{font-size:10px;color:#8aa;margin:0 4px 1px}
  .input{display:flex;gap:4px;padding:6px;border-top:1px solid #e0e9f4;background:#f3f7fc}
  .input input{flex:1;font-size:13px;padding:5px 7px;border:1px solid #b9cde3;border-radius:5px}
  .input button{font-size:13px;padding:5px 12px;border:0;border-radius:5px;cursor:pointer;
                background:#2f6db5;color:#fff;font-weight:bold}
  .addbuddy{display:flex;gap:4px;padding:6px;border-top:1px solid #d6e2f0;background:#f6f9fd}
  .addbuddy input{flex:1;font-size:12px;padding:4px 6px;border:1px solid #b9cde3;border-radius:5px}
  .addbuddy button{font-size:12px;padding:4px 10px;border:0;border-radius:5px;background:#5a86b8;color:#fff;cursor:pointer}
  .empty{color:#9bb;font-size:12px;text-align:center;margin-top:30px}
  .tip{color:#dbeafe;text-align:center;font-size:12px;margin:12px auto 0;max-width:340px}
  .tip a{color:#fff}
  /* 로비 */
  .lobby{width:320px;margin:46px auto;background:#eef4fb;border:1px solid #5a86b8;border-radius:10px;
         box-shadow:0 6px 16px #0004;overflow:hidden}
  .lobby .lb{padding:22px 18px;text-align:center}
  .lobby h2{font-size:15px;margin:0 0 14px;color:#1a3a5a}
  .lobby a.pick{display:inline-block;margin:4px;padding:9px 18px;border-radius:6px;
                background:#2f6db5;color:#fff;font-weight:bold;text-decoration:none;font-size:14px}
  .lobby .or{color:#789;font-size:12px;margin:16px 0 8px}
  .lobby .namerow{display:flex;gap:6px;justify-content:center}
  .lobby input{font-size:14px;padding:6px 8px;border:1px solid #b9cde3;border-radius:6px;width:130px}
  .lobby button{font-size:14px;padding:6px 14px;border:0;border-radius:6px;background:#36c06a;color:#fff;
                font-weight:bold;cursor:pointer}
  .lobby .demo{display:block;margin-top:18px;font-size:12px;color:#567}
</style></head>
"""


# ──────────────────────────────── 로비 ────────────────────────────────
LOBBY_BODY = """<body>
  <h1 class="brand">버디버디 · BuddyBuddy</h1>
  <p class="sub">누구로 접속할까요? (창을 2개 열어 서로 대화해 보세요)</p>
  <div class="lobby"><div class="lb">
    <h2>__MASCOT__<br>로그인</h2>
    <a class="pick" href="/?me=%ED%98%84%EC%A3%BC">현주로 접속</a>
    <a class="pick" href="/?me=%EB%AF%BC%EC%88%98">민수로 접속</a>
    <div class="or">— 또는 새 이름으로 —</div>
    <div class="namerow">
      <input id="nm" placeholder="이름 입력" onkeydown="if(event.key==='Enter')go()">
      <button onclick="go()">접속</button>
    </div>
    <a class="demo" href="/demo">▶ 두 창 한눈에 보기 (데모)</a>
  </div></div>
  <p class="tip">팁: 브라우저 창 2개를 띄워 한쪽은 <b>현주</b>, 한쪽은 <b>민수</b>로 접속하면
     실제로 주고받는 게 보입니다.</p>
<script>
function go(){ const v=document.getElementById('nm').value.trim();
  if(v) location.href='/?me='+encodeURIComponent(v); }
</script>
</body></html>"""


# ──────────────────────── 단일 사용자 클라이언트 ────────────────────────
CLIENT_BODY = """<body>
  <h1 class="brand">버디버디 · BuddyBuddy</h1>
  <p class="sub"><b>__ME__</b> 님으로 접속됨 · 다른 창에서 <code>/?me=이름</code>으로 접속해 대화</p>
  <div class="client single">
    <div class="titlebar">__MASCOT__<span class="tt">__ME__ 님 — 버디버디</span>
      <span class="winbtns"><i>_</i><i>□</i><i>×</i></span></div>
    <div class="me">__MASCOT__<span class="nm">__ME__</span>
      <span class="dot on" id="dot"></span><span style="font-size:11px;color:#567" id="st">online</span></div>
    <div class="cols">
      <div class="buddies"><div class="grp">버디</div><div id="buddies"></div></div>
      <div class="chat">
        <div class="partner" id="partner">대화 상대를 고르세요</div>
        <div class="thread" id="thread"></div>
        <div class="input">
          <input id="input" placeholder="메시지 입력..." onkeydown="if(event.key==='Enter')sendMsg()">
          <button onclick="sendMsg()">전송</button>
        </div>
      </div>
    </div>
    <div class="addbuddy">
      <input id="newbuddy" placeholder="버디 추가 (이름)" onkeydown="if(event.key==='Enter')addBuddy()">
      <button onclick="addBuddy()">추가</button>
    </div>
  </div>
  <p class="tip"><a href="/">← 로비</a> · 다른 사람과 대화하려면 새 창에서 <b>/?me=이름</b>으로 접속</p>
<script>
const ME = "__ME__";
let sel = null;     // 보고 있는 상대
let cmid = 0;       // 전송 멱등 카운터
const enc = encodeURIComponent;

async function api(path, body){
  const r = await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify(body)});
  return r.json();
}
async function getJSON(path){ return (await fetch(path)).json(); }
function escapeHtml(s){ return s.replace(/[&<>\"']/g,c=>(
  {'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c])); }

async function sendMsg(){
  const box=document.getElementById('input'); const text=box.value.trim();
  if(!text || !sel) return;
  cmid++;
  await api('/api/send',{frm:ME,to:sel,text:text,client_msg_id:ME+'-'+cmid});
  box.value=''; refresh();
}
function pickBuddy(name){ sel=name; refresh(); }
async function addBuddy(){
  const box=document.getElementById('newbuddy'); const name=box.value.trim();
  if(!name || name===ME) return;
  await api('/api/buddy_add',{owner:ME,buddy:name});
  box.value=''; sel=name; refresh();
}
function renderBuddies(s){
  const box=document.getElementById('buddies');
  if(!sel && s.buddies.length) sel=s.buddies[0].name;
  box.innerHTML = s.buddies.map(b=>{
    const cls=(b.name===sel)?'b sel':'b';
    const dot=b.status==='online'?'on':'off';
    const badge=b.unread>0?`<span class="badge">${b.unread}</span>`:'';
    return `<div class="${cls}" onclick="pickBuddy('${b.name}')">
      <span class="dot ${dot}"></span>${b.name}${badge}</div>`;
  }).join('') || '<div style="font-size:12px;color:#9bb;padding:8px">버디를 추가하세요</div>';
}
async function renderThread(){
  const tEl=document.getElementById('thread'), pEl=document.getElementById('partner');
  if(!sel){ tEl.innerHTML='<div class="empty">버디를 클릭해 대화를 시작하세요</div>';
    pEl.textContent='대화 상대를 고르세요'; return; }
  pEl.textContent=sel+' 님과의 대화';
  const msgs=await getJSON('/api/thread?a='+enc(ME)+'&b='+enc(sel));
  tEl.innerHTML = msgs.map(m=>{
    const mine=m.frm===ME;
    return `<div class="row ${mine?'mine':'theirs'}">`+
      `<div><div class="who">${mine?'':m.frm}</div><div class="bubble">${escapeHtml(m.text)}</div></div></div>`;
  }).join('') || '<div class="empty">아직 메시지가 없어요</div>';
  tEl.scrollTop=tEl.scrollHeight;
  await api('/api/read',{reader:ME,other:sel});   // 창이 열려 있으니 읽음 처리(AC-5)
}
async function refresh(){
  const s=await getJSON('/api/state?me='+enc(ME));
  document.getElementById('st').textContent=s.status;
  document.getElementById('dot').className='dot '+(s.status==='online'?'on':'off');
  renderBuddies(s);
  await renderThread();
}
async function boot(){
  await api('/api/login',{user:ME});   // 이 프론트 = ME 접속 → 온라인
  refresh();
  setInterval(refresh,1000);           // 폴링 = 실시간 흉내
}
boot();
</script>
</body></html>"""


# ──────────────────── 데모(두 창 한 페이지) — 기존 보기 ────────────────────
DEMO_BODY = """<body>
  <h1 class="brand">버디버디 · BuddyBuddy</h1>
  <p class="sub">데모: 두 사용자 창을 한 페이지에 — <a href="/" style="color:#fff">로비로</a></p>
  <div class="stage" id="stage"></div>
  <p class="tip">왼쪽(현주) 입력 → 1초 내 오른쪽(민수) 창에 도착합니다. 버디를 바꾸면 대화도 분리돼요.</p>
<script>
const MASCOT = `__MASCOT__`;
const USERS = __USERS__;
const sel = {};
const cmid = {};
const enc = encodeURIComponent;
async function api(path, body){
  const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  return r.json();
}
async function getJSON(path){ return (await fetch(path)).json(); }
function escapeHtml(s){ return s.replace(/[&<>\"']/g,c=>(
  {'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c])); }
function panelHTML(me){
  return `<div class="client" data-me="${me}">
    <div class="titlebar">${MASCOT}<span class="tt">${me} 님 — 버디버디</span>
      <span class="winbtns"><i>_</i><i>□</i><i>×</i></span></div>
    <div class="me">${MASCOT}<span class="nm">${me}</span>
      <span class="dot on" id="dot-${me}"></span><span style="font-size:11px;color:#567" id="st-${me}">online</span></div>
    <div class="cols">
      <div class="buddies"><div class="grp">버디</div><div id="buddies-${me}"></div></div>
      <div class="chat">
        <div class="partner" id="partner-${me}">대화 상대를 고르세요</div>
        <div class="thread" id="thread-${me}"></div>
        <div class="input">
          <input id="input-${me}" placeholder="메시지 입력..." onkeydown="if(event.key==='Enter')sendMsg('${me}')">
          <button onclick="sendMsg('${me}')">전송</button>
        </div>
      </div>
    </div>
  </div>`;
}
async function sendMsg(me){
  const box=document.getElementById('input-'+me); const text=box.value.trim(); const to=sel[me];
  if(!text || !to) return;
  cmid[me]=(cmid[me]||0)+1;
  await api('/api/send',{frm:me,to:to,text:text,client_msg_id:me+'-'+cmid[me]});
  box.value=''; refresh();
}
function pickBuddy(me, name){ sel[me]=name; refresh(); }
function renderBuddies(me, s){
  const box=document.getElementById('buddies-'+me);
  box.innerHTML=s.buddies.map(b=>{
    const cls=(b.name===sel[me])?'b sel':'b'; const dot=b.status==='online'?'on':'off';
    const badge=b.unread>0?`<span class="badge">${b.unread}</span>`:'';
    return `<div class="${cls}" onclick="pickBuddy('${me}','${b.name}')"><span class="dot ${dot}"></span>${b.name}${badge}</div>`;
  }).join('');
}
async function renderThread(me){
  const to=sel[me]; const tEl=document.getElementById('thread-'+me); const pEl=document.getElementById('partner-'+me);
  if(!to){ tEl.innerHTML='<div class="empty">버디를 클릭해 대화를 시작하세요</div>'; return; }
  pEl.textContent=to+' 님과의 대화';
  const msgs=await getJSON('/api/thread?a='+enc(me)+'&b='+enc(to));
  tEl.innerHTML=msgs.map(m=>{ const mine=m.frm===me;
    return `<div class="row ${mine?'mine':'theirs'}"><div><div class="who">${mine?'':m.frm}</div><div class="bubble">${escapeHtml(m.text)}</div></div></div>`;
  }).join('') || '<div class="empty">아직 메시지가 없어요</div>';
  tEl.scrollTop=tEl.scrollHeight;
  await api('/api/read',{reader:me,other:to});
}
async function refresh(){
  for(const me of USERS){
    const s=await getJSON('/api/state?me='+enc(me));
    document.getElementById('st-'+me).textContent=s.status;
    document.getElementById('dot-'+me).className='dot '+(s.status==='online'?'on':'off');
    renderBuddies(me,s); await renderThread(me);
  }
}
function boot(){
  document.getElementById('stage').innerHTML=USERS.map(panelHTML).join('');
  sel[USERS[0]]=USERS[1]; sel[USERS[1]]=USERS[0];
  refresh(); setInterval(refresh,1000);
}
boot();
</script>
</body></html>"""


def render_lobby():
    return HEAD + LOBBY_BODY.replace("__MASCOT__", MASCOT_SVG)


def render_client(me):
    return (HEAD + CLIENT_BODY
            .replace("__MASCOT__", MASCOT_SVG)
            .replace("__ME__", me))


def render_demo():
    return (HEAD + DEMO_BODY
            .replace("__MASCOT__", MASCOT_SVG)
            .replace("__USERS__", json.dumps(USERS, ensure_ascii=False)))


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        if ctype.startswith("text"):
            data = body.encode("utf-8")
        else:
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
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
        q = parse_qs(u.query)
        if u.path == "/":
            me = q.get("me", [""])[0].strip()
            return self._send(200, render_client(me) if me else render_lobby(), "text/html")
        if u.path == "/demo":
            return self._send(200, render_demo(), "text/html")
        if u.path == "/api/state":
            me = q.get("me", [USERS[0]])[0]
            return self._send(200, state(me))
        if u.path == "/api/thread":
            a = q.get("a", [""])[0]
            b = q.get("b", [""])[0]
            return self._send(200, message.thread(a, b))
        return self._send(404, {"error": "not_found"})

    def do_POST(self):
        u = urlparse(self.path)
        try:
            b = self._body()
            if u.path == "/api/login":
                return self._send(200, presence.login(b["user"]))
            if u.path == "/api/logout":
                return self._send(200, presence.logout(b["user"]))
            if u.path == "/api/buddy_add":
                return self._send(200, buddy.add(b["owner"], b["buddy"]))
            if u.path == "/api/send":
                return self._send(200, message.send(
                    b["frm"], b["to"], b["text"], client_msg_id=b.get("client_msg_id")))
            if u.path == "/api/read":
                return self._send(200, message.mark_read(b["reader"], b["other"]))
        except (KeyError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as e:
            return self._send(400, {"error": f"bad_request: {e}"})
        return self._send(404, {"error": "not_found"})

    def log_message(self, *a):  # 조용히
        pass


def main(port=8010):
    _seed()
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"버디버디 로컬 데모: http://localhost:{port}  (Ctrl+C 종료)")
    srv.serve_forever()


if __name__ == "__main__":
    main()
