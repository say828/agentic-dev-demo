# -*- coding: utf-8 -*-
"""pytest 픽스처 + 패키지 경로. 결정적: 인메모리 서비스, 실시간·난수 비의존."""
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from server.contexts.cyworld.dotori import DotoriService  # noqa: E402
from server.contexts.cyworld.guestbook import GuestbookService  # noqa: E402
from server.contexts.cyworld.ilchon import IlchonService  # noqa: E402
from server.contexts.cyworld.today import TodayService  # noqa: E402


@pytest.fixture
def dotori():
    return DotoriService()


@pytest.fixture
def ilchon():
    return IlchonService()


@pytest.fixture
def today():
    return TodayService()


@pytest.fixture
def guestbook():
    return GuestbookService()
