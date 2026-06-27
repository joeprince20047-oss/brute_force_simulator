"""
Brute Force Simulator - Entry Point
=====================================
ETHICAL USE ONLY: Run exclusively against the included localhost
Flask server or systems you explicitly own. Never target real websites.
"""

import argparse
import sys
from src.engine.config import Config
from src.engine.attacker import BruteForceAttacker


def parse_args():
    parser = argparse.ArgumentParser(
        description="Brute Force Simulator - Educational Cybersecurity Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dictionary attack (default)
  python main.py --target http://127.0.0.1:5000/login --wordlist wordlists/common_passwords.txt

  # Pure brute force with custom charset
  python main.py --target http://127.0.0.1:5000/login --mode bruteforce --max-length 4

  # Multi-threaded with delay
  python main.py --target http://127.0.0.1:5000/login --wordlist wordlists/common_passwords.txt --threads 10 --delay 0.1

  # Dry run (no real requests sent)
  python main.py --target http://127.0.0.1:5000/login --wordlist wordlists/common_passwords.txt --dry-run

Start the target server first:
  python -m src.target.server
        """,
    )

    parser.add_argument("--target",     required=True,  help="Target login URL (localhost only!)")
    parser.add_argument("--wordlist",   default=None,   help="Path to password wordlist file")
    parser.add_argument("--username",   default="admin",help="Username to attack (default: admin)")
    parser.add_argument("--mode",       default="dictionary",
                        choices=["dictionary", "bruteforce", "stuffing"],
                        help="Attack mode (default: dictionary)")
    parser.add_argument("--threads",    type=int,   default=5,   help="Number of threads (default: 5)")
    parser.add_argument("--delay",      type=float, default=0.0, help="Delay between attempts in seconds")
    parser.add_argument("--max-length", type=int,   default=4,   help="Max password length for bruteforce mode")
    parser.add_argument("--timeout",    type=int,   default=5,   help="HTTP request timeout in seconds")
    parser.add_argument("--dry-run",    action="store_true",     help="Preview without sending real requests")
    parser.add_argument("--gui",        action="store_true",     help="Launch Tkinter dashboard GUI")

    return parser.parse_args()


def main():
    args = parse_args()

    # Safety check: warn if target is not localhost
    if "127.0.0.1" not in args.target and "localhost" not in args.target:
        print("\n[!] WARNING: Target does not appear to be localhost.")
        print("[!] This tool is for EDUCATIONAL USE ONLY on systems you own.")
        confirm = input("[?] Continue? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("[*] Aborted.")
            sys.exit(0)

    if args.mode == "dictionary" and not args.wordlist:
        print("[!] --wordlist is required for dictionary mode.")
        sys.exit(1)

    config = Config(
        target=args.target,
        wordlist=args.wordlist,
        username=args.username,
        mode=args.mode,
        threads=args.threads,
        delay=args.delay,
        max_length=args.max_length,
        timeout=args.timeout,
        dry_run=args.dry_run,
    )

    if args.gui:
        from src.gui.dashboard import launch_dashboard
        launch_dashboard(config)
    else:
        attacker = BruteForceAttacker(config)
        attacker.run()


if __name__ == "__main__":
    main()
