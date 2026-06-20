# -*- coding: utf-8 -*-
"""미니홈피 웹 프론트 v4 — v3에서 놓친 '우측 메뉴 그리드(탭) 구조'를 반영.

배경(원인): v3는 저해상도 소스를 전체로만 보고, 메뉴 영역을 따로 확대해 보지 않아
실제의 2열 메뉴 그리드(다이어리·쥬크박스·사진첩·갤러리·게시판·방명록 + today/total 카운트
+ N 배지)를 단순 가로 메뉴로 뭉뚱그렸다. v4는 메뉴 영역을 확대(crop) 확인해 그 구조를 반영.

레퍼런스: sdd/00_sources/2026-06-09 08 05 47.png (메뉴 영역 확대 확인)
도메인·API·JS는 app.py, 포트레이트는 app_v3 것을 재사용(요소 id 동일).

실행:  python3 -m server.web.app_v4   # → http://localhost:8003
"""
from http.server import ThreadingHTTPServer
from urllib.parse import urlparse

from server.web import app as base
from server.web.app_v3 import PORTRAIT

ROOM_SVG = base.PAGE.split('<div class="room">', 1)[1].split('</div>', 1)[0]
SCRIPT = base.PAGE.split("<script>", 1)[1].rsplit("</script>", 1)[0]

# 실제 소스의 우측 메뉴 그리드(2열 + today/total 카운트 + N 배지)
MENU_GRID = """
      <div class="header2">
        <div class="todaystory">
          <div class="t">TODAY STORY</div>
          Updated news<br>
          · 미니룸을 새로 꾸몄어요<br>
          · 일촌 신청 1건이 왔어요<br>
          · 방명록에 새 글이 있어요
        </div>
        <div class="menucard">
          <div class="bgm-h">🔊 BGM ▶ 첫눈</div>
          <div class="menugrid">
            <a>다이어리<span class="cnt">0/1</span></a>
            <a>쥬크박스<span class="cnt">0/0</span></a>
            <a>사진첩<span class="cnt">1396/1367<span class="nb">N</span></span></a>
            <a>갤러리<span class="cnt">0/0</span></a>
            <a>게시판<span class="cnt">1019/998<span class="nb">N</span></span></a>
            <a>방명록<span class="cnt">11101<span class="nb">N</span></span></a>
          </div>
        </div>
      </div>"""

EXTRA_CSS = """
  /* v4: 우측 메뉴 그리드 */
  .header2{display:flex;gap:12px;align-items:flex-start;margin:2px 0}
  .todaystory{flex:1;font-size:11px;color:#5a7d92;line-height:1.8}
  .todaystory .t{color:#2f9fd0;font-weight:bold;font-size:12px}
  .menucard{width:312px;flex:none;border:1px solid #cfe6f2;border-radius:8px;background:#f4fbff;padding:6px 9px}
  .menucard .bgm-h{font-size:11px;color:#2f7fb0;font-weight:bold;border-bottom:1px solid #d6e9f3;
                   padding-bottom:3px;margin-bottom:4px}
  .menugrid{display:grid;grid-template-columns:1fr 1fr;gap:0 14px}
  .menugrid a{display:flex;justify-content:space-between;align-items:center;font-size:12px;color:#2f6f93;
              text-decoration:none;padding:3px 0;border-bottom:1px dotted #dcebf3;cursor:pointer}
  .menugrid .cnt{color:#e0563c;font-size:10px}
  .menugrid .nb{background:#f3a03a;color:#fff;font-size:9px;border-radius:3px;padding:0 3px;margin-left:3px}
"""

# v3 페이지를 가져와 (1) CSS 추가 (2) 단순 가로 메뉴를 메뉴 그리드로 교체
from server.web import app_v3  # noqa: E402

MENU_ROW_OLD = """      <div class="menu-row">
        <a class="on">홈</a><a>프로필</a><a>다이어리 <b>12</b></a>
        <a>사진첩 <b>34</b></a><a>방명록</a>
      </div>"""

PAGE_V4 = (app_v3.PAGE_V3
           .replace("</style>", EXTRA_CSS + "</style>")
           .replace(MENU_ROW_OLD, MENU_GRID))


class HandlerV4(base.Handler):
    def do_GET(self):
        if urlparse(self.path).path == "/":
            return self._send(200, PAGE_V4, "text/html")
        return super().do_GET()


def main(port=8003):
    base._seed()
    srv = ThreadingHTTPServer(("127.0.0.1", port), HandlerV4)
    print(f"미니홈피 v4 (우측 메뉴 그리드 반영): http://localhost:{port}  (Ctrl+C 종료)")
    srv.serve_forever()


if __name__ == "__main__":
    main()
