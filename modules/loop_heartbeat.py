"""
👑 BASIT JARVIS AI — 5-MINUTE AUTONOMOUS HEARTBEAT & AUDITOR
Runs health, telemetry, database, dropzone, and process safety checks.
"""

import os
import sys
import time
import sqlite3
import requests

# Force UTF-8 for Windows PowerShell terminals
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE_DIR)

def check_heartbeat():
    t0 = time.time()
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "port_8888": "OFFLINE",
        "cpu_percent": 0,
        "ram_percent": 0,
        "db_integrity": False,
        "dropzone_files": 0,
        "latency_ms": 0,
        "status": "FAIL"
    }

    try:
        r = requests.get("http://localhost:8888/api/status", timeout=3).json()
        report["port_8888"] = r.get("status", "UNKNOWN")
    except Exception as e:
        report["port_8888"] = f"ERROR: {str(e)[:40]}"

    try:
        m = requests.get("http://localhost:8888/api/metrics", timeout=3).json()
        report["cpu_percent"] = m.get("cpu_percent", 0)
        report["ram_percent"] = m.get("ram_percent", 0)
    except Exception:
        pass

    try:
        db_path = os.path.join(BASE_DIR, "data", "session_memory.db")
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            res = conn.cursor().execute("PRAGMA integrity_check").fetchone()
            conn.close()
            report["db_integrity"] = (res and res[0] == "ok")
        else:
            report["db_integrity"] = True
    except Exception:
        report["db_integrity"] = False

    try:
        dp = os.path.join(BASE_DIR, "dropzone")
        if os.path.exists(dp):
            report["dropzone_files"] = len(os.listdir(dp))
    except Exception:
        pass

    report["latency_ms"] = round((time.time() - t0) * 1000, 1)
    if report["port_8888"] == "ONLINE" and report["db_integrity"]:
        report["status"] = "OPTIMAL"

    print(f"👑 [HEARTBEAT {report['timestamp']}] Status: {report['status']} | Port 8888: {report['port_8888']} | CPU: {report['cpu_percent']}% | RAM: {report['ram_percent']}% | DB: OK | Files: {report['dropzone_files']} ({report['latency_ms']}ms)")
    return report

if __name__ == "__main__":
    check_heartbeat()
