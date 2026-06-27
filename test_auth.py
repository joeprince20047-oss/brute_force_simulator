"""
Unit Tests — Auth Guard (Lockout & Rate Limiting)
"""

import time
import pytest
from src.target.auth import AuthGuard


@pytest.fixture
def guard():
    return AuthGuard(max_attempts=3, lockout_seconds=2)


def test_no_lockout_initially(guard):
    assert guard.is_locked("192.168.1.1") is False


def test_lockout_after_max_attempts(guard):
    for _ in range(3):
        guard.record_fail("10.0.0.1")
    assert guard.is_locked("10.0.0.1") is True


def test_lockout_expires(guard):
    for _ in range(3):
        guard.record_fail("10.0.0.2")
    assert guard.is_locked("10.0.0.2") is True
    time.sleep(2.1)
    assert guard.is_locked("10.0.0.2") is False


def test_reset_clears_lockout(guard):
    for _ in range(3):
        guard.record_fail("10.0.0.3")
    assert guard.is_locked("10.0.0.3") is True
    guard.reset("10.0.0.3")
    assert guard.is_locked("10.0.0.3") is False


def test_different_ips_are_independent(guard):
    for _ in range(3):
        guard.record_fail("10.0.0.4")
    assert guard.is_locked("10.0.0.4") is True
    assert guard.is_locked("10.0.0.5") is False


def test_attempt_count_tracked(guard):
    guard.record_fail("10.0.0.6")
    guard.record_fail("10.0.0.6")
    assert guard.get_attempts("10.0.0.6") == 2
