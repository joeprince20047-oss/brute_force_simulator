"""
Unit Tests — Wordlist Loader & Brute Force Generator
"""

import pytest
from src.engine.wordlist import WordlistLoader, BruteForceGen, StuffingLoader


# ── WordlistLoader ─────────────────────────────────────────────────────────────

def test_wordlist_loads_correctly(tmp_path):
    wl = tmp_path / "passwords.txt"
    wl.write_text("password\nadmin\n123456\nsecret\n")
    loader = WordlistLoader(str(wl))
    results = list(loader.load())
    assert results == ["password", "admin", "123456", "secret"]


def test_wordlist_skips_empty_lines(tmp_path):
    wl = tmp_path / "passwords.txt"
    wl.write_text("password\n\n\nadmin\n")
    loader = WordlistLoader(str(wl))
    results = list(loader.load())
    assert "" not in results
    assert len(results) == 2


def test_wordlist_file_not_found():
    with pytest.raises(FileNotFoundError):
        WordlistLoader("nonexistent_file.txt")


def test_wordlist_count(tmp_path):
    wl = tmp_path / "passwords.txt"
    wl.write_text("a\nb\nc\nd\ne\n")
    loader = WordlistLoader(str(wl))
    assert loader.count() == 5


# ── BruteForceGen ─────────────────────────────────────────────────────────────

def test_bruteforce_gen_length_1():
    gen = BruteForceGen(charset="abc", max_length=1)
    results = list(gen.generate())
    assert results == ["a", "b", "c"]


def test_bruteforce_gen_length_2():
    gen = BruteForceGen(charset="ab", max_length=2)
    results = list(gen.generate())
    assert "a"  in results
    assert "b"  in results
    assert "aa" in results
    assert "ab" in results
    assert "ba" in results
    assert "bb" in results
    assert len(results) == 6  # 2^1 + 2^2


def test_bruteforce_gen_total_combinations():
    gen = BruteForceGen(charset="abc", max_length=2)
    # 3^1 + 3^2 = 3 + 9 = 12
    assert gen.total_combinations() == 12


# ── StuffingLoader ─────────────────────────────────────────────────────────────

def test_stuffing_loader(tmp_path):
    f = tmp_path / "creds.txt"
    f.write_text("admin:secret123\nuser:password1\n")
    loader = StuffingLoader(str(f))
    pairs = list(loader.load())
    assert pairs[0] == ("admin", "secret123")
    assert pairs[1] == ("user", "password1")


def test_stuffing_loader_skips_invalid_lines(tmp_path):
    f = tmp_path / "creds.txt"
    f.write_text("admin:secret123\nnocolon\nuser:pass\n")
    loader = StuffingLoader(str(f))
    pairs = list(loader.load())
    assert len(pairs) == 2


def test_stuffing_file_not_found():
    with pytest.raises(FileNotFoundError):
        StuffingLoader("no_such_file.txt")
