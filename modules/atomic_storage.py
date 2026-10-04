"""
================================================================================
BASIT JARVIS AI — ATOMIC STORAGE & CRASH RESISTANCE ENGINE
================================================================================
Production-grade persistence with atomic writes, corruption detection,
and self-healing backup recovery for JSON configurations and databases.
================================================================================
"""
import os
import sys
import json
import uuid
import shutil
import logging
from pathlib import Path
from typing import Any, Optional, Tuple, Union

logger = logging.getLogger("Jarvis.AtomicStorage")


def atomic_write_json(
    filepath: Union[Path, str],
    data: Any,
    indent: int = 2,
    backup: bool = True,
    ensure_ascii: bool = False
) -> bool:
    """
    Atomically writes data to a JSON file.
    Guarantees:
      - Zero-byte file protection via staging tmp files.
      - Hardware sync via os.fsync.
      - Atomic replacement on Windows/NTFS using os.replace.
      - Preserves verified .bak copies for automatic rollback.
    """
    target = Path(filepath).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)

    temp_name = f"{target.name}.tmp.{os.getpid()}.{uuid.uuid4().hex[:8]}"
    temp_path = target.parent / temp_name

    try:
        payload = json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())

        if backup and target.exists() and target.stat().st_size > 0:
            bak_path = target.with_suffix(target.suffix + ".bak")
            try:
                shutil.copy2(target, bak_path)
            except Exception as e:
                logger.warning(f"Could not create backup for {target}: {e}")

        os.replace(temp_path, target)
        return True

    except Exception as e:
        logger.error(f"Atomic write failed for {target}: {e}", exc_info=True)
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass
        return False


def atomic_read_json(
    filepath: Union[Path, str],
    default: Any = None,
    auto_heal_from_backup: bool = True
) -> Tuple[Any, bool]:
    """
    Safely reads JSON with automatic corruption detection and self-healing.
    Returns:
        (data, was_healed_from_backup: bool)
    """
    target = Path(filepath).resolve()
    bak_path = target.with_suffix(target.suffix + ".bak")

    # 1. Primary load attempt
    if target.exists() and target.stat().st_size > 0:
        try:
            with open(target, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data, False
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as err:
            logger.error(f"⚠️ Primary state corrupted in {target}: {err}. Initiating self-healing...")

    # 2. Check and restore from backup if primary is missing, 0-byte, or corrupted
    if auto_heal_from_backup and bak_path.exists() and bak_path.stat().st_size > 0:
        try:
            with open(bak_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.warning(f"🔄 Self-Healing Activated: Restoring {target.name} from verified backup (.bak)...")
            atomic_write_json(target, data, backup=False)
            return data, True
        except Exception as bak_err:
            logger.critical(f"❌ Backup file {bak_path} also corrupted: {bak_err}")

    # 3. Quarantine corrupt file if unrecoverable
    if target.exists():
        try:
            quarantine = target.with_suffix(f"{target.suffix}.corrupt.{int(uuid.uuid4().hex[:6], 16)}")
            shutil.move(target, quarantine)
            logger.warning(f"Quarantined corrupted file to {quarantine.name}")
        except Exception:
            pass

    return default, False
