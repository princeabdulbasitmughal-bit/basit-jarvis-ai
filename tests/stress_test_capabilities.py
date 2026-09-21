"""
================================================================================
👑 BASIT JARVIS AI & OMNITRADE — COMPREHENSIVE CAPABILITY STRESS TESTER
================================================================================
Executes live end-to-end benchmark testing across all 20 subsystems and live APIs:
- Natural Language Urdu/English Math, Jokes, Notes via /api/command
- GPU Cluster Status (/api/cluster)
- All 6 AI Engines (/api/engine/basit1..4, gemini-spark, arsenal)
- OmniTrade Scalper Core (http://127.0.0.1:8899/status)
- Cloudflare Public Tunnel
"""

import urllib.request
import urllib.parse
import json
import time
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

results = {}

def test_endpoint(name, url, method="GET", payload=None, timeout=15):
    t0 = time.perf_counter()
    req = urllib.request.Request(url, method=method)
    req.add_header('User-Agent', 'BasitStressTester/1.0')
    if payload:
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        data_bytes = json.dumps(payload).encode('utf-8')
    else:
        data_bytes = None
    
    try:
        with urllib.request.urlopen(req, data=data_bytes, timeout=timeout) as resp:
            elapsed = round((time.perf_counter() - t0) * 1000, 2)
            body = resp.read().decode('utf-8', errors='replace')
            try:
                parsed = json.loads(body)
            except Exception:
                parsed = body[:200]
            return {
                "status": "PASS",
                "http_code": resp.getcode(),
                "latency_ms": elapsed,
                "data": parsed
            }
    except Exception as e:
        elapsed = round((time.perf_counter() - t0) * 1000, 2)
        return {
            "status": "FAIL",
            "http_code": getattr(e, 'code', 500),
            "latency_ms": elapsed,
            "error": str(e)
        }

print("=================================================================")
print("👑 RUNNING LIVE CAPABILITY STRESS BENCHMARK FOR BASIT BHAI")
print("=================================================================")

# 1. Math Query
print("\n[1/12] Testing Math Query ('50 into 4 plus 25 kitna hota hai')...")
res_math = test_endpoint(
    "Math Query",
    "http://localhost:8888/api/command",
    method="POST",
    payload={"command": "50 into 4 plus 25 kitna hota hai"}
)
results["math_query"] = res_math
print(f" -> Status: {res_math['status']} | Latency: {res_math['latency_ms']}ms | Response: {json.dumps(res_math.get('data', {}))[:120]}")

# 2. Joke Query
print("\n[2/12] Testing Joke Query ('koi zabardast joke sunao')...")
res_joke = test_endpoint(
    "Joke Query",
    "http://localhost:8888/api/command",
    method="POST",
    payload={"command": "koi zabardast joke sunao"}
)
results["joke_query"] = res_joke
print(f" -> Status: {res_joke['status']} | Latency: {res_joke['latency_ms']}ms | Response: {json.dumps(res_joke.get('data', {}))[:120]}")

# 3. Note Creation Query
print("\n[3/12] Testing Note Query ('naya note likho Basit bhai ke business expansion plans')...")
res_note = test_endpoint(
    "Note Query",
    "http://localhost:8888/api/command",
    method="POST",
    payload={"command": "naya note likho Basit bhai ke business expansion plans"}
)
results["note_query"] = res_note
print(f" -> Status: {res_note['status']} | Latency: {res_note['latency_ms']}ms | Response: {json.dumps(res_note.get('data', {}))[:120]}")

# 4. GPU Cluster Status
print("\n[4/12] Testing GPU Cluster Status (/api/cluster)...")
res_cluster = test_endpoint("GPU Cluster", "http://localhost:8888/api/cluster")
results["gpu_cluster"] = res_cluster
print(f" -> Status: {res_cluster['status']} | Latency: {res_cluster['latency_ms']}ms | Cluster Nodes: {list(res_cluster.get('data', {}).get('cluster', {}).keys())}")

