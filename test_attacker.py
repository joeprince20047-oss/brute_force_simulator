"""
Unit Tests — Attack Engine
"""

import pytest
from unittest.mock import patch, MagicMock
from src.engine.config   import Config
from src.engine.attacker import BruteForceAttacker
from src.engine.reporter import Reporter


@pytest.fixture
def basic_config():
    return Config(
        target="http://127.0.0.1:5000/login",
        wordlist="wordlists/common_passwords.txt",
        mode="dictionary",
        threads=2,
        dry_run=True,
    )


def test_config_valid(basic_config):
    assert basic_config.threads == 2
    assert basic_config.mode == "dictionary"
    assert basic_config.dry_run is True


def test_config_invalid_mode():
    with pytest.raises(ValueError, match="Invalid mode"):
        Config(target="http://127.0.0.1:5000/login", mode="hack")


def test_config_invalid_threads():
    with pytest.raises(ValueError, match="Threads"):
        Config(target="http://127.0.0.1:5000/login", threads=0)


def test_attacker_dry_run(basic_config, tmp_path):
    # Create a small wordlist
    wl = tmp_path / "words.txt"
    wl.write_text("password\nadmin\n123456\n")
    basic_config.wordlist = str(wl)

    reporter = Reporter()
    attacker = BruteForceAttacker(basic_config, reporter)
    attacker.run()

    assert reporter.attempts == 3
    assert len(reporter.results) == 0


def test_is_success_on_welcome():
    config   = Config(target="http://127.0.0.1:5000/login", dry_run=True)
    reporter = Reporter()
    attacker = BruteForceAttacker(config, reporter)

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = "Welcome, admin!"
    assert attacker._is_success(mock_resp) is True


def test_is_success_fails_on_invalid():
    config   = Config(target="http://127.0.0.1:5000/login", dry_run=True)
    reporter = Reporter()
    attacker = BruteForceAttacker(config, reporter)

    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Invalid credentials"
    assert attacker._is_success(mock_resp) is False


def test_reporter_logs_success():
    reporter = Reporter()
    reporter.log_success("admin", "secret123")
    assert len(reporter.results) == 1
    assert reporter.results[0]["username"] == "admin"
    assert reporter.results[0]["password"] == "secret123"


def test_reporter_summary():
    reporter = Reporter()
    reporter.log_attempt()
    reporter.log_attempt()
    reporter.log_failure()
    s = reporter.summary()
    assert s["total_attempts"] == 2
    assert s["failures"] == 1
