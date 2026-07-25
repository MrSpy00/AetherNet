"""DNS Leak Checker to identify if DNS requests bypass active VPN tunnel or resolve via unexpected servers."""

import socket
from typing import List, Dict


class DNSLeakChecker:
    """Verifies DNS query resolvers and detects DNS leaks."""

    KNOWN_SAFE_RESOLVERS = [
        "1.1.1.1", "1.0.0.1",      # Cloudflare
        "8.8.8.8", "8.8.4.4",      # Google
        "9.9.9.9", "149.112.112.112", # Quad9
        "208.67.222.222", "208.67.220.220" # OpenDNS
    ]

    def __init__(self):
        pass

    def get_system_dns_servers(self) -> List[str]:
        """Attempt to query system configured DNS servers."""
        resolvers = []
        try:
            import dns.resolver
            resolver = dns.resolver.Resolver()
            resolvers = list(resolver.nameservers)
        except Exception:
            pass
        return resolvers

    def check_leak_status(self, is_vpn_active: bool = False) -> Dict[str, any]:
        """Check system DNS settings and flag potential DNS leaks."""
        resolvers = self.get_system_dns_servers()
        alerts = []
        has_leak = False

        if is_vpn_active:
            # If VPN is active but DNS server is local ISP / gateway address, likely a leak
            for res in resolvers:
                if res.startswith("192.168.") or res.startswith("10.") or res.startswith("172.16."):
                    has_leak = True
                    alerts.append(f"DNS Leak Warning: VPN is active, but DNS resolver is pointing to local gateway/router IP ({res}).")

        return {
            "resolvers": resolvers,
            "has_leak": has_leak,
            "alerts": alerts,
            "is_vpn_active": is_vpn_active
        }
