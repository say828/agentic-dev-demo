package kr.elice.buddybuddy.web;

import java.util.Set;

/**
 * HTML 페이지 렌더: 로비 / 단일 클라이언트 / 데모(두 패널).
 * Python server/web/app.py 의 HTML/CSS/JS 포트 — 1초 폴링으로 두 창이 대화한다.
 */
public final class Pages {

    private Pages() {
    }

    /** 공통 스타일 + 마스코트. 버디버디 레트로 메신저 룩앤필. */
    private static final String CSS =
            "<style>"
            + "*{box-sizing:border-box;font-family:'Malgun Gothic','맑은 고딕',Tahoma,sans-serif}"
            + "body{margin:0;background:#cfe3f7;color:#173049}"
            + ".wrap{max-width:760px;margin:24px auto;padding:0 12px}"
            + "h1{font-size:20px}"
            + ".win{border:1px solid #2b5d97;border-radius:8px;overflow:hidden;"
            + "box-shadow:0 6px 22px rgba(0,0,0,.18);background:#fff;margin:10px 0}"
            + ".win-title{display:flex;align-items:center;gap:6px;"
            + "background:linear-gradient(#4d9be6,#2b6fc2);color:#fff;padding:6px 10px;font-weight:bold}"
            + ".win-name{flex:1}"
            + ".win-btns i{display:inline-block;width:18px;height:16px;line-height:16px;"
            + "text-align:center;background:#e7f0fb;color:#234;margin-left:3px;border-radius:3px;"
            + "font-style:normal;font-size:11px}"
            + ".win-body{padding:10px}"
            + ".mascot{vertical-align:middle}"
            + ".buddy{display:flex;align-items:center;gap:8px;padding:7px 9px;border-radius:6px;"
            + "cursor:pointer}"
            + ".buddy:hover{background:#eef5ff}"
            + ".buddy.active{background:#dcebff}"
            + ".dot{width:9px;height:9px;border-radius:50%;background:#bbb}"
            + ".dot.on{background:#43c463}"
            + ".badge{margin-left:auto;background:#ff4d4f;color:#fff;border-radius:10px;"
            + "padding:0 7px;font-size:12px;min-width:18px;text-align:center}"
            + ".chat{height:300px;overflow:auto;background:#f4f8ff;border:1px solid #cfe0f5;"
            + "border-radius:6px;padding:8px;margin:8px 0}"
            + ".msg{margin:4px 0;display:flex}"
            + ".msg .bub{padding:6px 10px;border-radius:12px;max-width:72%;white-space:pre-wrap}"
            + ".msg.me{justify-content:flex-end}"
            + ".msg.me .bub{background:#ffe14d}"
            + ".msg.them .bub{background:#fff;border:1px solid #d8e6f7}"
            + ".row{display:flex;gap:6px}"
            + "input,button{font-size:14px;padding:7px 9px;border-radius:6px;border:1px solid #9bbbe0}"
            + "input{flex:1}"
            + "button{background:#2b6fc2;color:#fff;cursor:pointer;border-color:#2b6fc2}"
            + "button:hover{background:#2360ab}"
            + ".muted{color:#5a7493;font-size:13px}"
            + ".stage{display:flex;gap:14px;flex-wrap:wrap}"
            + ".stage .panel{flex:1;min-width:320px}"
            + "a{color:#2b6fc2}"
            + "</style>";

    // ------------------------------------------------------------------
    // 로비
    // ------------------------------------------------------------------

    public static String lobby(Set<String> online) {
        StringBuilder list = new StringBuilder();
        if (online.isEmpty()) {
            list.append("<p class=\"muted\">접속 중인 사용자가 없습니다.</p>");
        } else {
            for (String u : online) {
                String enc = url(u);
                list.append("<div class=\"buddy\"><span class=\"dot on\"></span>")
                        .append("<a href=\"/?me=").append(enc).append("\">")
                        .append(esc(u)).append("</a></div>");
            }
        }
        String body =
                "<p class=\"muted\">이름으로 로그인해서 메신저 창을 여세요. "
                + "두 창(<code>/?me=현주</code>, <code>/?me=민수</code>)을 띄우면 서로 대화합니다.</p>"
                + "<div class=\"row\"><input id=\"name\" placeholder=\"이름 (예: 현주)\"/>"
                + "<button onclick=\"go()\">로그인</button></div>"
                + "<h3>접속 중</h3>" + list
                + "<p class=\"muted\"><a href=\"/demo\">▶ 두 패널 데모 보기</a></p>";
        String script =
                "<script>"
                + "function go(){var n=document.getElementById('name').value.trim();"
                + "if(n) location.href='/?me='+encodeURIComponent(n);}"
                + "document.getElementById('name').addEventListener('keydown',"
                + "function(e){if(e.key==='Enter')go();});"
                + "</script>";
        return page("버디버디 메신저 — 로비",
                "<div class=\"wrap\">"
                + Screens.windowChrome("버디버디 — 로비", body)
                + "</div>" + script);
    }

    // ------------------------------------------------------------------
    // 단일 클라이언트 (?me=현주)
    // ------------------------------------------------------------------

