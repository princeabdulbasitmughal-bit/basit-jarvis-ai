"""
AI Engine Controller Evaluation Script
Tests:
- /api/engine/basit1 (Devin / OpenHands code gen)
- /api/engine/basit2 (Deep Research synthesis)
- /api/engine/basit3 (OWASP Guardian & Security)
- /api/engine/basit4 (Autonomous AI Hedge Fund)
- /api/engine/gemini-spark (PySpark Distributed + Gemini 2.0)
- /api/engine/arsenal (Open-Source AI Arsenal / Dual-Node GPU Cluster)
"""

import sys
import json
import time
import urllib.request
import urllib.error

# Force UTF-8 stdout
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_URL = "http://localhost:8888"

ENGINES_TO_TEST = [
    {
        "endpoint": "/api/engine/arsenal",
        "method": "GET",
        "payload": None,
        "name": "Open-Source AI Arsenal / GPU Cluster",
        "timeout": 20
    },
    {
        "endpoint": "/api/engine/basit3",
        "method": "POST",
        "payload": {"action": "sweep_zombies"},
        "name": "Basit3 Guardian / Security & Process Guard",
        "timeout": 30
    },
    {
        "endpoint": "/api/engine/basit1",
        "method": "POST",
        "payload": {"task": "Write a quick hello world in python"},
        "name": "Basit1 Coder / Devin OpenHands",
        "timeout": 45
    },
    {
        "endpoint": "/api/engine/basit2",
        "method": "POST",
        "payload": {"query": "Latest advances in agentic AI 2026"},
        "name": "Basit2 Deep Research",
        "timeout": 45
    },
    {
        "endpoint": "/api/engine/basit4",
        "method": "POST",
        "payload": {"task": "Analyze NVDA stock trajectory"},
        "name": "Basit4 AI Hedge Fund Consensus",
        "timeout": 45
    },
    {
        "endpoint": "/api/engine/gemini-spark",
        "method": "POST",
        "payload": {"task": "Verify spark cluster memory profile"},
        "name": "Gemini-Spark Master Engine",
        "timeout": 45
    },
]

def test_engine(cfg):
    url = f"{BASE_URL}{cfg['endpoint']}"
    method = cfg["method"]
    payload = cfg["payload"]
    timeout = cfg["timeout"]
    name = cfg["name"]

    print(f"\nTesting [{name}] -> {url} ({method})...")
    t0 = time.perf_counter()
    headers = {"Content-Type": "application/json"}
    
    data_bytes = None
    if payload and method == "POST":
        data_bytes = json.dumps(payload).encode("utf-8")
        
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
    
    status_code = None
    response_json = None
    error_msg = None
    
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status_code = resp.status
            raw_body = resp.read().decode("utf-8", errors="replace")
            try:
                response_json = json.loads(raw_body)
            except Exception:
                response_json = {"raw": raw_body[:300]}
    except urllib.error.HTTPError as e:
        status_code = e.code
        err_body = e.read().decode("utf-8", errors="replace")
        error_msg = f"HTTP {e.code}: {err_body[:200]}"
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"

    elapsed = round((time.perf_counter() - t0) * 1000, 2)
    success = status_code == 200 and response_json and response_json.get("success", False)
    
    print(f"  Result: Code={status_code} | Time={elapsed}ms | Success={success}")
    if response_json:
        sum_text = response_json.get("summary") or response_json.get("engine") or str(response_json)[:120]
        print(f"  Summary/Preview: {str(sum_text)[:120]}...")
    if error_msg:
        print(f"  Error: {error_msg}")

    return {
        "engine": cfg["endpoint"],
        "name": name,
        "status_code": status_code,
        "success": success,
        "latency_ms": elapsed,
        "status": "Working" if success else ("Degraded" if status_code == 200 else "Not Working"),
        "error": error_msg,
        "preview": str(response_json.get("summary") or response_json.get("engine") or "")[:150] if response_json else error_msg
    }

def main():
    print("=" * 65)
    print("AI ENGINE CONTROLLER CAPABILITY EVALUATION (http://localhost:8888)")
    print("=" * 65)
    
    results = {}
    for cfg in ENGINES_TO_TEST:
        res = test_engine(cfg)
        results[cfg["endpoint"]] = res
        
    print("\n" + "=" * 65)
    print("AI ENGINE TEST MATRIX:")
    print("=" * 65)
    for ep, r in results.items():
        print(f"{r['engine']:<28} | {r['status']:<11} | Latency: {r['latency_ms']:>8.1f} ms | {r['name']}")

    with open("reports/engine_eval_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("\nResults saved to reports/engine_eval_results.json")

if __name__ == "__main__":
    main()
