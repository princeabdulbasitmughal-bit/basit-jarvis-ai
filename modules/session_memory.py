"""
================================================================================
BASIT JARVIS AI -- PERSISTENT SESSION MEMORY ENGINE
================================================================================
SQLite-backed conversation history, preferences, and engine analytics.
"""
import os
import json
import sqlite3
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'session_memory.db')

class SessionMemory:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _conn(self):
        return sqlite3.connect(self.db_path, timeout=5)

    def _init_db(self):
        with self._conn() as c:
            c.executescript("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    engine TEXT,
                    timestamp REAL DEFAULT (strftime('%s','now'))
                );
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at REAL DEFAULT (strftime('%s','now'))
                );
                CREATE TABLE IF NOT EXISTS engine_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    engine TEXT NOT NULL,
                    task TEXT,
                    result_summary TEXT,
                    latency_sec REAL,
                    success INTEGER DEFAULT 1,
                    timestamp REAL DEFAULT (strftime('%s','now'))
                );
            """)

    def save_conversation(self, role: str, content: str, engine: str = None):
        try:
            with self._conn() as c:
                c.execute('INSERT INTO conversations (role, content, engine) VALUES (?, ?, ?)', (role, content[:4000], engine))
        except Exception as e:
            pass

    def get_history(self, limit: int = 20) -> List[Dict]:
        try:
            with self._conn() as c:
                rows = c.execute('SELECT role, content, engine, timestamp FROM conversations ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
            return [{'role': r[0], 'content': r[1], 'engine': r[2], 'time': datetime.fromtimestamp(r[3]).strftime('%H:%M:%S')} for r in reversed(rows)]
        except Exception:
            return []

    def save_preference(self, key: str, value: str):
        try:
            with self._conn() as c:
                c.execute('INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)', (key, str(value)))
        except Exception:
            pass

    def get_preference(self, key: str, default: str = None) -> str:
        try:
            with self._conn() as c:
                row = c.execute('SELECT value FROM preferences WHERE key=?', (key,)).fetchone()
            return row[0] if row else default
        except Exception:
            return default

    def save_engine_result(self, engine: str, task: str, result_summary: str, latency: float, success: bool = True):
        try:
            with self._conn() as c:
                c.execute('INSERT INTO engine_log (engine, task, result_summary, latency_sec, success) VALUES (?,?,?,?,?)',
                          (engine, task[:200], result_summary[:500], latency, int(success)))
        except Exception:
            pass

    def get_engine_stats(self) -> Dict:
        try:
            with self._conn() as c:
                rows = c.execute('SELECT engine, COUNT(*), AVG(latency_sec), SUM(success) FROM engine_log GROUP BY engine').fetchall()
            return {r[0]: {'calls': r[1], 'avg_latency_sec': round(r[2] or 0, 2), 'successes': r[3]} for r in rows}
        except Exception:
            return {}

    def search_history(self, query: str, limit: int = 5) -> List[Dict]:
        try:
            with self._conn() as c:
                rows = c.execute("SELECT role, content, engine FROM conversations WHERE content LIKE ? ORDER BY id DESC LIMIT ?",
                                (f'%{query}%', limit)).fetchall()
            return [{'role': r[0], 'content': r[1], 'engine': r[2]} for r in rows]
        except Exception:
            return []

    def export_markdown(self, path: str = None) -> str:
        history = self.get_history(100)
        stats = self.get_engine_stats()
        lines = ['# Basit Jarvis Session Memory Export', f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', '', '## Conversation History', '']
        for h in history:
            prefix = '**User**' if h['role'] == 'user' else '**Jarvis**'
            lines.append(f"{prefix} [{h['time']}]: {h['content'][:200]}")
        lines += ['', '## Engine Statistics', '']
        for eng, s in stats.items():
            lines.append(f"- **{eng}**: {s['calls']} calls | avg {s['avg_latency_sec']}s | {s['successes']} successes")
        md = '\n'.join(lines)
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(md)
        return md


if __name__ == '__main__':
    mem = SessionMemory()
    mem.save_conversation('user', 'Aap kaun ho?')
    mem.save_conversation('assistant', 'Main Basit Jarvis hoon, aapka sovereign AI.', engine='gemini')
    mem.save_preference('language', 'roman_urdu')
    mem.save_engine_result('basit1', 'FastAPI code generate karo', 'Code generated in 3.2s', 3.2, True)
    mem.save_engine_result('basit4', 'NVDA analysis', 'BUY consensus 85%', 9.1, True)
    print('Engine Stats:', json.dumps(mem.get_engine_stats(), indent=2))
    print('History:', json.dumps(mem.get_history(5), indent=2))
    print('Preferred language:', mem.get_preference('language'))
    print('Session Memory DB OK at:', mem.db_path)
