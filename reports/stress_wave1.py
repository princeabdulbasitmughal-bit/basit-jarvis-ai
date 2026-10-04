import os
import json
import time
import requests
from datetime import datetime

os.makedirs(r'E:\basit-jarvis-ai\reports', exist_ok=True)

TESTS = [
    {'id': 1,  'method': 'GET',  'url': 'http://127.0.0.1:8888/api/ping',
     'body': None, 'expect': 'ONLINE'},
    {'id': 2,  'method': 'GET',  'url': 'http://127.0.0.1:8888/api/status',
     'body': None, 'expect': None},
    {'id': 3,  'method': 'GET',  'url': 'http://127.0.0.1:8888/api/cluster',
     'body': None, 'expect': None},
    {'id': 4,  'method': 'POST', 'url': 'http://127.0.0.1:8888/api/command',
     'body': {'command': '50 ko 4 se multiply karo phir 25 add karo'}, 'expect': '225'},
    {'id': 5,  'method': 'POST', 'url': 'http://127.0.0.1:8888/api/command',
     'body': {'command': 'koi mazedaar joke sunao'}, 'expect': None},
    {'id': 6,  'method': 'POST', 'url': 'http://127.0.0.1:8888/api/command',
     'body': {'command': 'naya note likho: OmniTrade loop ne 200 se zyada iterations complete kiye 100% pass rate ke sath'},
     'expect': None},
    {'id': 7,  'method': 'POST', 'url': 'http://127.0.0.1:8888/api/command',
     'body': {'command': 'mera naam kya hai'}, 'expect': None},
    {'id': 8,  'method': 'GET',  'url': 'http://127.0.0.1:8888/api/voices',
     'body': None, 'expect': None},
    {'id': 9,  'method': 'GET',  'url': 'http://127.0.0.1:8888/api/models',
     'body': None, 'expect': None},
    {'id': 10, 'method': 'POST', 'url': 'http://127.0.0.1:8888/api/engine/basit1',
     'body': {'task': 'Write hello world in Python'}, 'expect': None},
    {'id': 11, 'method': 'POST', 'url': 'http://127.0.0.1:8888/api/engine/basit2',
     'body': {'task': 'Summarize AI trends 2026'}, 'expect': None},
    {'id': 12, 'method': 'POST', 'url': 'http://127.0.0.1:8888/api/engine/gemini-spark',
     'body': {'task': 'ping'}, 'expect': None},
]

LABELS = {
    1:  'GET /api/ping',
    2:  'GET /api/status',
    3:  'GET /api/cluster',
    4:  'POST /api/command (math)',
    5:  'POST /api/command (joke)',
    6:  'POST /api/command (note)',
    7:  'POST /api/command (name)',
    8:  'GET /api/voices',
    9:  'GET /api/models',
    10: 'POST /api/engine/basit1',
    11: 'POST /api/engine/basit2',
    12: 'POST /api/engine/gemini-spark',
}

results = []
total_score = 0.0
max_per_test = 100.0 / len(TESTS)

print()
print('=' * 95)
print(f'  BASIT JARVIS AI — ENGINE STRESS TEST WAVE 1   [{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]')
print('=' * 95)

for t in TESTS:
    tid   = t['id']
    label = LABELS[tid]
    result = {'test_id': tid, 'label': label, 'method': t['method'], 'url': t['url']}

    try:
        start = time.time()
        if t['method'] == 'GET':
            resp = requests.get(t['url'], timeout=10)
        else:
            resp = requests.post(t['url'], json=t['body'], timeout=10)
        elapsed_ms = round((time.time() - start) * 1000, 2)

        body_text  = resp.text[:200]
        status     = resp.status_code
        ok         = status in (200, 201)
        extra      = ''

        # extra validation for math answer
        if t['expect'] and t['expect'] not in resp.text:
            ok    = False
            extra = f'[expected "{t["expect"]}" not found in response]'

        verdict      = 'PASS' if ok else 'FAIL'
        test_score   = round(max_per_test, 2) if ok else 0.0
        total_score += test_score

        result.update({
            'status_code':      status,
            'latency_ms':       elapsed_ms,
            'verdict':          verdict,
            'score':            test_score,
            'response_preview': body_text,
            'note':             extra,
        })

        flag = '✔' if ok else '✘'
        print(f'  [{verdict}] {flag} #{tid:02d} {label:<40} | HTTP {status} | {elapsed_ms:>8.1f} ms  {extra}')
        print(f'           {body_text[:130]}')
        print()

    except Exception as exc:
        elapsed_ms = -1
        result.update({
            'status_code':      0,
            'latency_ms':       -1,
            'verdict':          'FAIL',
            'score':            0.0,
            'response_preview': str(exc),
            'note':             'exception',
        })
        print(f'  [FAIL] ✘ #{tid:02d} {label:<40} | ERR | {str(exc)[:80]}')
        print()

    results.append(result)

print('=' * 95)

# ── Summary table ──────────────────────────────────────────────────────────────
print()
print(f'  {"#":<4} {"LABEL":<42} {"STATUS":>6} {"LATENCY":>10} {"VERDICT":>7} {"SCORE":>7}')
print(f'  {"-"*4} {"-"*42} {"-"*6} {"-"*10} {"-"*7} {"-"*7}')
for r in results:
    lat = f'{r["latency_ms"]:>8.1f}ms' if r['latency_ms'] >= 0 else '     N/A'
    print(f'  {r["test_id"]:<4} {r["label"]:<42} {str(r["status_code"]):>6} {lat:>10} '
          f'{r["verdict"]:>7} {r["score"]:>6.2f}')

print(f'  {"-"*4} {"-"*42} {"-"*6} {"-"*10} {"-"*7} {"-"*7}')
print(f'  {"TOTAL SCORE":>55}  {round(total_score, 1):>6.1f} / 100')
print()
print('=' * 95)

# ── Save JSON report ───────────────────────────────────────────────────────────
report = {
    'generated_at': datetime.utcnow().isoformat() + 'Z',
    'server':       'http://127.0.0.1:8888',
    'wave':         'engine_stress_wave1',
    'total_score':  round(total_score, 1),
    'max_score':    100,
    'tests':        results,
}
report_path = r'E:\basit-jarvis-ai\reports\engine_stress_wave1.json'
with open(report_path, 'w', encoding='utf-8') as fh:
    json.dump(report, fh, indent=2, ensure_ascii=False)

print(f'  ✔  Report saved  →  {report_path}')
print()
