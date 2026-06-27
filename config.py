"""
Configuration dataclass for the Brute Force Simulator.
All runtime settings are stored here and passed between modules.
"""

from dataclasses import dataclass, field


@dataclass
class Config:
    target:     str
    username:   str   = "admin"
    wordlist:   str   = None
    mode:       str   = "dictionary"   # dictionary | bruteforce | stuffing
    threads:    int   = 5
    delay:      float = 0.0
    max_length: int   = 4
    timeout:    int   = 5
    dry_run:    bool  = False
    charset:    str   = "abcdefghijklmnopqrstuvwxyz0123456789"

    def __post_init__(self):
        valid_modes = {"dictionary", "bruteforce", "stuffing"}
        if self.mode not in valid_modes:
            raise ValueError(f"Invalid mode '{self.mode}'. Choose from {valid_modes}")
        if self.threads < 1 or self.threads > 50:
            raise ValueError("Threads must be between 1 and 50.")
        if self.delay < 0:
            raise ValueError("Delay cannot be negative.")
