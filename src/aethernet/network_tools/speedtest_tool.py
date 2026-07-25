import sys
import io
from dataclasses import dataclass
from typing import Optional
from loguru import logger

class DummyStream(io.StringIO):
    def fileno(self):
        return 1
    def isatty(self):
        return False

@dataclass
class SpeedtestResult:
    download_mbps: float
    upload_mbps: float
    ping_ms: float
    server_name: str
    client_ip: str

class SpeedtestTool:
    """Bandwidth Speedtest tool using speedtest-cli with closest server auto-discovery"""

    @staticmethod
    def run_test() -> Optional[SpeedtestResult]:
        orig_stdout = sys.stdout
        orig_stderr = sys.stderr

        try:
            # Prevent 'NoneType' object has no attribute 'fileno' crash in PyInstaller --noconsole
            if sys.stdout is None:
                sys.stdout = DummyStream()
            if sys.stderr is None:
                sys.stderr = DummyStream()

            import speedtest
            st = speedtest.Speedtest(secure=True)
            
            # Fetch closest servers and evaluate ping to select absolute lowest-latency node
            logger.info("En yakın ve en hızlı Speedtest sunucuları aranıyor...")
            st.get_servers([])
            best = st.get_best_server()

            sponsor = best.get("sponsor", "Otomatik Sunucu")
            city = best.get("name", "Bölgesel Node")
            country = best.get("country", "")
            server_info = f"{sponsor} ({city}, {country})" if country else f"{sponsor} ({city})"

            client_ip = st.config.get("client", {}).get("ip", "Bilinmiyor")

            logger.info(f"Seçilen en yakın sunucu: {server_info} | Latency: {best.get('latency', 0):.1f} ms")

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
        finally:
            sys.stdout = orig_stdout
            sys.stderr = orig_stderr
