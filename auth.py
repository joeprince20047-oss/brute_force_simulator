"""
Auth Guard
-----------
Simulates real-world account lockout and rate-limiting
defences against brute force attacks.
"""

import time
import threading


class AuthGuard:
    def __init__(self, max_attempts: int = 5, lockout_seconds: int = 30):
        self.max_attempts    = max_attempts
        self.lockout_seconds = lockout_seconds
        self._attempts: dict       = {}   # ip -> attempt count
        self._locked_until: dict   = {}   # ip -> lockout expiry timestamp
        self._lock = threading.Lock()

    def is_locked(self, ip: str) -> bool:
        with self._lock:
            if ip in self._locked_until:
                if time.time() < self._locked_until[ip]:
                    remaining = round(self._locked_until[ip] - time.time(), 1)
                    print(f"[AUTH] {ip} is locked out for {remaining}s more.")
                    return True
                else:
                    # Lockout expired — reset
                    del self._locked_until[ip]
                    self._attempts[ip] = 0
            return False

    def record_fail(self, ip: str):
        with self._lock:
            self._attempts[ip] = self._attempts.get(ip, 0) + 1
            count = self._attempts[ip]
            print(f"[AUTH] {ip} failed attempt #{count}/{self.max_attempts}")
            if count >= self.max_attempts:
                self._locked_until[ip] = time.time() + self.lockout_seconds
                print(f"[AUTH] {ip} locked out for {self.lockout_seconds}s")

    def reset(self, ip: str):
        with self._lock:
            self._attempts.pop(ip, None)
            self._locked_until.pop(ip, None)

    def get_attempts(self, ip: str) -> int:
        return self._attempts.get(ip, 0)

    def status(self, ip: str) -> dict:
        return {
            "ip":          ip,
            "attempts":    self._attempts.get(ip, 0),
            "locked":      self.is_locked(ip),
            "max_allowed": self.max_attempts,
        }
