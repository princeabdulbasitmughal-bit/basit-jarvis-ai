import sys
import os
import json
import time
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

base = 'http://localhost:8888'

print('=' * 60)
print('👑 BASIT JARVIS AI — LIVE ENDPOINT & ENGINE VERIFICATION')
print('=' * 60)

tests = [
    ('Cluster Status', 'GET', f'{base}/api/cluster-status', None, 25),
    ('Spark Status', 'GET', f'{base}/api/spark?task=status', None, 10),
    ('Spark SQL', 'POST', f'{base}/api/spark', {'task': 'sql', 'query': 'SELECT * FROM contacts'}, 30),
    ('Gemini Spark Engine', 'POST', f'{base}/api/gemini-spark', {'prompt': 'status'}, 10),
    ('Command: /gemini-spark status', 'POST', f'{base}/api/command', {'command': '/gemini-spark status'}, 15),
    ('Command: /basit1 ping', 'POST', f'{base}/api/command', {'command': '/basit1 ping'}, 15),
    ('Command: /basit3 sweep', 'POST', f'{base}/api/command', {'command': '/basit3 sweep'}, 15),
    ('Command: /basit4 NVDA', 'POST', f'{base}/api/command', {'command': '/basit4 NVDA'}, 15),
    ('Command: /basitswarm SaaS', 'POST', f'{base}/api/command', {'command': '/basitswarm SaaS'}, 15),
]

for name, method, url, payload, timeout in tests:
    t0 = time.time()
    try:
        if method == 'GET':
            req = urllib.request.Request(url, headers={'User-Agent': 'JarvisVerify'})
        else:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json', 'User-Agent': 'JarvisVerify'})
        
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode('utf-8')
            dt = round(time.time() - t0, 2)
            parsed = json.loads(body)
            success = parsed.get('success', True)
            print(f'✅ [PASS] {name:<30} | {dt:>5}s | success={success}')
    except Exception as e:
        dt = round(time.time() - t0, 2)
        print(f'❌ [FAIL] {name:<30} | {dt:>5}s | Error: {e}')

print('=' * 60)
print('VERIFICATION RUN COMPLETE')
print('=' * 60)
