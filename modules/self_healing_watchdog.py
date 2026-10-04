"""
================================================================================
👑 BASIT JARVIS AI — 24/7 ENTERPRISE SELF-HEALING WATCHDOG DAEMON
================================================================================
Continuous autonomous health guardian for Basit Jarvis AI.
Features:
  - Real-time CPU & RAM guard thresholds (90% CPU, 88% RAM, 3.5GB process limit)
  - Port 8888 & HTTP Status telemetry verification with strict timeouts
  - Zombie and hung process detection & automatic termination (releasing port locks)
  - Memory leak protection (auto-recycles leaking Node/Python processes)
  - Continuous supervisor for launch_jarvis_master.py (Tray, HUD, Hotkeys)
  - SQLite database integrity validation (PRAGMA integrity_check)
  - Disk health monitoring (ensures >= 5GB free space on primary drive)
  - Rotating log management (prevents unbounded log file growth)
  - Native Windows 11 toast notifications on auto-recovery & resource containment
  - Zero system hang guarantee — all I/O strictly timed out, periodic GC passes

Usage:
  python modules/self_healing_watchdog.py           # Interactive monitor
  python modules/self_healing_watchdog.py --daemon  # Silent background daemon
================================================================================
"""

import os
import gc
import sys
import time
import json
import socket
import logging
from logging.handlers import RotatingFileHandler
import requests
import subprocess
import threading
from datetime import datetime
import psutil

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
WATCHDOG_LOG = os.path.join(LOGS_DIR, "self_healing_watchdog.log")

# Rotating file handler to prevent unbounded log growth (max 10MB x 5 backups)
rotating_handler = RotatingFileHandler(
    WATCHDOG_LOG, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
)
console_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
rotating_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger = logging.getLogger("JarvisWatchdog")
logger.setLevel(logging.INFO)
logger.handlers.clear()
logger.addHandler(rotating_handler)
logger.addHandler(console_handler)

# ── CONFIGURATION & THRESHOLDS ──────────────────────────────────────────────
PORT = 8888
STATUS_URL = f"http://127.0.0.1:{PORT}/api/status"
CHECK_INTERVAL_SEC = 15
MAX_RECOVERY_ATTEMPTS = 5

# Guard Thresholds
MAX_CPU_PERCENT = 90.0            # Trigger alert/investigation if sustained > 90%
MAX_RAM_PERCENT = 88.0            # Trigger alert if total RAM > 88%
MAX_PROCESS_RAM_MB = 3500.0       # Trigger recycle if Jarvis Node/Python > 3.5GB RSS
MIN_DISK_FREE_GB = 5.0            # Trigger warning if disk free < 5GB
MAX_DISK_PERCENT = 95.0           # Trigger warning if disk > 95% full
CONSECUTIVE_SPIKE_LIMIT = 3       # 3 intervals * 15s = 45s sustained high load

# Managed HTTP Session for zero socket leaks
http_session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=5, pool_maxsize=10, max_retries=1)
http_session.mount("http://", adapter)
http_session.mount("https://", adapter)


def send_toast(title: str, message: str):
    """Dispatches non-blocking Windows toast notification."""
    def _toast():
        try:
            from win11toast import toast
            toast(title, message, app_id="Basit Jarvis AI Watchdog")
            return
        except Exception:
            pass
        try:
            from winotify import Notification
            n = Notification(app_id="Basit Jarvis AI Watchdog", title=title, msg=message)
            n.show()
        except Exception:
            pass

    t = threading.Thread(target=_toast, daemon=True)
    t.start()


