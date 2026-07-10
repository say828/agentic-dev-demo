# -*- coding: utf-8 -*-
"""미니홈피 웹 프론트 v5 — 페이지 가장 오른쪽 '세로 탭 레일'을 반영.

배경(원인): v3/v4는 화면 오른쪽 끝을 '별도 창(3D 타워)'으로 보고 통째로 제외했는데,
그 타워 왼쪽에는 페이지에 속한 세로 탭 레일(홈·프로필·다이어리·쥬크박스·미니룸·사진첩·
갤러리·게시판·방명록)이 따로 있었다. 즉 영역 경계를 잘못 그어 페이지 소속 탭까지 버렸다.
v5는 그 영역을 확대해 타워(별도 창)와 세로 탭(페이지 소속)을 구분하고, 탭 레일만 반영.

도메인·API·JS·나머지 배치는 v4를 그대로 두고, 가장 오른쪽 세로 탭 레일만 추가.

실행:  python3 -m server.web.app_v5   # → http://localhost:8004
"""
from http.server import ThreadingHTTPServer
from urllib.parse import urlparse

from server.web import app as base
from server.web import app_v4

TABRAIL = """    <div class="tabrail">
      <a class="on">홈</a><a>프로필</a><a>다이어리</a><a>쥬크박스</a><a>미니룸</a>
      <a>사진첩</a><a>갤러리</a><a>게시판</a><a>방명록</a>
    </div>
"""

TABRAIL_CSS = """
  /* v5: 가장 오른쪽 세로 탭 레일 */
  .hp{align-items:flex-start}
  .tabrail{width:50px;flex:none;display:flex;flex-direction:column;gap:5px;padding-top:44px;margin-left:-2px}
  .tabrail a{font-size:11px;color:#fff;background:#5aa6d6;border:1px solid #4a90c0;border-right:none;
             border-radius:8px 0 0 8px;padding:7px 0;text-align:center;text-decoration:none;cursor:pointer;
             box-shadow:-1px 1px 2px #0001}
  .tabrail a.on{background:#fff;color:#15557e;font-weight:bold;border-color:#8fc6e6}
"""

# v4 페이지를 가져와 (1) CSS 추가 (2) .hp 닫기 직전에 세로 탭 레일 삽입
PAGE_V5 = (app_v4.PAGE_V4
           .replace("</style>", TABRAIL_CSS + "</style>")
           .replace("  </div>\n<script>", TABRAIL + "  </div>\n<script>"))


class HandlerV5(base.Handler):
    def do_GET(self):
        if urlparse(self.path).path == "/":
            return self._send(200, PAGE_V5, "text/html")
        return super().do_GET()


def main(port=8004):
    base._seed()
    srv = ThreadingHTTPServer(("127.0.0.1", port), HandlerV5)
    print(f"미니홈피 v5 (세로 탭 레일 반영): http://localhost:{port}  (Ctrl+C 종료)")
    srv.serve_forever()


if __name__ == "__main__":
    main()
