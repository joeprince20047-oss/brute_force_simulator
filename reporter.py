"""
Reporter
---------
Logs discovered credentials, tracks attempt stats,
and saves results to CSV and JSON in the logs/ directory.
"""

import csv
import json
import time
import threading
from pathlib import Path


class Reporter:
    def __init__(self):
        self.results       = []
        self.attempts      = 0
        self.failures      = 0
        self.rate_limited  = 0
        self.start_time    = time.time()
        self._lock         = threading.Lock()
        Path("logs").mkdir(exist_ok=True)

    # ── Recording ──────────────────────────────────────────────────────────────

    def log_success(self, username: str, password: str):
        with self._lock:
            self.results.append({
                "username":  username,
                "password":  password,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "elapsed":   round(time.time() - self.start_time, 2),
            })
            print(f"\n{'='*50}")
            print(f"  [+] FOUND  →  {username} : {password}")
            print(f"{'='*50}\n")

    def log_attempt(self):
        with self._lock:
            self.attempts += 1

    def log_failure(self):
        with self._lock:
            self.failures += 1

    def log_rate_limited(self):
        with self._lock:
            self.rate_limited += 1

    # ── Stats ──────────────────────────────────────────────────────────────────

    def elapsed(self) -> float:
        return round(time.time() - self.start_time, 2)

    def attempts_per_second(self) -> float:
        elapsed = time.time() - self.start_time
        return round(self.attempts / elapsed, 2) if elapsed > 0 else 0.0

    def summary(self) -> dict:
        return {
            "total_attempts":   self.attempts,
            "failures":         self.failures,
            "rate_limits_hit":  self.rate_limited,
            "credentials_found": len(self.results),
            "elapsed_seconds":  self.elapsed(),
            "attempts_per_sec": self.attempts_per_second(),
        }

    def print_summary(self):
        s = self.summary()
        print("\n" + "─" * 50)
        print("  ATTACK SUMMARY")
        print("─" * 50)
        print(f"  Total attempts   : {s['total_attempts']}")
        print(f"  Failures         : {s['failures']}")
        print(f"  Rate limits hit  : {s['rate_limits_hit']}")
        print(f"  Credentials found: {s['credentials_found']}")
        print(f"  Time elapsed     : {s['elapsed_seconds']}s")
        print(f"  Speed            : {s['attempts_per_sec']} attempts/sec")
        print("─" * 50 + "\n")

    # ── Saving ─────────────────────────────────────────────────────────────────

    def save(self):
        if not self.results:
            print("[*] No credentials found. Nothing saved.")
            self.print_summary()
            return

        ts = time.strftime("%Y%m%d_%H%M%S")

        # CSV
        csv_path = f"logs/results_{ts}.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["username", "password", "timestamp", "elapsed"])
            writer.writeheader()
            writer.writerows(self.results)

        # JSON
        json_path = f"logs/results_{ts}.json"
        with open(json_path, "w") as f:
            json.dump({
                "summary": self.summary(),
                "credentials": self.results,
            }, f, indent=2)

        print(f"[*] Results saved → {csv_path}")
        print(f"[*] Results saved → {json_path}")
        self.print_summary()
