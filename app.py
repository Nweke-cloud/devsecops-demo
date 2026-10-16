import sqlite3
import subprocess
from flask import Flask, request

app = Flask(__name__)
SECRET_KEY = "hardcoded-secret-123"  # SAST bait


@app.route("/")
def index():
    return '<h1>Demo</h1><form action="/search"><input name="q"><input type="submit"></form>'


@app.route("/search")
def search():
    q = request.args.get("q", "")
    conn = sqlite3.connect(":memory:")
    conn.execute("create table t(name text)")
    conn.execute("select * from t where name = '%s'" % q)  # SQL injection
    return "<p>Results for " + q + "</p>"  # reflected XSS


@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    return subprocess.check_output("ping -c 1 " + host, shell=True)  # command injection


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)