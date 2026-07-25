from dataclasses import dataclass
from typing import Optional
from loguru import logger

@dataclass
class SpeedtestResult:
    download_mbps: float
    upload_mbps: float
    ping_ms: float
    server_name: str
    client_ip: str

class SpeedtestTool:
    """Bandwidth Speedtest tool using speedtest-cli or fallback simulation"""

    @staticmethod
    def run_test() -> Optional[SpeedtestResult]:
        try:
            import speedtest
            st = speedtest.Speedtest(secure=True)
            st.get_best_server()
            server_info = st.best.get("name", "Unknown Server")
            client_ip = st.config.get("client", {}).get("ip", "Unknown IP")

            download_bps = st.download()
            upload_bps = st.upload()

            dl_mbps = round(download_bps / 1_000_000, 2)
            ul_mbps = round(upload_bps / 1_000_000, 2)
            ping = round(st.results.ping, 1)

            return SpeedtestResult(
                download_mbps=dl_mbps,
                upload_mbps=ul_mbps,
                ping_ms=ping,
                server_name=server_info,
                client_ip=client_ip
            )
        except Exception as e:
            logger.error(f"Speedtest execution failed: {e}")
            return None
