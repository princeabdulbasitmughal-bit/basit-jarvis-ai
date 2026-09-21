"""
Core implementation of an asynchronous ICMP ping utility.

The module provides:
* :class:`PingResult` – a dataclass describing a single ping outcome.
* :func:`async_ping` – an async function that sends an ICMP Echo Request and
  awaits the matching Echo Reply, returning a :class:`PingResult`.

The implementation uses raw sockets, therefore the process must have
administrative/root privileges on most operating systems.
"""

from __future__ import annotations

import asyncio
import logging
import os
import socket
import struct
import sys
import time
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def _checksum(source: bytes) -> int:
    """
    Compute the Internet Checksum of the supplied data.

    Args:
        source: The data over which to compute the checksum.

    Returns:
        The checksum as an unsigned 16‑bit integer.
    """
    sum_ = 0
    count_to = (len(source) // 2) * 2
    count = 0

    # Sum all the short words together
    while count < count_to:
        this_val = source[count + 1] * 256 + source[count]
        sum_ = sum_ + this_val
        sum_ = sum_ & 0xffffffff  # Keep it 32‑bit
        count += 2

    # Handle odd byte
    if count_to < len(source):
        sum_ += source[-1]
        sum_ = sum_ & 0xffffffff

    # Fold 32‑bit sum to 16 bits
    sum_ = (sum_ >> 16) + (sum_ & 0xffff)
    sum_ = sum_ + (sum_ >> 16)

    answer = ~sum_ & 0xffff
    # Swap bytes. On little‑endian machines the checksum must be byte‑swapped.
    answer = socket.htons(answer)

    return answer


def _build_packet(identifier: int, sequence_number: int, payload_size: int = 56) -> bytes:
    """
    Build a raw ICMP Echo Request packet.

    Args:
        identifier: Identifier to match request/reply (usually PID).
        sequence_number: Incrementing sequence number.
        payload_size: Number of bytes for the payload (default 56, like classic ping).

    Returns:
        The complete ICMP packet ready to be sent over a raw socket.
    """
    # Header: Type (8), Code (0), Checksum (0 initially), Identifier, Sequence Number
    header = struct.pack("!BBHHH", 8, 0, 0, identifier, sequence_number)

    # Payload: just a bunch of dummy bytes (could be timestamps, etc.)
    payload = bytes((i & 0xff for i in range(payload_size)))

    # Compute checksum on the header + payload
    checksum = _checksum(header + payload)

    # Re-pack header with correct checksum
    header = struct.pack("!BBHHH", 8, 0, checksum, identifier, sequence_number)

    return header + payload


def _parse_reply(packet: bytes, identifier: int, sequence_number: int) -> bool:
    """
    Verify that a received ICMP packet matches the request.

    Args:
        packet: The raw packet received from the socket.
        identifier: Expected identifier.
        sequence_number: Expected sequence number.

    Returns:
        ``True`` if the packet is a matching Echo Reply, ``False`` otherwise.
    """
    # The IP header is variable length; the first 4 bits contain the header length.
    ip_header_len = (packet[0] & 0x0F) * 4
    icmp_header = packet[ip_header_len : ip_header_len + 8]

    icmp_type, icmp_code, _, recv_id, recv_seq = struct.unpack("!BBHHH", icmp_header)

    # ICMP Echo Reply is type 0, code 0
    return icmp_type == 0 and icmp_code == 0 and recv_id == identifier and recv_seq == sequence_number


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #

@dataclass
class PingResult:
    """
    Result of a single ping attempt.

    Attributes:
        success: Whether a reply was received within the timeout.
        rtt_ms: Round‑trip time in milliseconds (``None`` if unsuccessful).
        error: Optional error message if the ping failed.
        target: The IP address (or hostname) that was pinged.
    """
    success: bool
    rtt_ms: Optional[float]
    error: Optional[str]
    target: str


async def async_ping(
    target: str,
    timeout: float = 1.0,
    payload_size: int = 56,
    ttl: int = 64,
) -> PingResult:
    """
    Send a single ICMP Echo Request to *target* and wait for the reply.

    The function runs the blocking socket operations in a thread pool executor,
    making it safe to call from an ``asyncio`` event loop.

    Args:
        target: Hostname or IPv4 address to ping.
        timeout: Maximum time to wait for a reply, in seconds.
        payload_size: Number of bytes in the ICMP payload.
        ttl: Time‑to‑Live for the outgoing packet.

    Returns:
        A :class:`PingResult` describing the outcome.

    Raises:
        PermissionError: If the process lacks privileges to open a raw socket.
        OSError: For other socket‑related errors.
    """
    loop = asyncio.get_running_loop()
    identifier = os.getpid() & 0xFFFF
    sequence_number = int(time.time() * 1000) & 0xFFFF  # pseudo‑random per call

    try:
        # Resolve the target to an IPv4 address
        dest_addr = socket.gethostbyname(target)
    except socket.gaierror as exc:
        logger.error("Failed to resolve %s: %s", target, exc)
        return PingResult(False, None, f"Resolution error: {exc}", target)

    # Use a thread pool to avoid blocking the event loop
    try:
        return await loop.run_in_executor(
            None,
            _sync_ping,
            dest_addr,
            identifier,
            sequence_number,
            timeout,
            payload_size,
            ttl,
            target,
        )
    except PermissionError as exc:
        logger.error("Insufficient privileges for raw socket: %s", exc)
        raise
    except Exception as exc:  # pragma: no cover – unexpected errors
        logger.exception("Unexpected error during ping")
        return PingResult(False, None, str(exc), target)


def _sync_ping(
    dest_addr: str,
    identifier: int,
    sequence_number: int,
    timeout: float,
    payload_size: int,
    ttl: int,
    target_display: str,
) -> PingResult:
    """
    Blocking implementation used by :func:`async_ping`.

    This function is deliberately kept private; callers should use the async wrapper.
    """
    try:
        # Create raw socket (requires root/administrator)
        with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as sock:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
            sock.settimeout(timeout)

            packet = _build_packet(identifier, sequence_number, payload_size)

            send_time = time.time()
            sock.sendto(packet, (dest_addr, 1))

            while True:
                try:
                    recv_packet, addr = sock.recvfrom(1024)
                except socket.timeout:
                    logger.warning("Ping to %s timed out after %.2f s", target_display, timeout)
                    return PingResult(False, None, "Request timed out", target_display)

                if addr[0] == dest_addr and _parse_reply(recv_packet, identifier, sequence_number):
                    rtt = (time.time() - send_time) * 1000.0
                    logger.info("Reply from %s: seq=%d time=%.2f ms", dest_addr, sequence_number, rtt)
                    return PingResult(True, rtt, None, target_display)

                # If we received something else, continue waiting (until timeout)
    except PermissionError as exc:
        raise PermissionError(
            "Raw sockets require administrative/root privileges. "
            "Run the program as root or with sudo."
        ) from exc
    except OSError as exc:
        logger.error("Socket error while pinging %s: %s", target_display, exc)
        return PingResult(False, None, f"Socket error: {exc}", target_display)
