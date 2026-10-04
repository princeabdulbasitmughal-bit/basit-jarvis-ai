"""
================================================================================
BASIT JARVIS AI — ATOMIC STORAGE, DB WAL & RECOVERY TEST SUITE
================================================================================
Validates:
1. Atomic write safety for contacts.json and reminders.json (fsync + replace).
2. JSON corruption resistance: automatic rollback to .bak on truncated/0-byte file.
3. SQLite SessionMemory WAL mode & integrity check.
4. SQLite corruption resilience: simulated DB damage auto-repaired via .bak snapshot.
5. Instant recovery latency upon daemon re-spawns (<50ms).
================================================================================
"""
import os
import sys
import time
import json
import sqlite3
import shutil
import tempfile
import unittest
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from modules.atomic_storage import atomic_write_json, atomic_read_json
from modules.session_memory import SessionMemory


class TestJarvisAtomicAndRecovery(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="jarvis_test_"))
        self.contacts_file = self.test_dir / "contacts.json"
        self.reminders_file = self.test_dir / "reminders.json"
        self.db_path = str(self.test_dir / "test_session_memory.db")

    def tearDown(self):
        try:
            shutil.rmtree(self.test_dir)
        except Exception:
            pass

    def test_01_atomic_write_json_and_backup(self):
        """Test atomic writing of contacts registry with verified .bak generation."""
        contacts_v1 = {
            "basit": {"phone": "923007654321", "email": "absh5506@gmail.com"}
        }
        contacts_v2 = {
            "basit": {"phone": "923007654321", "email": "absh5506@gmail.com"},
            "ali": {"phone": "923001234567", "email": "ali@gmail.com"}
        }

        # Write v1
        self.assertTrue(atomic_write_json(self.contacts_file, contacts_v1, backup=True))
        self.assertTrue(self.contacts_file.exists())

        # Write v2
        self.assertTrue(atomic_write_json(self.contacts_file, contacts_v2, backup=True))

        bak_file = self.contacts_file.with_suffix(".json.bak")
        self.assertTrue(bak_file.exists(), ".bak backup file must exist")

        v2_data, _ = atomic_read_json(self.contacts_file)
        v1_data, _ = atomic_read_json(bak_file)

        self.assertEqual(len(v2_data), 2)
        self.assertEqual(len(v1_data), 1)

    def test_02_reminders_corruption_auto_heal(self):
        """Test that truncated/0-byte reminders file auto-heals from backup."""
        reminders = [
            {"id": 1, "task": "AI Swarm Review", "delay_sec": 300},
            {"id": 2, "task": "Check MT5 Bridge", "delay_sec": 600}
        ]
        # Establish baseline + backup
        atomic_write_json(self.reminders_file, reminders, backup=True)
        reminders.append({"id": 3, "task": "Cloudflare URL ping", "delay_sec": 120})
        atomic_write_json(self.reminders_file, reminders, backup=True)

        # Corrupt primary with partial write
        with open(self.reminders_file, "w", encoding="utf-8") as f:
            f.write('[{"id": 1, "task": "AI Swarm Review", "delay_sec": 30')

        # Read should trigger auto-heal from .bak
        recovered, was_healed = atomic_read_json(self.reminders_file, auto_heal_from_backup=True)
        self.assertTrue(was_healed)
        self.assertEqual(len(recovered), 2)
        self.assertEqual(recovered[0]["task"], "AI Swarm Review")

    def test_03_sqlite_wal_mode_and_live_backup(self):
        """Test that SessionMemory initializes in WAL mode and supports live physical backup."""
        mem = SessionMemory(db_path=self.db_path)
        mem.save_conversation("user", "Hello Jarvis", engine="basit1")
        mem.save_conversation("assistant", "Greetings Basit!", engine="basit1")
        mem.save_preference("theme", "sovereign_dark")

        # Verify WAL mode
        with sqlite3.connect(self.db_path) as conn:
            mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
            self.assertEqual(mode.lower(), "wal", "Database must operate in WAL mode for high concurrency")
            integrity = conn.execute("PRAGMA integrity_check;").fetchone()[0]
            self.assertEqual(integrity, "ok", "Database integrity must be ok")

        # Verify physical backup was created
        bak_path = self.db_path + ".bak"
        self.assertTrue(os.path.exists(bak_path))
        with sqlite3.connect(bak_path) as bconn:
            b_count = bconn.execute("SELECT count(*) FROM conversations;").fetchone()[0]
            self.assertEqual(b_count, 2)

    def test_04_sqlite_corruption_recovery(self):
        """Test that a corrupted SQLite database is automatically recovered from its .bak snapshot."""
        # 1. Populate DB and ensure backup is synced
        mem = SessionMemory(db_path=self.db_path)
        mem.save_conversation("user", "Critical mission state alpha", engine="deepseek")
        mem.save_preference("api_state", "active")
        self.assertTrue(mem.backup())

        # 2. Inject raw disk corruption into the primary database file
        # Overwrite SQLite header and first sector with garbage
        with open(self.db_path, "r+b") as f:
            f.seek(0)
            f.write(b"CORRUPTED_GARBAGE_HEADER_DATA_NOT_A_SQLITE3_DATABASE_FILE_XYZ123456789")

        # Verify that direct query fails on corrupted DB
        with self.assertRaises(sqlite3.DatabaseError):
            test_conn = sqlite3.connect(self.db_path)
            test_conn.execute("SELECT * FROM conversations;")
            test_conn.close()

        # 3. Instantiate SessionMemory — self-healing should trigger
        t0 = time.perf_counter()
        repaired_mem = SessionMemory(db_path=self.db_path)
        recovery_ms = (time.perf_counter() - t0) * 1000

        # 4. Verify that data was restored and DB is healthy
        self.assertTrue(repaired_mem.verify_integrity())
        history = repaired_mem.get_history(limit=5)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["content"], "Critical mission state alpha")
        self.assertEqual(repaired_mem.get_preference("api_state"), "active")
        print(f"\n[PASS] Jarvis SQLite database corruption recovery latency: {recovery_ms:.3f} ms")

    def test_05_instant_daemon_respawn_recovery_latency(self):
        """Measure recovery time (<50ms) across daemon termination and restart cycles."""
        # Setup initial state
        mem = SessionMemory(db_path=self.db_path)
        for i in range(20):
            mem.save_conversation("user", f"Query {i}", engine="basit1")

        # Daemon kill simulation
        del mem

        # Daemon re-spawn
        t0 = time.perf_counter()
        respawned_mem = SessionMemory(db_path=self.db_path)
        history = respawned_mem.get_history(limit=20)
        recovery_ms = (time.perf_counter() - t0) * 1000

        self.assertLess(recovery_ms, 50.0, f"Daemon respawn latency {recovery_ms:.2f}ms exceeds 50ms target")
        self.assertEqual(len(history), 20)
        print(f"[PASS] Jarvis daemon re-spawn and state retrieval latency: {recovery_ms:.3f} ms")


if __name__ == "__main__":
    unittest.main()
