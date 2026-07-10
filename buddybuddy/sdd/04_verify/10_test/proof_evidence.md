# 증거 캡처 (04_verify / 10_test)

## pytest
```
$ python -m pytest -q
...................                                                      [100%]
19 passed in 0.07s
```

## 라이브 송수신 (python tmp/smoke.py, 서버 localhost:8010)
```
1) 현주 sends: {'seq': 3, 'frm': '현주', 'to': '민수', 'text': '민수야 테스트중 ㅋㅋ', 'replay': False}
2) 민수 unread badge: [{'name': '현주', 'status': 'online', 'unread': 2}]
3) 민수 replies: {'seq': 4, 'frm': '민수', 'to': '현주', 'text': '오 도착했어!', 'replay': False}
4) resend t1 (idempotent): {'seq': 3, 'frm': '현주', 'to': '민수', 'text': '민수야 테스트중 ㅋㅋ', 'replay': True}
5) thread (양쪽 동일), count=4:
    seq1 현주 -> 민수 : 민수야 접속했어? 🐤
    seq2 민수 -> 현주 : 어 현주야! 방가방가~
    seq3 현주 -> 민수 : 민수야 테스트중 ㅋㅋ
    seq4 민수 -> 현주 : 오 도착했어!
6) 민수 reads -> mark_read: {'read': 2}
7) 민수 unread after read: [{'name': '현주', 'status': 'online', 'unread': 0}]
8) isolation 현주<->철수: []
```

## 해석
- (1)(3)(5) 송수신·순번·양방향 동일 대화 = AC-3.
- (4) 동일 client_msg_id 재전송 → `replay: True`, seq 그대로 3, 대화 4건 유지 = AC-4(중복 미기록).
- (2)(6)(7) 안읽음 2 → 읽음 2 → 안읽음 0 = AC-5.
- (8) 다른 상대 대화는 빈 배열 = AC-6(대화 격리).

## 두 프론트 라우팅·자동 인식 (python tmp/smoke2.py)
```
1) 로비에 '로그인' 있나: True
   현주 클라이언트에 ME=현주 박혔나: True
   데모 페이지 stage 있나: True
2) 지우 login: {'user': '지우', 'status': 'online'}
   지우→현주 send: {'seq': 3, 'frm': '지우', 'to': '현주', 'text': '현주야 나 지우야!', 'replay': False}
3) 현주의 대화 목록: ['민수', '지우'] → 지우 자동 포함: True
4) 지우↔현주 대화:
    지우 -> 현주 : 현주야 나 지우야!
    현주 -> 지우 : 오 지우야 안녕!
```
- (1) `/` 로비 / `/?me=현주` 단일 클라이언트(ME 주입) / `/demo` 라우팅 정상 = AC-7.
- (2)(3) 버디로 추가 안 한 '지우'가 메시지를 보내자 현주의 대화 목록에 자동 노출(partners 병합) = AC-7.
- (4) 두 프론트(지우 창 / 현주 창)가 같은 서버로 주고받음 = AC-7 핵심("두 프론트에서 대화").
