import subprocess
import re
import sys
from dataclasses import dataclass
from typing import List, Optional
from loguru import logger

@dataclass
class PingResult:
    target: str
    sent: int
    received: int
    loss_percent: float
    min_ms: float
    max_ms: float
    avg_ms: float
    jitter_ms: float
    replies: List[float]

class PingTool:
    """Tekli veya sürekli ICMP/System Ping aracı"""

    @staticmethod
    def ping(target: str, count: int = 4, timeout_sec: int = 2) -> PingResult:
        replies: List[float] = []
        
        if sys.platform == "win32":
            cmd = ["ping", "-n", str(count), "-w", str(timeout_sec * 1000), target]
        else:
            cmd = ["ping", "-c", str(count), "-W", str(timeout_sec), target]

        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            out = res.stdout

            # Parse latency values from output
            if sys.platform == "win32":
                times = re.findall(r"(?:time|zaman)[=<](\d+)ms", out, re.IGNORECASE)
                replies = [float(t) for t in times]
            else:
                times = re.findall(r"time=(\d+(?:\.\d+)?)", out)
                replies = [float(t) for t in times]

        except Exception as e:
            logger.error(f"Ping execution error: {e}")

        received = len(replies)
        loss = round(((count - received) / count) * 100, 1) if count > 0 else 100.0

        if replies:
            min_ms = min(replies)
            max_ms = max(replies)
            avg_ms = round(sum(replies) / len(replies), 1)
            # Simple jitter calculation (average variance between consecutive pings)
            jitter = 0.0
            if len(replies) > 1:
                diffs = [abs(replies[i] - replies[i-1]) for i in range(1, len(replies))]
                jitter = round(sum(diffs) / len(diffs), 1)
        else:
            min_ms = max_ms = avg_ms = jitter = 0.0

        return PingResult(
            target=target,
            sent=count,
            received=received,
            loss_percent=loss,
            min_ms=min_ms,
            max_ms=max_ms,
            avg_ms=avg_ms,
            jitter_ms=jitter,
            replies=replies
        )
