"""
================================================================================
BASIT JARVIS AI -- LIVE TERMINAL DASHBOARD
================================================================================
Real-time terminal dashboard showing system health, engine status, and
recent activity. Run standalone or import for status checking.
"""
import os, sys, json, time, threading
from datetime import datetime
from typing import Dict, Any

# Fix Windows console encoding for emoji/unicode
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    import psutil
    PSUTIL = True
except ImportError:
    PSUTIL = False

try:
    from dotenv import load_dotenv
    for ep in [r'E:\.env', '.env']:
        if os.path.exists(ep):
            load_dotenv(ep); break
except ImportError:
    pass


class LiveDashboard:
    def __init__(self):
        self.start_time = time.time()
        self.engine_calls = {e: 0 for e in ['basit1','basit2','basit3','basit4','basitswarm','arsenal','basitloop','gemini-spark']}
        self.last_activity = []
        self._lock = threading.Lock()

    def get_system_stats(self) -> Dict[str, Any]:
        stats = {
            'uptime_sec': round(time.time() - self.start_time),
            'timestamp': datetime.now().strftime('%H:%M:%S'),
        }
        if PSUTIL:
            try:
                stats['cpu_percent'] = psutil.cpu_percent(interval=0.1)
                mem = psutil.virtual_memory()
                stats['ram_used_gb'] = round(mem.used / 1e9, 1)
                stats['ram_total_gb'] = round(mem.total / 1e9, 1)
                stats['ram_percent'] = mem.percent
                disk = psutil.disk_usage('C:\\')
                stats['disk_percent'] = round(disk.percent, 1)
                stats['disk_used_gb'] = round(disk.used / 1e9, 1)
            except Exception:
                pass
        return stats

    def get_api_keys_status(self) -> Dict[str, bool]:
        return {
            'Gemini': bool(os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')),
            'Groq': bool(os.getenv('GROQ_API_KEY')),
            'Mistral': bool(os.getenv('MISTRAL_API_KEY')),
            'Anthropic': bool(os.getenv('ANTHROPIC_API_KEY')),
            'OpenAI': bool(os.getenv('OPENAI_API_KEY')),
            'HuggingFace': bool(os.getenv('HF_TOKEN_1')),
        }

    def get_server_status(self) -> Dict[str, Any]:
        import urllib.request as _ur
        try:
            with _ur.urlopen(_ur.Request('http://localhost:8888/api/ping'), timeout=2) as r:
                d = json.loads(r.read().decode())
                return {'online': True, 'version': d.get('version', '?'), 'uptime_sec': d.get('uptime_sec', 0)}
        except Exception:
            return {'online': False}

    def render_header(self) -> str:
        lines = [
            '\033[96m' + '='*70 + '\033[0m',
            '\033[96m  \U0001f451 BASIT JARVIS AI \u2014 LIVE SYSTEM DASHBOARD\033[0m',
            f'\033[96m  {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\033[0m',
            '\033[96m' + '='*70 + '\033[0m',
        ]
        return '\n'.join(lines)

    def render_system_stats(self, stats: Dict) -> str:
        cpu = stats.get('cpu_percent', '?')
        ram = stats.get('ram_percent', '?')
        disk = stats.get('disk_percent', '?')
        uptime = stats.get('uptime_sec', 0)
        h, m = divmod(uptime, 3600)
        m, s = divmod(m, 60)
        lines = [
            '\033[93m\u25a0 SYSTEM TELEMETRY\033[0m',
            f'  CPU: {cpu}%  RAM: {ram}%  DISK: {disk}%  UPTIME: {h}h{m}m{s}s',
        ]
        return '\n'.join(lines)

    def render_api_keys(self, keys: Dict) -> str:
        lines = ['\033[93m\u25a0 API KEY STATUS\033[0m']
        for name, active in keys.items():
            icon = '\033[92m\u25cf\033[0m' if active else '\033[91m\u25cf\033[0m'
            lines.append(f'  {icon} {name}')
        return '\n'.join(lines)

    def render_server(self, srv: Dict) -> str:
        if srv.get('online'):
            uptime = srv.get('uptime_sec', 0)
            h, m = divmod(uptime, 3600)
            return f'\033[93m\u25a0 SERVER\033[0m\n  \033[92m\u25cf ONLINE\033[0m  v{srv.get("version","?")}  uptime:{h}h{m}m'
        return '\033[93m\u25a0 SERVER\033[0m\n  \033[91m\u25cf OFFLINE\033[0m  (start with: node server.js)'

    def print_dashboard(self):
        stats = self.get_system_stats()
        keys = self.get_api_keys_status()
        srv = self.get_server_status()
        print(self.render_header())
        print(self.render_system_stats(stats))
        print()
        print(self.render_api_keys(keys))
        print()
        print(self.render_server(srv))
        print('\033[96m' + '='*70 + '\033[0m')

    def get_status_json(self) -> Dict[str, Any]:
        return {
            'system': self.get_system_stats(),
            'api_keys': self.get_api_keys_status(),
            'server': self.get_server_status(),
            'timestamp': datetime.now().isoformat()
        }


if __name__ == '__main__':
    dash = LiveDashboard()
    dash.print_dashboard()
    status = dash.get_status_json()
    print('\nJSON status:')
    print(json.dumps(status, indent=2))