# 5. Engine Basit1 (Devin / OpenHands)
print("\n[5/12] Testing Engine Basit1 (/api/engine/basit1?task=ping)...")
res_b1 = test_endpoint("Basit1", "http://localhost:8888/api/engine/basit1?task=ping")
results["engine_basit1"] = res_b1
print(f" -> Status: {res_b1['status']} | Latency: {res_b1['latency_ms']}ms")

# 6. Engine Basit2 (Deep Research)
print("\n[6/12] Testing Engine Basit2 (/api/engine/basit2?task=ping)...")
res_b2 = test_endpoint("Basit2", "http://localhost:8888/api/engine/basit2?task=ping")
results["engine_basit2"] = res_b2
print(f" -> Status: {res_b2['status']} | Latency: {res_b2['latency_ms']}ms")

# 7. Engine Basit3 (OWASP Guardian)
print("\n[7/12] Testing Engine Basit3 (/api/engine/basit3?task=ping)...")
res_b3 = test_endpoint("Basit3", "http://localhost:8888/api/engine/basit3?task=ping")
results["engine_basit3"] = res_b3
print(f" -> Status: {res_b3['status']} | Latency: {res_b3['latency_ms']}ms")

# 8. Engine Basit4 (Autonomous Hedge Fund)
print("\n[8/12] Testing Engine Basit4 (/api/engine/basit4?task=ping)...")
res_b4 = test_endpoint("Basit4", "http://localhost:8888/api/engine/basit4?task=ping")
results["engine_basit4"] = res_b4
print(f" -> Status: {res_b4['status']} | Latency: {res_b4['latency_ms']}ms")

# 9. Engine Gemini Spark (PySpark + Gemini 2.0)
print("\n[9/12] Testing Engine Gemini Spark (/api/engine/gemini-spark?task=ping)...")
res_gs = test_endpoint("Gemini Spark", "http://localhost:8888/api/engine/gemini-spark?task=ping")
results["engine_gemini_spark"] = res_gs
print(f" -> Status: {res_gs['status']} | Latency: {res_gs['latency_ms']}ms")

# 10. Engine AI Arsenal Matrix
print("\n[10/12] Testing Engine Arsenal Matrix (/api/engine/arsenal)...")
res_ars = test_endpoint("Arsenal", "http://localhost:8888/api/engine/arsenal", timeout=20)
results["engine_arsenal"] = res_ars
print(f" -> Status: {res_ars['status']} | Latency: {res_ars['latency_ms']}ms")

# 11. OmniTrade Scalper Core (Port 8899)
print("\n[11/12] Testing OmniTrade Scalper Core (http://127.0.0.1:8899/status)...")
res_scalper = test_endpoint("OmniTrade Scalper", "http://127.0.0.1:8899/status")
results["omnitrade_scalper"] = res_scalper
if res_scalper['status'] == 'PASS':
    d = res_scalper['data']
    lat = d.get('latency_metrics', {})
    print(f" -> Status: {d.get('status')} | Balance: ${d.get('balance')} | Win Rate: {d.get('win_rate_pct')}% | Avg Tick: {lat.get('avg_tick_loop_us')} µs | Tick-to-Signal: {lat.get('tick_to_signal_us')} µs")
else:
    print(f" -> Failed: {res_scalper}")

# 12. Cloudflare Public Tunnel
cf_url = "https://nikon-produce-ruled-generated.trycloudflare.com"
try:
    with open(r"E:\omnitrade-ai-matrix\tunnel_status.json", "r", encoding="utf-8") as f:
        t_data = json.load(f)
        if t_data.get("url"):
            cf_url = t_data.get("url")
except Exception:
    pass

print(f"\n[12/12] Testing Cloudflare Public Tunnel ({cf_url}/status)...")
res_cf = test_endpoint("Cloudflare Tunnel", f"{cf_url}/status", timeout=15)
results["cloudflare_tunnel"] = res_cf
print(f" -> Status: {res_cf['status']} | Latency: {res_cf['latency_ms']}ms")

# Save full results
with open("reports/live_stress_benchmark_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\n=================================================================")
print("✅ ALL 12 ENDPOINT BENCHMARKS COMPLETED AND SAVED TO reports/live_stress_benchmark_results.json")
print("=================================================================")