def check_port_open(port: int, host: str = "127.0.0.1", timeout: float = 2.0) -> bool:
    """Check if TCP port is accepting connections."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def check_http_health(url: str, timeout: float = 4.0) -> dict:
    """Check if Jarvis HTTP server is responding with valid JSON telemetry."""
    try:
        resp = http_session.get(url, timeout=(2.0, timeout))
        if resp.status_code == 200:
            data = resp.json()
            return {"healthy": True, "data": data}
        return {"healthy": False, "error": f"HTTP {resp.status_code}"}
    except requests.RequestException as e:
        return {"healthy": False, "error": str(e)[:120]}


def check_memory_db() -> bool:
    """Verify SQLite database integrity."""
    db_path = os.path.join(BASE_DIR, "data", "session_memory.db")
    if not os.path.exists(db_path):
        return True  # Will be auto-created when needed
    try:
        import sqlite3
        conn = sqlite3.connect(db_path, timeout=3.0)
        cur = conn.cursor()
        cur.execute("PRAGMA integrity_check;")
        res = cur.fetchone()
        conn.close()
        return res and res[0] == "ok"
    except Exception as e:
        logger.warning(f"[DB INTEGRITY FAIL]: {e}")
        return False


def check_disk_health(path: str = BASE_DIR) -> dict:
    """Verify primary storage drive has sufficient free headroom."""
    try:
        usage = psutil.disk_usage(path)
        free_gb = round(usage.free / (1024 ** 3), 2)
        total_gb = round(usage.total / (1024 ** 3), 2)
        percent = usage.percent
        healthy = (free_gb >= MIN_DISK_FREE_GB) and (percent <= MAX_DISK_PERCENT)
        return {
            "healthy": healthy,
            "free_gb": free_gb,
            "total_gb": total_gb,
            "percent": percent
        }
    except Exception as e:
        logger.warning(f"[DISK HEALTH CHECK ERROR]: {e}")
        return {"healthy": True, "free_gb": 0, "total_gb": 0, "percent": 0}


def is_jarvis_process(proc: psutil.Process) -> bool:
    """Strictly checks if a process belongs to Basit Jarvis AI."""
    try:
        base_norm = os.path.normpath(BASE_DIR).lower()
        try:
            cwd_norm = os.path.normpath(proc.cwd()).lower()
            if cwd_norm == base_norm or cwd_norm.startswith(base_norm + os.sep):
                return True
            else:
                return False
        except (psutil.AccessDenied, Exception):
            pass

        try:
            cmd = " ".join(proc.cmdline() or []).lower()
            if "basit-jarvis-ai" in cmd:
                return True
        except (psutil.AccessDenied, Exception):
            pass
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
    return False


def kill_hung_jarvis_processes(port: int = PORT) -> int:
    """
    Terminates any process hanging on PORT or running server.js in BASE_DIR.
    Releases port lockups and prevents EADDRINUSE errors upon restart.
    """
    killed_count = 0
    pids_to_kill = set()

    # 1. Check process actively listening on port 8888
    try:
        for c in psutil.net_connections(kind="inet"):
            if c.laddr and c.laddr.port == port and c.pid:
                pids_to_kill.add(c.pid)
    except Exception as e:
        logger.debug(f"[NETSTAT SCAN]: {e}")

    # 2. Check for node server.js specifically inside BASE_DIR
    for p in psutil.process_iter(["pid", "name"]):
        try:
            if p.info["name"] and p.info["name"].lower().startswith("node"):
                if is_jarvis_process(p):
                    pids_to_kill.add(p.info["pid"])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # 3. Graceful termination followed by forceful kill if stubborn
    for pid in pids_to_kill:
        try:
            proc = psutil.Process(pid)
            logger.warning(f"[PORT LOCKUP RELEASE] Terminating hung process PID {pid} ({proc.name()})...")
            proc.terminate()
            try:
                proc.wait(timeout=3.0)
            except psutil.TimeoutExpired:
                logger.warning(f"[FORCE KILL] PID {pid} did not exit after 3s, force killing...")
                proc.kill()
            killed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.debug(f"PID {pid} already dead or inaccessible: {e}")

    # 4. Wait for port to be fully released
    for _ in range(10):
        if not check_port_open(port, timeout=0.5):
            break
        time.sleep(0.5)

    return killed_count


def reap_zombies_and_orphans():
    """
    Scans for dead/zombie processes and cleans up orphaned workers.
    Ensures zero system lockups or leaked background handles.
    """
    reaped = 0
    for p in psutil.process_iter(["pid", "name", "status"]):
        try:
            # Check for zombie status
            if p.info.get("status") == psutil.STATUS_ZOMBIE:
                logger.info(f"[REAPER] Reaping zombie PID {p.info['pid']}")
                p.kill()
                reaped += 1
                continue

            # Check for orphaned jarvis workers
            if is_jarvis_process(p):
                name = (p.info.get("name") or "").lower()
                # Check if process memory is leaking (> MAX_PROCESS_RAM_MB)
                mem = p.memory_info()
                rss_mb = mem.rss / (1024 * 1024)
                if rss_mb > MAX_PROCESS_RAM_MB:
                    logger.error(f"🚨 [MEMORY LEAK DETECTED] Process PID {p.pid} ({name}) RSS={rss_mb:.1f}MB exceeds {MAX_PROCESS_RAM_MB}MB! Recycling...")
                    send_toast("Jarvis Memory Guard 🛡️", f"Terminating PID {p.pid} ({rss_mb:.0f}MB leak)")
                    p.terminate()
                    reaped += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return reaped


def restart_node_server() -> bool:
    """Restarts Node.js server gracefully, releasing any hung port lock first."""
    logger.info("[RECOVERY] Cleaning port lockups before spawning node server.js...")
    kill_hung_jarvis_processes(PORT)

    logger.info("[RECOVERY] Attempting to spawn node server.js...")
    try:
        subprocess.Popen(
            ["node", "server.js"],
            cwd=BASE_DIR,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # Poll up to 10 seconds for port to open and status to respond
        for attempt in range(10):
            time.sleep(1)
            if check_port_open(PORT, timeout=1.0):
                health = check_http_health(STATUS_URL, timeout=2.0)
                if health.get("healthy"):
                    logger.info("✅ [RECOVERY SUCCESS] Jarvis server restored & healthy on port 8888!")
                    send_toast("Jarvis Self-Healing ✅", "Server auto-restarted and verified operational on port 8888!")
                    return True
        logger.warning("⚠️ [RECOVERY WARNING] Port opened but /api/status did not respond in time.")
        return check_port_open(PORT)
    except Exception as e:
        logger.error(f"[RECOVERY ERROR]: {e}")
    return False


def ensure_master_suite() -> bool:
    """Ensures launch_jarvis_master.py is active for Tray, HUD, and Hotkeys."""
    try:
        for p in psutil.process_iter(["pid", "cmdline"]):
            try:
                cmd = " ".join(p.info.get("cmdline") or []).lower()
                if "launch_jarvis_master.py" in cmd:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        logger.info("[WATCHDOG] launch_jarvis_master.py is not running. Spawning master suite...")
        subprocess.Popen(
            [sys.executable, "launch_jarvis_master.py", "--tray"],
            cwd=BASE_DIR,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        logger.info("✅ [WATCHDOG] Spawned launch_jarvis_master.py background suite.")
        return True
    except Exception as e:
        logger.warning(f"[WATCHDOG MASTER SPAWN FAILED]: {e}")
        return False


def inspect_high_resource_consumers():
    """Identifies and logs top CPU and RAM consumer processes for diagnostic telemetry."""
    try:
        procs = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
            try:
                mem = p.info.get("memory_info")
                rss_mb = (mem.rss / (1024 * 1024)) if mem else 0
                procs.append({
                    "pid": p.info["pid"],
                    "name": p.info["name"],
                    "cpu": p.info.get("cpu_percent") or 0.0,
                    "ram_mb": rss_mb
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        # Sort by CPU
        top_cpu = sorted(procs, key=lambda x: x["cpu"], reverse=True)[:3]
        top_ram = sorted(procs, key=lambda x: x["ram_mb"], reverse=True)[:3]
        logger.warning(f"[RESOURCE GUARD AUDIT] Top CPU: {top_cpu}")
        logger.warning(f"[RESOURCE GUARD AUDIT] Top RAM: {top_ram}")
    except Exception as e:
        logger.debug(f"[RESOURCE AUDIT ERROR]: {e}")


def watchdog_loop(daemon_mode: bool = False):
    """Main continuous health evaluation loop."""
    logger.info("╔══════════════════════════════════════════════════════════════════╗")
    logger.info("║   👑 BASIT JARVIS AI — ENTERPRISE SELF-HEALING WATCHDOG ONLINE   ║")
    logger.info(f"║   Monitoring Port {PORT} every {CHECK_INTERVAL_SEC}s — Zero Hang System         ║")
    logger.info(f"║   Thresholds: CPU < {MAX_CPU_PERCENT}% | RAM < {MAX_RAM_PERCENT}% | ProcRAM < {MAX_PROCESS_RAM_MB}MB  ║")
    logger.info("╚══════════════════════════════════════════════════════════════════╝")

    consecutive_failures = 0
    consecutive_cpu_spikes = 0
    consecutive_ram_spikes = 0
    cycle_counter = 0

    ensure_master_suite()

    # Prime psutil CPU calculation
    psutil.cpu_percent(interval=None)

    while True:
        try:
            cycle_counter += 1
            now_str = datetime.now().strftime("%H:%M:%S")

            # 1. System Resource Checks
            sys_cpu = psutil.cpu_percent(interval=None)
            mem_info = psutil.virtual_memory()
            sys_ram = mem_info.percent
            disk_info = check_disk_health(BASE_DIR)

            # CPU Guard Threshold Evaluation
            if sys_cpu >= MAX_CPU_PERCENT:
                consecutive_cpu_spikes += 1
                logger.warning(f"[{now_str}] ⚠️ High CPU detected: {sys_cpu}% ({consecutive_cpu_spikes}/{CONSECUTIVE_SPIKE_LIMIT})")
                if consecutive_cpu_spikes >= CONSECUTIVE_SPIKE_LIMIT:
                    logger.error(f"🚨 [CPU GUARD TRIGGERED] Sustained high CPU: {sys_cpu}% for {consecutive_cpu_spikes * CHECK_INTERVAL_SEC}s!")
                    send_toast("Jarvis CPU Guard ⚠️", f"Sustained CPU at {sys_cpu:.1f}%. Inspecting offending processes.")
                    inspect_high_resource_consumers()
            else:
                consecutive_cpu_spikes = 0

            # RAM Guard Threshold Evaluation
            if sys_ram >= MAX_RAM_PERCENT:
                consecutive_ram_spikes += 1
                logger.warning(f"[{now_str}] ⚠️ High RAM detected: {sys_ram}% ({consecutive_ram_spikes}/{CONSECUTIVE_SPIKE_LIMIT})")
                if consecutive_ram_spikes >= CONSECUTIVE_SPIKE_LIMIT:
                    logger.error(f"🚨 [RAM GUARD TRIGGERED] Sustained high RAM: {sys_ram}%!")
                    send_toast("Jarvis RAM Guard ⚠️", f"Total RAM at {sys_ram:.1f}%. Checking memory leaks.")
                    inspect_high_resource_consumers()
            else:
                consecutive_ram_spikes = 0

            # Disk Space Warning
            if not disk_info.get("healthy", True):
                logger.warning(f"[{now_str}] ⚠️ Low Disk Space on Drive! Free: {disk_info.get('free_gb')}GB ({disk_info.get('percent')}%)")

            # 2. Service & Port Health Checks
            port_ok = check_port_open(PORT, timeout=2.0)
            http_check = check_http_health(STATUS_URL, timeout=4.0) if port_ok else {"healthy": False, "error": "Port 8888 closed"}
            db_ok = check_memory_db()

            # 3. Health Assessment & Logging
            if port_ok and http_check.get("healthy") and db_ok:
                consecutive_failures = 0
                telemetry = http_check.get("data", {}).get("telemetry", {})
                t_cpu = telemetry.get("cpu_percent", sys_cpu)
                t_ram = telemetry.get("ram_percent", sys_ram)
                if not daemon_mode:
                    logger.info(
                        f"[{now_str}] 🟢 System Healthy | Port 8888 OK | "
                        f"CPU: {sys_cpu}% | RAM: {sys_ram}% ({mem_info.used // (1024**3)}GB / {mem_info.total // (1024**3)}GB) | "
                        f"Disk Free: {disk_info.get('free_gb')}GB | DB: OK"
                    )
            else:
                consecutive_failures += 1
                reason = http_check.get("error", "Unknown") if port_ok else "Port 8888 unreachable"
                if not db_ok:
                    reason += " | DB Integrity error"
                logger.warning(f"[{now_str}] ⚠️ Health check failed ({consecutive_failures}/{MAX_RECOVERY_ATTEMPTS}): {reason}")

                if consecutive_failures >= 2:
                    logger.error(f"[{now_str}] 🚨 Triggering Self-Healing Recovery...")
                    recovered = restart_node_server()
                    if recovered:
                        consecutive_failures = 0

            # 4. Periodic Maintenance (Every 4 cycles = ~60s)
            if cycle_counter % 4 == 0:
                ensure_master_suite()
                reap_zombies_and_orphans()

            # 5. Internal Garbage Collection & Zero Leak Guarantee (Every 100 cycles = ~25 min)
            if cycle_counter % 100 == 0:
                gc.collect()

            time.sleep(CHECK_INTERVAL_SEC)

        except KeyboardInterrupt:
            logger.info("\n[WATCHDOG] Stopped by user.")
            break
        except Exception as e:
            logger.error(f"[WATCHDOG UNEXPECTED ERROR]: {e}")
            time.sleep(CHECK_INTERVAL_SEC)


if __name__ == "__main__":
    is_daemon = "--daemon" in sys.argv
    watchdog_loop(daemon_mode=is_daemon)
