"""
System metrics collection using psutil.
Provides async endpoints that return JSON payloads.
"""

import asyncio
from typing import Dict

import psutil
from fastapi import APIRouter, Depends, HTTPException, status

from .auth import get_current_user, TokenData

router = APIRouter(prefix="/metrics", tags=["metrics"])


async def _collect_cpu() -> float:
    """
    Returns CPU usage percentage.
    """
    return await asyncio.to_thread(psutil.cpu_percent, interval=1)


async def _collect_memory() -> Dict[str, float]:
    """
    Returns memory usage statistics.
    """
    mem = await asyncio.to_thread(psutil.virtual_memory)
    return {
        "total_gb": mem.total / (1024 ** 3),
        "available_gb": mem.available / (1024 ** 3),
        "used_gb": mem.used / (1024 ** 3),
        "percent": mem.percent,
    }


async def _collect_disk() -> Dict[str, float]:
    """
    Returns disk usage statistics for the root partition.
    """
    disk = await asyncio.to_thread(psutil.disk_usage, "/")
    return {
        "total_gb": disk.total / (1024 ** 3),
        "used_gb": disk.used / (1024 ** 3),
        "free_gb": disk.free / (1024 ** 3),
        "percent": disk.percent,
    }


@router.get("/", response_model=Dict[str, Dict[str, float]])
async def get_metrics(current_user: TokenData = Depends(get_current_user)):
    """
    Returns aggregated system metrics.
    Protected by JWT authentication.

    Args:
        current_user: Injected by the JWT dependency.

    Returns:
        Dictionary containing CPU, memory, and disk stats.
    """
    try:
        cpu_task = asyncio.create_task(_collect_cpu())
        mem_task = asyncio.create_task(_collect_memory())
        disk_task = asyncio.create_task(_collect_disk())
        cpu, memory, disk = await asyncio.gather(cpu_task, mem_task, disk_task)
        return {"cpu": {"percent": cpu}, "memory": memory, "disk": disk}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to collect system metrics",
        ) from exc
