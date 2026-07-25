"""Wi-Fi QR Code Generator for easy sharing of network credentials."""

import base64
import io
from typing import Optional


class WiFiQRGenerator:
    """Generates standard Wi-Fi connection QR codes and base64 PNG images."""

    @staticmethod
    def generate_qr_payload(ssid: str, password: str = "", auth_type: str = "WPA") -> str:
        """Construct standard Wi-Fi QR payload.
        Format: WIFI:S:<SSID>;T:<WPA|WEP|nopass>;P:<PASSWORD>;;
        """
        security = auth_type.upper()
        if security not in ["WPA", "WEP", "NOPASS"]:
            security = "WPA"
        if not password or security == "NOPASS":
            return f"WIFI:S:{ssid};T:nopass;;"
        return f"WIFI:S:{ssid};T:{security};P:{password};;"

    @staticmethod
    def generate_qr_png_base64(ssid: str, password: str = "", auth_type: str = "WPA") -> Optional[str]:
        """Generate base64 encoded PNG data URI for QR payload using qrcode library if available."""
        payload = WiFiQRGenerator.generate_qr_payload(ssid, password, auth_type)
        try:
            import qrcode
            qr = qrcode.QRCode(version=1, box_size=8, border=2)
            qr.add_data(payload)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            b64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
            return f"data:image/png;base64,{b64_str}"
        except ImportError:
            return None
