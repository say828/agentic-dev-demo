# -*- coding: utf-8 -*-
"""투데이: 같은 방문자·같은 날 1회 집계(멱등), 날짜 분리, TOTAL 누적."""


def test_today_counts_unique_visitor_once(today):
    r1 = today.visit("owner", "guest", "2026-06-08")
    r2 = today.visit("owner", "guest", "2026-06-08")  # 같은 날 재방문
    assert r1["replay"] is False and r2["replay"] is True
    assert today.today_count("owner", "2026-06-08") == 1


def test_today_distinct_visitors(today):
    today.visit("owner", "g1", "2026-06-08")
    today.visit("owner", "g2", "2026-06-08")
    assert today.today_count("owner", "2026-06-08") == 2


def test_today_resets_per_day_total_accumulates(today):
    today.visit("owner", "g1", "2026-06-08")
    today.visit("owner", "g1", "2026-06-09")  # 다른 날 → 다시 집계
    assert today.today_count("owner", "2026-06-08") == 1
    assert today.today_count("owner", "2026-06-09") == 1
    assert today.total_count("owner") == 2  # 누적
