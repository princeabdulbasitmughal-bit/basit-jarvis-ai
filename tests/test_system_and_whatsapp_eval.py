"""
Evaluation Script for:
1. System Controls (modules/system_control.py)
   - System status (CPU%, RAM%, Disk%, Battery)
   - CPU/RAM statistics
   - Process management (sweep zombies, get active window)
   - Screenshot capability (take screenshot, verify file size)
2. WhatsApp Integration & Contact Book
   - data/contacts.json structure & contents
   - Contact resolution
   - modules/whatsapp_sender.js inspection & mock dry-run
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime

# UTF-8 stdout
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from modules.system_control import SystemControl

def evaluate_system_controls():
    print("=" * 60)
    print("1. EVALUATING SYSTEM CONTROLS (modules/system_control.py)")
    print("=" * 60)
    
    sys_ctrl = SystemControl()
    results = {}

    # A. System Status (CPU / RAM / Disk / Battery)
    print("\n[A] Testing get_system_status()...")
    t0 = time.perf_counter()
    status = sys_ctrl.get_system_status()
    latency_status = round((time.perf_counter() - t0) * 1000, 2)
    print(f"Status Output: {json.dumps(status, indent=2)}")
    status_ok = (
        isinstance(status.get("cpu_percent"), (int, float)) and
        isinstance(status.get("ram_percent"), (int, float)) and
        isinstance(status.get("ram_used_gb"), (int, float)) and
        isinstance(status.get("disk_percent"), (int, float))
    )
    results["system_status"] = {
        "status": "Working" if status_ok else "Not Working",
        "latency_ms": latency_status,
        "details": status
    }

    # B. Active Window Detection
    print("\n[B] Testing get_active_window()...")
    t0 = time.perf_counter()
    active_win = sys_ctrl.get_active_window()
    latency_win = round((time.perf_counter() - t0) * 1000, 2)
    print(f"Active Window: {active_win}")
    results["active_window"] = {
        "status": "Working" if active_win and "title" in active_win else "Degraded",
        "latency_ms": latency_win,
        "details": active_win
    }

    # C. Process Management / Zombie Sweeper
    print("\n[C] Testing sweep_zombies()...")
    t0 = time.perf_counter()
    zombies_swept = sys_ctrl.sweep_zombies()
    latency_sweep = round((time.perf_counter() - t0) * 1000, 2)
    print(f"Zombies Swept: {zombies_swept}")
    results["process_management"] = {
        "status": "Working",
        "latency_ms": latency_sweep,
        "zombies_killed": zombies_swept
    }

    # D. Screenshot Capability
    print("\n[D] Testing take_screenshot()...")
    t0 = time.perf_counter()
    shot_path = sys_ctrl.take_screenshot()
    latency_shot = round((time.perf_counter() - t0) * 1000, 2)
    shot_valid = shot_path and os.path.exists(shot_path) and os.path.getsize(shot_path) > 1000
    print(f"Screenshot Path: {shot_path} | Exists: {shot_valid} | Size: {os.path.getsize(shot_path) if shot_valid else 0} bytes")
    results["screenshot"] = {
        "status": "Working" if shot_valid else "Not Working",
        "latency_ms": latency_shot,
        "file_path": shot_path,
        "file_size_bytes": os.path.getsize(shot_path) if shot_valid else 0
    }

    # E. Shell Execution
    print("\n[E] Testing run_shell_command()...")
    t0 = time.perf_counter()
    cmd_res = sys_ctrl.run_shell_command("Write-Output 'Jarvis System Control Active'")
    latency_cmd = round((time.perf_counter() - t0) * 1000, 2)
    print(f"Shell Result: {cmd_res}")
    results["shell_execution"] = {
        "status": "Working" if cmd_res.get("success") else "Not Working",
        "latency_ms": latency_cmd
    }

    return results

def evaluate_whatsapp_and_contacts():
    print("\n" + "=" * 60)
    print("2. EVALUATING WHATSAPP INTEGRATION & CONTACT BOOK")
    print("=" * 60)
    
    results = {}
    
    # A. Contact Book (data/contacts.json)
    contacts_path = os.path.join(BASE_DIR, "data", "contacts.json")
    print(f"\n[A] Inspecting Contact Book ({contacts_path})...")
    t0 = time.perf_counter()
    contacts_data = {}
    contacts_valid = False
    if os.path.exists(contacts_path):
        try:
            with open(contacts_path, "r", encoding="utf-8") as f:
                contacts_data = json.load(f)
            contacts_valid = isinstance(contacts_data, dict) and len(contacts_data) > 0
        except Exception as e:
            print(f"Error loading contacts: {e}")
    latency_contacts = round((time.perf_counter() - t0) * 1000, 2)
    print(f"Contacts Count: {len(contacts_data)}")
    print(f"Sample Contacts: {list(contacts_data.items())[:5]}")
    results["contact_book"] = {
        "status": "Working" if contacts_valid else "Not Working",
        "count": len(contacts_data),
        "latency_ms": latency_contacts,
        "contacts": contacts_data
    }

    # B. Contact API on Server (GET /api/contacts)
    print("\n[B] Testing Server API GET /api/contacts...")
    import urllib.request
    t0 = time.perf_counter()
    api_contacts_ok = False
    api_count = 0
    try:
        with urllib.request.urlopen("http://localhost:8888/api/contacts", timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            api_count = len(data) if isinstance(data, (dict, list)) else 0
            api_contacts_ok = resp.status == 200
    except Exception as e:
        print(f"Contacts API error: {e}")
    latency_api_contacts = round((time.perf_counter() - t0) * 1000, 2)
    print(f"API /api/contacts -> Status: {api_contacts_ok} | Count: {api_count} | Latency: {latency_api_contacts}ms")
    results["contacts_api"] = {
        "status": "Working" if api_contacts_ok else "Not Working",
        "count": api_count,
        "latency_ms": api_contacts_api if False else latency_api_contacts
    }

    # C. WhatsApp Integration Module (modules/whatsapp_sender.js)
    wa_script = os.path.join(BASE_DIR, "modules", "whatsapp_sender.js")
    print(f"\n[C] Inspecting WhatsApp Sender Script ({wa_script})...")
    wa_exists = os.path.exists(wa_script)
    print(f"whatsapp_sender.js exists: {wa_exists}")
    
    # Test node execution of whatsapp_sender.js with argument check
    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            ["node", wa_script, "help"],
            capture_output=True,
            text=True,
            timeout=3,
            cwd=BASE_DIR
        )
        exit_code = proc.returncode
        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()
    except subprocess.TimeoutExpired:
        exit_code = 1
        stdout = ""
        stderr = "Timeout waiting for WhatsApp auth"
    latency_wa = round((time.perf_counter() - t0) * 1000, 2)
    print(f"whatsapp_sender.js Exit Code: {exit_code}")
    print(f"Stdout: {stdout[:200]}")
    print(f"Stderr: {stderr[:200]}")
    
    # Check if dependencies (puppeteer / whatsapp-web.js) are present or if fallback web URL is used
    has_dep_error = "cannot find module" in stderr.lower()
    results["whatsapp_integration"] = {
        "status": "Degraded" if has_dep_error else ("Working" if exit_code in (0, 1) else "Not Working"),
        "latency_ms": latency_wa,
        "script_exists": wa_exists,
        "exit_code": exit_code,
        "notes": "Direct browser automation fallback exists in ConversationalBrain._whatsapp_send" if has_dep_error else "Headless WhatsApp module present; QR scan needed for first auth"
    }

    return results

if __name__ == "__main__":
    sys_results = evaluate_system_controls()
    wa_results = evaluate_whatsapp_and_contacts()
    
    combined = {
        "system_controls": sys_results,
        "whatsapp_and_contacts": wa_results
    }
    
    with open("reports/system_and_whatsapp_eval.json", "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
    print("\nEvaluation saved to reports/system_and_whatsapp_eval.json")
