"""
👑 Basit Jarvis AI — Sovereign 6-Engine Master Runner
Module: modules/sovereign_master_runner.py

Executes all 6 sovereign engines:
1. /basit1: Devin/OpenHands Ultra-Fast Software Engineer
2. /basit2: Multi-Agent Deep Research & Synthesis
3. /basit3: Enterprise OWASP Guardian & Zero-Hang Sentinel
4. /basit4: Autonomous AI Hedge Fund & Boardroom Consensus
5. /basitswarm: 100-Agent Ultra-Parallel Burst Engine
6. /arsenal: OpenSource AI Arsenal Dual-Node GPU Telemetry

Saves aggregate master telemetry to: reports/sovereign_full_run.json
"""

import os
import sys
import json
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

BASE_DIR = r"E:\basit-jarvis-ai"
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
OUTPUT_JSON = os.path.join(REPORTS_DIR, "sovereign_full_run.json")

# Ensure UTF-8 stdout
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

sys.path.insert(0, os.path.join(BASE_DIR, "modules"))
try:
    from ai_brain import AIBrain
    from basit_engines import BasitEngines
except Exception as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def run_master_cycle():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    t0 = time.time()
    brain = AIBrain()
    engines = BasitEngines(brain, default_dir=BASE_DIR)
    
    print("=" * 70)
    print("👑 BASIT JARVIS — SOVEREIGN 6-ENGINE MASTER EXECUTION RUNNER")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Target: Basit bhai")
    print("=" * 70)
    
    tasks = {
        "basit1": ("basit1", "FastAPI production telemetry microservice with JWT and psutil metrics"),
        "basit2": ("basit2", "Autonomous AI Agents and Multi-Model Swarms in 2026"),
        "basit3": ("basit3", "all"),
        "basit4": ("basit4", "NVDA"),
        "basitswarm": ("basitswarm", "Autonomous Enterprise SaaS Platform Architecture"),
        "arsenal": ("arsenal", "")
    }

    results = {}

    def run_one(key, eng_name, eng_task):
        sub_t0 = time.time()
        print(f"▶ Dispatching {eng_name.upper()}...")
        try:
            res = engines.dispatch(eng_name, eng_task, BASE_DIR)
            dur = round(time.time() - sub_t0, 2)
            print(f"✔ {eng_name.upper()} finished in {dur}s")
            return key, res
        except Exception as ex:
            dur = round(time.time() - sub_t0, 2)
            print(f"✖ {eng_name.upper()} failed after {dur}s: {ex}")
            return key, {"error": str(ex), "latency_sec": dur}

    # Execute with 6 workers in parallel
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [
            executor.submit(run_one, k, v[0], v[1])
            for k, v in tasks.items()
        ]
        for f in futures:
            k, res = f.result()
            results[k] = res

    total_latency = round(time.time() - t0, 2)

    master_payload = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_latency_sec": total_latency,
        "boss": "Basit bhai",
        "basit1": results.get("basit1", {}),
        "basit2": results.get("basit2", {}),
        "basit3": results.get("basit3", {}),
        "basit4": results.get("basit4", {}),
        "basitswarm": results.get("basitswarm", {}),
        "arsenal": results.get("arsenal", {})
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(master_payload, f, indent=2, ensure_ascii=False)

    print("=" * 70)
    print(f"🎉 MASTER 6-ENGINE RUN COMPLETE! Total time: {total_latency}s")
    print(f"Saved master report to: {OUTPUT_JSON}")
    print("=" * 70)
    return master_payload

if __name__ == "__main__":
    run_master_cycle()
