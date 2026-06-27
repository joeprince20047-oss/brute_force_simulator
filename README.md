# ⚡ Brute Force Simulator

> **Educational cybersecurity tool** — Internship Project  
> Python 3.11 · Flask · Tkinter · pytest · GitHub Actions

![CI](https://github.com/YOUR_USERNAME/brute-force-simulator/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ⚠️ Ethical Use Disclaimer

This tool is built **exclusively for educational purposes**, internship demonstration,
and authorized penetration testing on systems you own.

**Never use this against real websites, cloud services, or any system without written permission.**

---

## Features

- **3 Attack Modes** — Dictionary, Pure Brute Force, Credential Stuffing
- **Multithreaded Engine** — configurable thread pool (1–50 threads)
- **Local Sandbox Server** — Flask login target with lockout simulation
- **Live GUI Dashboard** — Tkinter real-time stats viewer
- **Auto Reporter** — saves results to CSV and JSON in `logs/`
- **Dry Run Mode** — preview attacks without sending real requests
- **GitHub Actions CI** — pytest runs on every push

---

## Project Structure

```
brute_force_simulator/
├── main.py                        # CLI entry point
├── src/
│   ├── engine/
│   │   ├── attacker.py            # Core attack engine + threading
│   │   ├── wordlist.py            # Wordlist loader & brute force generator
│   │   ├── reporter.py            # Results logger (CSV + JSON)
│   │   └── config.py              # Settings dataclass
│   ├── target/
│   │   ├── server.py              # Flask sandbox login server
│   │   ├── auth.py                # Lockout & rate-limit guard
│   │   └── templates/login.html
│   └── gui/
│       └── dashboard.py           # Tkinter live dashboard
├── tests/                         # pytest test suite
├── wordlists/
│   └── common_passwords.txt
├── .github/workflows/             # CI/CD pipelines
│   ├── ci.yml
│   └── release.yml
├── docs/architecture.md
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/brute-force-simulator.git
cd brute-force-simulator
pip install -r requirements.txt
```

### 2. Start the Sandbox Target Server

```bash
# Terminal 1
python -m src.target.server
# → Running at http://127.0.0.1:5000/login
```

### 3. Run the Simulator

```bash
# Terminal 2 — Dictionary attack
python main.py \
  --target http://127.0.0.1:5000/login \
  --wordlist wordlists/common_passwords.txt \
  --username admin \
  --threads 5

# Pure brute force (all combos up to 4 chars)
python main.py \
  --target http://127.0.0.1:5000/login \
  --mode bruteforce \
  --max-length 4

# With GUI dashboard
python main.py \
  --target http://127.0.0.1:5000/login \
  --wordlist wordlists/common_passwords.txt \
  --gui

# Dry run (no real requests)
python main.py \
  --target http://127.0.0.1:5000/login \
  --wordlist wordlists/common_passwords.txt \
  --dry-run
```

---

## CLI Options

| Flag | Default | Description |
|---|---|---|
| `--target` | required | Target login URL |
| `--wordlist` | — | Path to password file |
| `--username` | admin | Username to attack |
| `--mode` | dictionary | dictionary / bruteforce / stuffing |
| `--threads` | 5 | Worker threads (1–50) |
| `--delay` | 0.0 | Seconds between attempts |
| `--max-length` | 4 | Max length for bruteforce mode |
| `--timeout` | 5 | HTTP timeout in seconds |
| `--dry-run` | false | Preview without real requests |
| `--gui` | false | Launch Tkinter dashboard |

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Demo Credentials (sandbox only)

| Username | Password |
|---|---|
| admin | secret123 |
| user | password1 |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| Web Server | Flask 3.x |
| HTTP Client | requests |
| GUI | Tkinter |
| Testing | pytest |
| CI/CD | GitHub Actions |

---

## License

MIT © 2025 Prince
