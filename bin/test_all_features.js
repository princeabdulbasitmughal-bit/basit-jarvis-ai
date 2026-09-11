// Basit Jarvis AI — Comprehensive Test Suite
const http = require('http');

const BASE = 'http://localhost:8888';
let passed = 0;
let failed = 0;

function request(path, method = 'GET', body = null) {
  return new Promise((resolve) => {
    const url = new URL(path, BASE);
    const options = {
      hostname: url.hostname,
      port: url.port,
      path: url.pathname,
      method: method,
      headers: { 'Content-Type': 'application/json' },
      timeout: 8000
    };

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', chunk => { data += chunk; });
      res.on('end', () => {
        try {
          resolve({ status: res.statusCode, data: JSON.parse(data || '{}') });
        } catch (e) {
          resolve({ status: res.statusCode, data: data });
        }
      });
    });

    req.on('error', (err) => resolve({ status: 500, error: err.message }));
    req.on('timeout', () => { req.destroy(); resolve({ status: 408, error: 'Timeout' }); });

    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

async function runTests() {
  console.log('===============================================================');
  console.log('  ♾️  BASIT JARVIS AI — 100% EXHAUSTIVE FEATURE VERIFICATION PASS');
  console.log('===============================================================');

  async function test(name, path, method = 'GET', body = null) {
    const res = await request(path, method, body);
    if (res.status >= 200 && res.status < 400 && !res.error) {
      console.log(`  ✅ [PASS] ${name}`);
      passed++;
      return res.data;
    } else {
      console.log(`  ❌ [FAIL] ${name} -> ${res.error || res.status}`);
      failed++;
      return null;
    }
  }

  console.log('\n--- 1. CORE TELEMETRY & CLUSTER TESTS ---');
  await test('Server Status API', '/api/status');
  await test('Cluster Telemetry API', '/api/cluster');

  console.log('\n--- 2. DESKTOP OS AUDIO & SYSTEM TESTS ---');
  await test('Volume Set 80%', '/api/command', 'POST', { command: 'volume 80' });
  await test('Volume Up (+10%)', '/api/command', 'POST', { command: 'volume up' });
  await test('Volume Down (-10%)', '/api/command', 'POST', { command: 'volume down' });
  await test('Mute System Audio', '/api/command', 'POST', { command: 'mute' });
  await test('Unmute System Audio', '/api/command', 'POST', { command: 'unmute' });
  await test('Recycle Bin Empty', '/api/command', 'POST', { command: 'recycle bin khali karo' });
  await test('System Specs Command', '/api/command', 'POST', { command: 'system specs batao' });

  console.log('\n--- 3. SCREENSHOT & STATIC FILE SERVING TESTS ---');
  const scData = await test('Screenshot Capture', '/api/command', 'POST', { command: 'take a screenshot' });
  if (scData && scData.path) {
    const filename = scData.path.split(/[\\/]/).pop();
    await test(`Screenshot Static Serving (/screenshots/${filename})`, `/screenshots/${filename}`);
  }

  console.log('\n--- 4. PRODUCTIVITY (NOTES & CLIPBOARD) TESTS ---');
  await test('Post Quick Note', '/api/notes', 'POST', { text: 'Automated test note from BasitLoop' });
  await test('Get Stored Notes', '/api/notes');
  await test('Get Clipboard', '/api/clipboard');

  console.log('\n--- 5. ALL 6 BASIT AUTONOMOUS POWER ENGINES ---');
  const engines = ['basit1', 'basit2', 'basit3', 'basit4', 'basitswarm', 'arsenal'];
  for (const eng of engines) {
    await test(`Engine /${eng}`, `/api/${eng}`, 'POST', { prompt: 'Healthcheck test' });
  }

  console.log('\n===============================================================');
  console.log(`  SUMMARY: ${passed} PASSED | ${failed} FAILED`);
  console.log('===============================================================');

  process.exit(failed > 0 ? 1 : 0);
}

runTests();