    public static String client(String me) {
        String body =
                "<div class=\"row\"><input id=\"add\" placeholder=\"버디 추가 (이름)\"/>"
                + "<button onclick=\"addBuddy()\">추가</button></div>"
                + "<h3 class=\"muted\">버디</h3>"
                + "<div id=\"buddies\"></div>"
                + "<hr/>"
                + "<div id=\"talking\" class=\"muted\">대화할 버디를 선택하세요.</div>"
                + "<div id=\"chat\" class=\"chat\"></div>"
                + "<div class=\"row\"><input id=\"text\" placeholder=\"메시지 입력...\"/>"
                + "<button onclick=\"send()\">전송</button></div>";
        // ME 를 JS 에 박는다. 스모크 테스트: const ME = "현주"
        String script =
                "<script>\n"
                + "const ME = \"" + jsStr(me) + "\";\n"
                + "let peer = null;\n"
                + "let cid = 0;\n"
                + "async function jget(u){const r=await fetch(u);return r.json();}\n"
                + "async function jpost(u,d){const r=await fetch(u,{method:'POST',"
                + "headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});"
                + "return r.json();}\n"
                + "function pick(name){peer=name;document.getElementById('talking')."
                + "textContent=name+' 님과 대화 중';read();refresh();}\n"
                + "async function addBuddy(){const v=document.getElementById('add').value.trim();"
                + "if(!v)return;await jpost('/api/buddy_add',{owner:ME,buddy:v});"
                + "document.getElementById('add').value='';refresh();}\n"
                + "async function send(){const t=document.getElementById('text').value;"
                + "if(!t.trim()||!peer)return;cid++;"
                + "await jpost('/api/send',{frm:ME,to:peer,text:t,"
                + "client_msg_id:ME+'-'+Date.now()+'-'+cid});"
                + "document.getElementById('text').value='';refresh();}\n"
                + "async function read(){if(peer)await jpost('/api/read',{reader:ME,other:peer});}\n"
                + "async function refresh(){\n"
                + " const st=await jget('/api/state?me='+encodeURIComponent(ME));\n"
                + " const box=document.getElementById('buddies');box.innerHTML='';\n"
                + " (st.buddies||[]).forEach(function(b){\n"
                + "  const d=document.createElement('div');"
                + "d.className='buddy'+(b.name===peer?' active':'');\n"
                + "  d.onclick=function(){pick(b.name);};\n"
                + "  let h='<span class=\"dot'+(b.online?' on':'')+'\"></span><span>'+b.name+'</span>';\n"
                + "  if(b.unread>0)h+='<span class=\"badge\">'+b.unread+'</span>';\n"
                + "  d.innerHTML=h;box.appendChild(d);});\n"
                + " if(peer){\n"
                + "  const th=await jget('/api/thread?a='+encodeURIComponent(ME)+"
                + "'&b='+encodeURIComponent(peer));\n"
                + "  const c=document.getElementById('chat');c.innerHTML='';\n"
                + "  th.forEach(function(m){\n"
                + "   const row=document.createElement('div');"
                + "row.className='msg '+(m.frm===ME?'me':'them');\n"
                + "   const bub=document.createElement('div');bub.className='bub';bub.textContent=m.text;\n"
                + "   row.appendChild(bub);c.appendChild(row);});\n"
                + "  c.scrollTop=c.scrollHeight;await read();}\n"
                + "}\n"
                + "document.getElementById('text').addEventListener('keydown',"
                + "function(e){if(e.key==='Enter')send();});\n"
                + "jpost('/api/login',{user:ME}).then(refresh);\n"
                + "setInterval(refresh,1000);\n"  // 1초 폴링
                + "</script>";
        return page("버디버디 — " + esc(me),
                "<div class=\"wrap\">"
                + Screens.windowChrome(esc(me) + " 님의 메신저", body)
                + "</div>" + script);
    }

    // ------------------------------------------------------------------
    // 데모 (두 패널)
    // ------------------------------------------------------------------

    public static String demo() {
        // stage 안에 두 iframe(현주/민수)을 띄워 한 화면에서 대화를 시연한다.
        String body =
                "<p class=\"muted\">한 화면에서 두 클라이언트가 1초 폴링으로 대화합니다.</p>"
                + "<div id=\"stage\" class=\"stage\">"
                + "<div class=\"panel\"><iframe src=\"/?me=" + url("현주")
                + "\" style=\"width:100%;height:560px;border:0\"></iframe></div>"
                + "<div class=\"panel\"><iframe src=\"/?me=" + url("민수")
                + "\" style=\"width:100%;height:560px;border:0\"></iframe></div>"
                + "</div>";
        return page("버디버디 — 데모",
                "<div class=\"wrap\">"
                + Screens.windowChrome("버디버디 — 데모 (현주 ↔ 민수)", body)
                + "</div>");
    }

    // ------------------------------------------------------------------
    // 헬퍼
    // ------------------------------------------------------------------

    private static String page(String title, String body) {
        return "<!doctype html><html lang=\"ko\"><head>"
                + "<meta charset=\"utf-8\"/>"
                + "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"/>"
                + "<title>" + esc(title) + "</title>" + CSS
                + "</head><body>" + body + "</body></html>";
    }

    private static String esc(String s) {
        if (s == null) {
            return "";
        }
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;");
    }

    private static String jsStr(String s) {
        if (s == null) {
            return "";
        }
        return s.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    private static String url(String s) {
        return java.net.URLEncoder.encode(s, java.nio.charset.StandardCharsets.UTF_8);
    }
}
