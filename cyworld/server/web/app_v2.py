# -*- coding: utf-8 -*-
"""미니홈피 웹 프론트 v2 — 실제 싸이월드 '책 펼친(open-book) 2단' 비율 배치.

현재 버전(app.py)은 그대로 두고, 레이아웃만 싸이월드 미니홈피 비율로 재배치한 다음 버전.
- 왼쪽 페이지: 미니룸(크게) + 프로필 + 기분/BGM
- 오른쪽 페이지: 메뉴 탭 + 본문(도토리·방꾸미기·일촌·기분·방명록)
도메인 서비스·JSON API·JS는 app.py 것을 그대로 재사용한다(화면 비율/배치만 변경).

실행:  python3 -m server.web.app_v2   # → http://localhost:8001
"""
from http.server import ThreadingHTTPServer
from urllib.parse import urlparse

from server.web import app as base  # 서비스·state·API 핸들러 재사용

# app.py의 방 SVG와 스크립트를 그대로 재사용(요소 id 동일 → JS 그대로 동작)
ROOM_SVG = base.PAGE.split('<div class="room">', 1)[1].split('</div>', 1)[0]
SCRIPT = base.PAGE.split("<script>", 1)[1].rsplit("</script>", 1)[0]

PAGE_V2 = """<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>도토리님의 미니홈피</title>
<style>
  body{margin:0;background:#243447;font-family:'맑은 고딕',sans-serif;color:#3a3024;
       display:flex;justify-content:center;align-items:flex-start;padding:26px 10px}
  /* 책 펼친 2단: 좌우 페이지 + 가운데 접힘선 */
  .book{width:940px;max-width:97vw;min-height:600px;display:flex;position:relative;
        background:#f5edd9;border-radius:10px;box-shadow:0 12px 44px #0008;overflow:hidden}
  .book::after{content:"";position:absolute;left:50%;top:0;bottom:0;width:0;
               border-left:1px solid #d8cba8;box-shadow:0 0 20px 7px #0002}
  .page{width:50%;box-sizing:border-box;padding:18px 22px}
  .page.left{background:linear-gradient(135deg,#f9f3e3,#efe4c8);text-align:center}
  .page.right{background:linear-gradient(135deg,#fdf8ec,#f3ead2)}
  /* 왼쪽: 타이틀 + 투데이 카운터 */
  .hp-head{display:flex;justify-content:space-between;align-items:baseline;
           border-bottom:2px solid #e0d3b0;padding-bottom:6px;margin-bottom:10px;text-align:left}
  .hp-name{font-size:15px;font-weight:bold;color:#5a4326}
  .hp-counter{font-size:11px;color:#8a7350}
  .hp-counter b{color:#c0563c}
  /* 미니룸: 좌측 페이지에서 크게 */
  .room{width:300px;max-width:100%;margin:4px auto 6px;border-radius:10px;overflow:hidden;
        box-shadow:inset 0 0 0 3px #fff,0 2px 8px #0003;border:1px solid #c9a;background:#fdeede}
  .room svg{display:block;width:100%;height:auto}
  .mini{animation:bob 2.6s ease-in-out infinite;transform-origin:center}
  @keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}
  .mininame{font-size:12px;color:#88600f;font-weight:bold;margin:2px 0 8px}
  /* 프로필 카드 */
  .profile{display:flex;align-items:center;gap:10px;text-align:left;
           background:#fffdf6;border:1px solid #e6dcc0;border-radius:8px;padding:8px 10px;margin:6px 2px}
  .pf-photo{width:46px;height:46px;border-radius:8px;background:#ffe7c2;border:1px solid #e3c79a;
            font-size:24px;display:flex;align-items:center;justify-content:center}
  .pf-info{font-size:12px;color:#5a4632;line-height:1.5}
  .pf-info b{font-size:13px;color:#3a2c18}
  .mood{font-size:12px;color:#6b7b5a;margin:8px 0 2px}
  .bgm{font-size:12px;color:#8a7a9a;margin:2px 0}
  /* 오른쪽: 메뉴 탭 + 본문 */
  .tabs{margin:2px 0 0;white-space:nowrap}
  .tabs a{display:inline-block;padding:5px 11px;font-size:12px;color:#6a543a;text-decoration:none;
          border:1px solid #d8cba8;border-bottom:none;border-radius:7px 7px 0 0;
          background:#ece0c2;margin-right:3px;cursor:pointer}
  .tabs a.on{background:#fffdf6;color:#15406b;font-weight:bold}
  .rcontent{border:1px solid #d8cba8;background:#fffdf6;border-radius:0 8px 8px 8px;padding:12px}
  section.card{border:1px solid #ece2c8;border-radius:6px;padding:9px 10px;margin:9px 0;background:#fffefa}
  section.card:first-child{margin-top:0}
  section.card h2{font-size:13px;margin:0 0 7px;color:#7a5a2a}
  input,button{font-size:12px;padding:3px 6px;margin:2px}
  button{background:#4a6f9c;color:#fff;border:0;border-radius:4px;cursor:pointer}
  ul{margin:6px 0;padding-left:18px;font-size:12px}
  .msg{font-size:11px;color:#c33;min-height:14px}
  .secret{color:#a6a}
</style></head>
<body>
  <div class="book">
    <!-- 왼쪽 페이지: 미니룸 · 프로필 -->
    <div class="page left">
      <div class="hp-head">
        <div class="hp-name" id="title">도토리님의 미니홈피</div>
        <div class="hp-counter">TODAY <b id="today">-</b> · TOTAL <b id="total">-</b></div>
      </div>
      <div class="room">""" + ROOM_SVG + """</div>
      <p class="mininame">미니미 — 도토리네 방</p>
      <div class="profile">
        <div class="pf-photo">🌰</div>
        <div class="pf-info"><b>도토리</b><br><span>추억의 그 시절 ✿ 일촌 환영</span></div>
      </div>
      <p class="mood" id="moodtxt">오늘의 기분: 🌧️</p>
      <p class="bgm" id="bgm">♪ BGM: 첫눈</p>
    </div>
    <!-- 오른쪽 페이지: 메뉴 탭 + 본문 -->
    <div class="page right">
      <nav class="tabs">
        <a class="on">홈</a><a>프로필</a><a>다이어리</a><a>사진첩</a><a>방명록</a>
      </nav>
      <div class="rcontent">
        <section class="card"><h2>🌰 도토리</h2>
          <input id="amt" type="number" value="100" style="width:64px"><button onclick="charge()">충전</button>
          <input id="item" value="미니룸스킨" style="width:84px">
          <input id="price" type="number" value="120" style="width:54px"><button onclick="buy()">구매</button>
          <div class="msg" id="dmsg"></div></section>

        <section class="card"><h2>🎀 방 꾸미기 상점 <small style="font-weight:normal;color:#a08">(사면 방이 바뀜)</small></h2>
          <button onclick="shop('벽지:하늘',80)">벽지:하늘 (80)</button>
          <button onclick="shop('벽지:노을',80)">벽지:노을 (80)</button>
          <button onclick="shop('벽지:벚꽃',80)">벽지:벚꽃 (80)</button>
          <button onclick="shop('BGM:벚꽃엔딩',50)">BGM:벚꽃엔딩 (50)</button>
          <div class="msg" id="smsg"></div>
          <div style="font-size:11px;color:#777">보유: <span id="owned">-</span></div></section>

        <section class="card"><h2>👫 일촌 <small style="font-weight:normal;color:#a08">(수락하면 방에 친구 등장)</small></h2>
          <span id="ilchons" style="font-size:12px"></span><br>
          <input id="who" value="친구C" style="width:74px"><button onclick="ilreq()">신청</button>
          <button onclick="ilacc()">친구B 수락</button>
          <div class="msg" id="imsg"></div></section>

        <section class="card"><h2>🌤️ 오늘의 기분 <small style="font-weight:normal;color:#a08">(창문 날씨 + 표정)</small></h2>
          <button onclick="setMood('맑음')">☀️ 맑음</button>
          <button onclick="setMood('흐림')">☁️ 흐림</button>
          <button onclick="setMood('비')">🌧️ 비</button>
          <button onclick="setMood('행복')">😊 행복</button></section>

        <section class="card"><h2>📖 방명록</h2>
          <input id="gauthor" value="방문자" style="width:64px">
          <input id="gmsg" value="다녀가요~" style="width:120px">
          <label style="font-size:11px"><input id="gsecret" type="checkbox">비밀</label>
          <button onclick="sign()">남기기</button>
          <ul id="gb"></ul></section>
      </div>
    </div>
  </div>
<script>""" + SCRIPT + """</script>
</body></html>"""


class HandlerV2(base.Handler):
    def do_GET(self):
        if urlparse(self.path).path == "/":
            return self._send(200, PAGE_V2, "text/html")
        return super().do_GET()


def main(port=8001):
    base._seed()
    srv = ThreadingHTTPServer(("127.0.0.1", port), HandlerV2)
    print(f"미니홈피 v2 (싸이월드 책 비율): http://localhost:{port}  (Ctrl+C 종료)")
    srv.serve_forever()


if __name__ == "__main__":
    main()
