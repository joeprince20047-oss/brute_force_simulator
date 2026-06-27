"""
Tkinter Live Dashboard
-----------------------
Real-time GUI showing attack progress, stats, and found credentials.
Launch with: python main.py --target ... --wordlist ... --gui
"""

import threading
import tkinter as tk
from tkinter import ttk, scrolledtext

from src.engine.config   import Config
from src.engine.attacker import BruteForceAttacker
from src.engine.reporter import Reporter


class Dashboard(tk.Tk):
    def __init__(self, config: Config, reporter: Reporter, attacker: BruteForceAttacker):
        super().__init__()
        self.config   = config
        self.reporter = reporter
        self.attacker = attacker

        self.title("Brute Force Simulator — Dashboard")
        self.geometry("680x520")
        self.configure(bg="#1e1b3a")
        self.resizable(False, False)

        self._build_ui()
        self._update_stats()

    # ── UI Build ───────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg="#534AB7", pady=12)
        header.pack(fill="x")
        tk.Label(header, text="⚡  Brute Force Simulator",
                 font=("Helvetica", 16, "bold"), fg="white", bg="#534AB7").pack()
        tk.Label(header, text=f"Target: {self.config.target}  |  Mode: {self.config.mode}  |  Threads: {self.config.threads}",
                 font=("Helvetica", 9), fg="#c4c0f0", bg="#534AB7").pack()

        # Stats row
        stats_frame = tk.Frame(self, bg="#2d2a50", pady=10)
        stats_frame.pack(fill="x", padx=0)

        self.stat_vars = {
            "Attempts":   tk.StringVar(value="0"),
            "Failures":   tk.StringVar(value="0"),
            "Rate Limits":tk.StringVar(value="0"),
            "Found":      tk.StringVar(value="0"),
            "Speed":      tk.StringVar(value="0/s"),
            "Elapsed":    tk.StringVar(value="0s"),
        }

        for i, (label, var) in enumerate(self.stat_vars.items()):
            col = tk.Frame(stats_frame, bg="#2d2a50", padx=18)
            col.grid(row=0, column=i, sticky="nsew")
            tk.Label(col, textvariable=var, font=("Helvetica", 18, "bold"),
                     fg="#a89fff", bg="#2d2a50").pack()
            tk.Label(col, text=label, font=("Helvetica", 9),
                     fg="#7e7aaa", bg="#2d2a50").pack()

        stats_frame.columnconfigure(list(range(len(self.stat_vars))), weight=1)

        # Progress bar
        prog_frame = tk.Frame(self, bg="#1e1b3a", pady=8)
        prog_frame.pack(fill="x", padx=20)
        tk.Label(prog_frame, text="Progress", font=("Helvetica", 9),
                 fg="#7e7aaa", bg="#1e1b3a").pack(anchor="w")
        self.progress = ttk.Progressbar(prog_frame, mode="indeterminate", length=640)
        self.progress.pack(fill="x")
        self.progress.start(12)

        # Log area
        log_frame = tk.Frame(self, bg="#1e1b3a", pady=4)
        log_frame.pack(fill="both", expand=True, padx=20, pady=(0, 8))
        tk.Label(log_frame, text="Live Log", font=("Helvetica", 9, "bold"),
                 fg="#c4c0f0", bg="#1e1b3a").pack(anchor="w")

        self.log_box = scrolledtext.ScrolledText(
            log_frame, bg="#12102e", fg="#a8f5a0",
            font=("Courier", 9), state="disabled",
            relief="flat", bd=0, height=12,
        )
        self.log_box.pack(fill="both", expand=True)

        # Found credentials area
        found_frame = tk.Frame(self, bg="#1e1b3a", pady=4)
        found_frame.pack(fill="x", padx=20, pady=(0, 14))
        tk.Label(found_frame, text="Found Credentials", font=("Helvetica", 9, "bold"),
                 fg="#f5a0a0", bg="#1e1b3a").pack(anchor="w")
        self.found_box = scrolledtext.ScrolledText(
            found_frame, bg="#2e1212", fg="#ffb3b3",
            font=("Courier", 9), state="disabled",
            relief="flat", bd=0, height=3,
        )
        self.found_box.pack(fill="x")

    # ── Stat Updates ──────────────────────────────────────────────────────────

    def _update_stats(self):
        r = self.reporter
        self.stat_vars["Attempts"].set(str(r.attempts))
        self.stat_vars["Failures"].set(str(r.failures))
        self.stat_vars["Rate Limits"].set(str(r.rate_limited))
        self.stat_vars["Found"].set(str(len(r.results)))
        self.stat_vars["Speed"].set(f"{r.attempts_per_second()}/s")
        self.stat_vars["Elapsed"].set(f"{r.elapsed()}s")

        # Write new found credentials
        if r.results:
            self.found_box.configure(state="normal")
            self.found_box.delete("1.0", "end")
            for cred in r.results:
                self.found_box.insert("end", f"  ✓  {cred['username']} : {cred['password']}\n")
            self.found_box.configure(state="disabled")

        if r.attempts > 0:
            self._append_log(f"Attempts: {r.attempts}  |  Speed: {r.attempts_per_second()}/s")

        if not self.attacker.found.is_set():
            self.after(500, self._update_stats)
        else:
            self.progress.stop()
            self._append_log("\n[*] Attack complete.")

    def _append_log(self, text: str):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")


def launch_dashboard(config: Config):
    reporter = Reporter()
    attacker = BruteForceAttacker(config, reporter)

    attack_thread = threading.Thread(target=attacker.run, daemon=True)
    attack_thread.start()

    app = Dashboard(config, reporter, attacker)
    app.mainloop()
