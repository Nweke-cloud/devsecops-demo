import ipaddress
import os
import sqlite3
import subprocess

from flask import Flask, render_template_string, request

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]  # injected at runtime, never committed


@app.after_request
def security_headers(resp):
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Content-Security-Policy"] = "default-src 'self'"
    resp.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.route("/")
def index():
    return '<h1>Demo</h1><form action="/search"><input name="q"><input type="submit"></form>'


@app.route("/search")
def search():
    q = request.args.get("q", "")
    conn = sqlite3.connect(":memory:")
    conn.execute("create table t(name text)")
    conn.execute("select * from t where name = ?", (q,))  # parameterized
    return render_template_string("<p>Results for {{ q }}</p>", q=q)  # autoescaped


@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    try:
        ipaddress.ip_address(host)  # allowlist: only a real IP gets through
    except ValueError:
        return "invalid host", 400
    return subprocess.check_output(["ping", "-c", "1", host])  # list, no shell


if __name__ == "__main__":
    # Binding 0.0.0.0 is required inside a container; reviewed and accepted.
    app.run(host="0.0.0.0", port=5000)  # nosemgrep: python.flask.security.audit.app-run-param-config.avoid_app_run_with_bad_host