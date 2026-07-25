"""SLA & ISP Network Quality Tracker for logging latency, packet loss, and connection outages."""

import time
from dataclasses import dataclass, asdict
from typing import List, Dict
import json


@dataclass
class SLAMetric:
    timestamp: float
    target: str
    latency_ms: float
    packet_loss_pct: float
    is_online: bool


class SLAMonitor:
    """Tracks latency and uptime compliance over time."""

    def __init__(self, target_host: str = "8.8.8.8"):
        self.target_host = target_host
        self.history: List[SLAMetric] = []

    def record_ping_sample(self, latency_ms: float, packet_loss_pct: float) -> SLAMetric:
        """Record ping sample."""
        is_online = packet_loss_pct < 100.0
        metric = SLAMetric(
            timestamp=time.time(),
            target=self.target_host,
            latency_ms=latency_ms,
            packet_loss_pct=packet_loss_pct,
            is_online=is_online
        )
        self.history.append(metric)
        # Limit buffer to 1000 samples
        if len(self.history) > 1000:
            self.history.pop(0)
        return metric

    def get_summary(self) -> Dict[str, any]:
        """Compute uptime percentage and average metrics."""
        if not self.history:
            return {"uptime_pct": 100.0, "avg_latency_ms": 0.0, "avg_loss_pct": 0.0, "samples_count": 0}

        total_samples = len(self.history)
        online_samples = sum(1 for m in self.history if m.is_online)
        avg_latency = sum(m.latency_ms for m in self.history if m.is_online) / max(1, online_samples)
        avg_loss = sum(m.packet_loss_pct for m in self.history) / total_samples

        return {
            "uptime_pct": round((online_samples / total_samples) * 100.0, 2),
            "avg_latency_ms": round(avg_latency, 2),
            "avg_loss_pct": round(avg_loss, 2),
            "samples_count": total_samples
        }

    def export_json(self) -> str:
        """Export history log to JSON string."""
        return json.dumps([asdict(m) for m in self.history], indent=2)
