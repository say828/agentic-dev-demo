# -*- coding: utf-8 -*-
"""pytest 픽스처 + 패키지 경로. 결정적: 인메모리 서비스, 실시간·난수 비의존."""
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from server.contexts.buddybuddy.buddy import BuddyService  # noqa: E402
from server.contexts.buddybuddy.message import MessageService  # noqa: E402
from server.contexts.buddybuddy.presence import PresenceService  # noqa: E402


@pytest.fixture
def presence():
    return PresenceService()


@pytest.fixture
def buddy():
    return BuddyService()


@pytest.fixture
def message():
    return MessageService()
