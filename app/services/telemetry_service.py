"""
Service layer for gathering system metrics via psutil.
All I/O bound calls are executed in a thread pool to keep the event loop responsive.
"""

import asyncio
import logging
from typing import Dict

import psutil

logger = logging.getLogger(__name__)


async def _gather_metrics() -> Dict[str, float | int]:
    """Blocking psutil calls wrapped in asyncio.to_thread."""
    cpu = psutil.cpu_percent(interval=0.5)  # short interval for realistic reading
    virtual_mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    logger.debug(
        "Raw psutil metrics collected: cpu=%s, mem=%s, disk=%s",
        cpu,
        virtual_mem,
        disk,
    )
    return {
        "cpu_percent": cpu,
        "memory_total": virtual_mem.total,
        "memory_used": virtual_mem.used,
        "memory_percent": virtual_mem.percent,
        "disk_total": disk.total,
        "disk_used": disk.used,
        "disk_percent": disk.percent,
    }


async def get_system_metrics() -> Dict[str, float | int]:
    """
    Public async API to retrieve system metrics.
    Returns a dictionary ready to be serialized by Pydantic.
    """
    try:
        metrics = await asyncio.to_thread(_gather_metrics)
        logger.info("System metrics retrieved successfully")
        return metrics
    except Exception as exc:  # pragma: no cover
        logger.exception("Failed to gather system metrics: %s", exc)
        raise
