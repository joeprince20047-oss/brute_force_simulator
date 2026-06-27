"""
Wordlist Loader & Brute Force Generator
-----------------------------------------
- WordlistLoader  : reads passwords line-by-line from a file (memory-efficient)
- BruteForceGen   : generates all character combinations up to max_length
- StuffingLoader  : reads user:pass pairs from a credential dump file
"""

import itertools
from pathlib import Path


class WordlistLoader:
    """Load passwords from a text file, one per line."""

    def __init__(self, path: str):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"Wordlist not found: {self.path}")

    def load(self):
        """Yield passwords one at a time (memory-efficient generator)."""
        with open(self.path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                password = line.strip()
                if password:
                    yield password

    def count(self) -> int:
        """Return total number of passwords in the wordlist."""
        return sum(1 for _ in self.load())


class BruteForceGen:
    """Generate all possible character combinations up to max_length."""

    def __init__(self, charset: str = "abcdefghijklmnopqrstuvwxyz0123456789", max_length: int = 4):
        self.charset    = charset
        self.max_length = max_length

    def generate(self):
        """Yield every combination from length 1 up to max_length."""
        for length in range(1, self.max_length + 1):
            for combo in itertools.product(self.charset, repeat=length):
                yield "".join(combo)

    def total_combinations(self) -> int:
        """Calculate total number of combinations (for progress tracking)."""
        n = len(self.charset)
        return sum(n ** i for i in range(1, self.max_length + 1))


class StuffingLoader:
    """Load username:password credential pairs from a dump file."""

    def __init__(self, path: str):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"Credential file not found: {self.path}")

    def load(self):
        """Yield (username, password) tuples."""
        with open(self.path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if ":" in line:
                    username, _, password = line.partition(":")
                    yield username.strip(), password.strip()
