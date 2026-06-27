"""
Sandbox Target Server
----------------------
A local Flask login server used as the ONLY safe attack target.
Run this first, then point the simulator at http://127.0.0.1:5000/login

NEVER use the simulator against real external websites.
"""

from flask import Flask, request, render_template, jsonify
from src.target.auth import AuthGuard

app   = Flask(__name__, template_folder="templates")
guard = AuthGuard(max_attempts=5, lockout_seconds=30)

# Dummy credentials — safe demo only
CREDENTIALS = {
    "admin": "secret123",
    "user":  "password1",
}


@app.route("/")
def index():
    return '<h2>Brute Force Simulator — Sandbox Server</h2><a href="/login">Go to Login</a>'


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    ip       = request.remote_addr
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if not username or not password:
        return jsonify({"error": "Missing fields"}), 400

    if guard.is_locked(ip):
        return jsonify({"error": "Too many attempts. Try again later."}), 429

    if CREDENTIALS.get(username) == password:
        guard.reset(ip)
        return jsonify({"message": f"Welcome, {username}!"}), 200

    guard.record_fail(ip)
    remaining = guard.max_attempts - guard.get_attempts(ip)
    return jsonify({
        "error":    "Invalid credentials",
        "attempts_remaining": max(0, remaining),
    }), 401


@app.route("/status")
def status():
    """Debug endpoint to check server status."""
    return jsonify({"status": "running", "users": list(CREDENTIALS.keys())}), 200


@app.route("/reset", methods=["POST"])
def reset():
    """Reset lockout for an IP (for testing)."""
    ip = request.remote_addr
    guard.reset(ip)
    return jsonify({"message": f"Lockout reset for {ip}"}), 200


if __name__ == "__main__":
    print("\n[*] Sandbox Target Server starting...")
    print("[*] URL: http://127.0.0.1:5000/login")
    print("[*] Demo credentials: admin:secret123  |  user:password1")
    print("[*] Lockout: 5 failed attempts → 30s cooldown\n")
    app.run(host="127.0.0.1", port=5000, debug=False)
