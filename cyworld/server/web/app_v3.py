# -*- coding: utf-8 -*-
"""미니홈피 웹 프론트 v3 — 실제 싸이월드 화면(sdd/00_sources 레퍼런스) 배치 반영.

레퍼런스: sdd/00_sources/2026-06-09 08 05 47.png (실제 미니홈피 캡처)
실제 구조 = 좌측 좁은 '프로필 칸' + 우측 넓은 '메인 칸(미니룸이 메인 비주얼)'.
- 좌측: TODAY/TOTAL → 미니미 얼굴(포트레이트) → TODAY IS(기분) → 주인 메시지 → HISTORY → 홈주인·일촌
- 메인: 타이틀(이름 + url) → 메뉴(다이어리·사진첩·방명록 + 카운트) → 미니룸(크게) → 본문(도토리·방꾸미기·일촌·기분·방명록)
도메인 서비스·JSON API·JS는 app.py 것을 그대로 재사용(요소 id 동일).

실행:  python3 -m server.web.app_v3   # → http://localhost:8002
"""
from http.server import ThreadingHTTPServer
from urllib.parse import urlparse

from server.web import app as base

ROOM_SVG = base.PAGE.split('<div class="room">', 1)[1].split('</div>', 1)[0]
SCRIPT = base.PAGE.split("<script>", 1)[1].rsplit("</script>", 1)[0]

# 좌측 포트레이트(미니미 얼굴 클로즈업) — 정적 SVG
PORTRAIT = """<svg width="120" height="128" viewBox="0 0 120 128" aria-label="미니미 얼굴">
  <rect x="54" y="8" width="11" height="16" rx="5" fill="#7a5230"/>
  <path d="M16 52 Q60 12 104 52 Q60 68 16 52 Z" fill="#9c6b3f"/>
  <path d="M16 52 Q60 68 104 52 Q82 62 60 62 Q38 62 16 52 Z" fill="#84592f"/>
  <ellipse cx="60" cy="88" rx="44" ry="44" fill="#edcb95"/>
  <ellipse cx="60" cy="88" rx="44" ry="44" fill="none" stroke="#d8b277" stroke-width="2"/>
  <circle cx="46" cy="86" r="5.5" fill="#3a2a1a"/><circle cx="74" cy="86" r="5.5" fill="#3a2a1a"/>
  <circle cx="48" cy="84" r="1.8" fill="#fff"/><circle cx="76" cy="84" r="1.8" fill="#fff"/>
  <circle cx="37" cy="98" r="7" fill="#f6a0b4" opacity="0.75"/>
  <circle cx="83" cy="98" r="7" fill="#f6a0b4" opacity="0.75"/>
  <path d="M50 99 Q60 107 70 99" stroke="#3a2a1a" stroke-width="2.6" fill="none" stroke-linecap="round"/>
</svg>"""

PAGE_V3 = """<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>도토리님의 미니홈피</title>
<style>
  body{margin:0;background:#bfe3f5;font-family:'맑은 고딕',sans-serif;color:#2a4257;
       display:flex;justify-content:center;padding:22px 10px}
  .hp{width:900px;max-width:97vw;background:#dcf0fb;border:2px solid #8fc6e6;border-radius:16px;
      padding:14px;display:flex;gap:12px;box-shadow:0 10px 40px #0005}
  .pane{background:#fff;border:1px solid #bfe0f0;border-radius:10px;padding:10px}
  /* 좌측 프로필 칸 */
  .left{width:248px;flex:none;display:flex;flex-direction:column;gap:10px}
  .today-bar{background:#eaf6fd;border:1px solid #bfe0f0;border-radius:8px;padding:5px 8px;
             font-size:11px;text-align:center;color:#3a6a86}
  .today-bar b{color:#e0563c}
  .portrait{text-align:center;padding:12px 10px 10px}
  .portrait .frame{border:1px solid #d3e6f0;border-radius:8px;background:#f7fcff;padding:6px;display:inline-block}
  .todayis{font-size:12px;color:#2f9fd0;font-weight:bold;margin:8px 0 0}
  .owner-msg{color:#e3577f;font-size:12px;line-height:1.5;margin:6px 2px 0}
  .history{font-size:11px;color:#5a7d92;line-height:1.7}
  .history .t{color:#2f6f93;font-weight:bold}
  .owner-sel{font-size:11px;color:#46708a}
  .owner-sel select{font-size:11px;margin-top:3px;width:100%}
  /* 메인 칸 */
  .main{flex:1;display:flex;flex-direction:column;gap:10px}
  .main-head{display:flex;justify-content:space-between;align-items:baseline;
             border-bottom:2px solid #8fc6e6;padding-bottom:7px}
  .main-head .nm{font-size:17px;font-weight:bold;color:#15557e}
  .main-head .url{font-size:11px;color:#7fa6bd}
  .menu-row{display:flex;flex-wrap:wrap;gap:5px}
  .menu-row a{font-size:11px;color:#39698a;text-decoration:none;background:#eaf6fd;
              border:1px solid #cfe6f2;border-radius:12px;padding:3px 9px}
  .menu-row a.on{background:#2f7fb0;color:#fff;border-color:#2f7fb0;font-weight:bold}
  .menu-row a b{color:#e0563c}
  .roompane{display:flex;gap:12px;align-items:center}
  .roompane .room{width:300px;flex:none;border-radius:10px;overflow:hidden;
                  box-shadow:inset 0 0 0 3px #fff,0 1px 6px #0003;border:1px solid #c9a;background:#fdeede}
  .roompane .room svg{display:block;width:100%;height:auto}
  .mini{animation:bob 2.6s ease-in-out infinite;transform-origin:center}
  @keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}
  .roomside{font-size:12px;color:#46708a;line-height:1.8}
  .roomside .lk{color:#2f7fb0}
  .mininame{font-size:11px;color:#88600f;font-weight:bold}
  /* 본문 카드 */
  section.card{border:1px solid #cfe6f2;border-radius:8px;padding:9px 10px;background:#f9fdff}
  section.card h2{font-size:13px;margin:0 0 7px;color:#15557e}
  input,button{font-size:12px;padding:3px 6px;margin:2px}
  button{background:#2f7fb0;color:#fff;border:0;border-radius:4px;cursor:pointer}
  ul{margin:6px 0;padding-left:18px;font-size:12px}
  .msg{font-size:11px;color:#c33;min-height:14px}
  .secret{color:#a6a}
  .bgm{font-size:11px;color:#8a7a9a}
</style></head>
<body>
  <div class="hp">
    <!-- 좌측: 프로필 칸 -->
    <div class="left">
      <div class="today-bar">TODAY <b id="today">-</b> · TOTAL <b id="total">-</b></div>
      <div class="pane portrait">
        <div class="frame">""" + PORTRAIT + """</div>
        <div class="todayis" id="moodtxt">오늘의 기분: 🌧️</div>
        <div class="owner-msg">싸이 5th 생일 축하해요!!!<br>모두 놀러와 주실꺼죠?♪</div>
      </div>
      <div class="pane history">
        <div>▶ HISTORY</div>
        <div><span class="t">미니홈피</span> 2026. 6. 9 (＋)</div>
        <div class="bgm" id="bgm">♪ BGM: 첫눈</div>
      </div>
      <div class="pane owner-sel">
        홈주인 <b>도토리</b>
        <select><option>★ 나의 일촌</option></select>
        <div id="ilchons" style="margin-top:5px;color:#39698a"></div>
      </div>
    </div>
    <!-- 메인 칸 -->
    <div class="main">
      <div class="main-head">
        <div class="nm" id="title">도토리님의 미니홈피</div>
        <div class="url">http://www.cyworld.com/dotori</div>
      </div>
      <div class="menu-row">
        <a class="on">홈</a><a>프로필</a><a>다이어리 <b>12</b></a>
        <a>사진첩 <b>34</b></a><a>방명록</a>
      </div>
      <div class="pane roompane">
        <div class="room">""" + ROOM_SVG + """</div>
        <div class="roomside">
          <div class="mininame">Mini Room</div>
          <div>도토리네 미니룸이에요.</div>
          <div class="lk">미니룸 · 일촌평 · 방명록</div>
          <div>🌰 도토리 <b id="bal">-</b></div>
        </div>
      </div>

      <section class="card"><h2>🌰 도토리</h2>
        <input id="amt" type="number" value="100" style="width:64px"><button onclick="charge()">충전</button>
        <input id="item" value="미니룸스킨" style="width:84px">
        <input id="price" type="number" value="120" style="width:54px"><button onclick="buy()">구매</button>
        <div class="msg" id="dmsg"></div></section>

      <section class="card"><h2>🎀 방 꾸미기 상점 <small style="font-weight:normal;color:#789">(사면 방이 바뀜)</small></h2>
        <button onclick="shop('벽지:하늘',80)">벽지:하늘 (80)</button>
        <button onclick="shop('벽지:노을',80)">벽지:노을 (80)</button>
        <button onclick="shop('벽지:벚꽃',80)">벽지:벚꽃 (80)</button>
        <button onclick="shop('BGM:벚꽃엔딩',50)">BGM:벚꽃엔딩 (50)</button>
        <div class="msg" id="smsg"></div>
        <div style="font-size:11px;color:#777">보유: <span id="owned">-</span></div></section>

      <section class="card"><h2>👫 일촌 <small style="font-weight:normal;color:#789">(수락하면 방에 친구 등장)</small></h2>
        <input id="who" value="친구C" style="width:74px"><button onclick="ilreq()">신청</button>
        <button onclick="ilacc()">친구B 수락</button>
        <div class="msg" id="imsg"></div></section>

      <section class="card"><h2>🌤️ 오늘의 기분 <small style="font-weight:normal;color:#789">(창문 날씨 + 표정)</small></h2>
        <button onclick="setMood('맑음')">☀️ 맑음</button>
        <button onclick="setMood('흐림')">☁️ 흐림</button>
        <button onclick="setMood('비')">🌧️ 비</button>
        <button onclick="setMood('행복')">😊 행복</button></section>

      <section class="card"><h2>📖 방명록 <small style="font-weight:normal;color:#789">What friends say ♥</small></h2>
        <input id="gauthor" value="방문자" style="width:64px">
        <input id="gmsg" value="다녀가요~" style="width:120px">
        <label style="font-size:11px"><input id="gsecret" type="checkbox">비밀</label>
        <button onclick="sign()">남기기</button>
        <ul id="gb"></ul></section>
    </div>
  </div>
<script>""" + SCRIPT + """</script>
</body></html>"""


class HandlerV3(base.Handler):
    def do_GET(self):
        if urlparse(self.path).path == "/":
            return self._send(200, PAGE_V3, "text/html")
        return super().do_GET()


def main(port=8002):
    base._seed()
    srv = ThreadingHTTPServer(("127.0.0.1", port), HandlerV3)
    print(f"미니홈피 v3 (실제 싸이월드 배치): http://localhost:{port}  (Ctrl+C 종료)")
    srv.serve_forever()


if __name__ == "__main__":
    main()
