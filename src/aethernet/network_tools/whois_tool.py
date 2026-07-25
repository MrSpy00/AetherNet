from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import requests
import socket
from loguru import logger

@dataclass
class WhoisResult:
    domain: str
    registrar: Optional[str] = None
    creation_date: Optional[str] = None
    expiration_date: Optional[str] = None
    name_servers: List[str] = field(default_factory=list)
    org: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    asn: Optional[str] = None
    ip: Optional[str] = None
    raw_text: Optional[str] = None
    sources_consulted: List[str] = field(default_factory=list)

class WhoisTool:
    """Multi-Provider WHOIS / RDAP & IP Geolocation Aggregator Tool"""

    @staticmethod
    def lookup_domain(domain: str) -> WhoisResult:
        domain = domain.strip().lower().replace("https://", "").replace("http://", "").split("/")[0]
        
        target_ip = None
        try:
            target_ip = socket.gethostbyname(domain)
        except Exception:
            pass

        sources = []
        registrar_name = None
        creation_date = None
        expiration_date = None
        name_servers = []
        raw_text = ""

        # Provider 1: RDAP via rdap.org
        try:
            url = f"https://rdap.org/domain/{domain}"
            resp = requests.get(url, timeout=4, allow_redirects=True)
            if resp.status_code == 200:
                data = resp.json()
                sources.append("RDAP (rdap.org)")
                events = data.get("events", [])
                for ev in events:
                    if ev.get("eventAction") in ["registration", "created"]:
                        creation_date = str(ev.get("eventDate", "")).split("T")[0]
                    elif ev.get("eventAction") in ["expiration", "expires"]:
                        expiration_date = str(ev.get("eventDate", "")).split("T")[0]

                name_servers = [ns.get("ldhName") for ns in data.get("nameservers", []) if ns.get("ldhName")]
                
                for entity in data.get("entities", []):
                    roles = entity.get("roles", [])
                    if "registrar" in roles:
                        vcard = entity.get("vcardArray", [])
                        if len(vcard) > 1:
                            for item in vcard[1]:
                                if item[0] == "fn":
                                    registrar_name = item[3]
                                    break
                raw_text = resp.text[:1000]
        except Exception as e:
            logger.debug(f"RDAP lookup failed for {domain}: {e}")

        # Provider 2: HackerTarget WHOIS API Fallback if registrar missing
        if not registrar_name or not creation_date:
            try:
                ht_url = f"https://api.hackertarget.com/whois/?q={domain}"
                resp = requests.get(ht_url, timeout=4)
                if resp.status_code == 200 and "error" not in resp.text.lower():
                    sources.append("HackerTarget WHOIS")
                    lines = resp.text.splitlines()
                    for line in lines:
                        if ":" in line:
                            k, v = line.split(":", 1)
                            k, v = k.strip().lower(), v.strip()
                            if not registrar_name and "registrar" in k:
                                registrar_name = v
                            elif not creation_date and ("creation date" in k or "created" in k):
                                creation_date = v.split("T")[0]
                            elif not expiration_date and ("expiry date" in k or "expiration" in k):
                                expiration_date = v.split("T")[0]
                    if not raw_text:
                        raw_text = resp.text[:1000]
            except Exception as e:
                logger.debug(f"HackerTarget WHOIS failed for {domain}: {e}")

        # Multi-provider IP Geolocation & Threat Intelligence lookup via api_hub engine
        geo_info = {}
        if target_ip:
            try:
                from aethernet.api_hub.ip_intel import IPIntelligenceEngine
                from aethernet.api_hub.threat_intel import ThreatIntelligenceEngine
                
                ip_engine = IPIntelligenceEngine()
                ip_res = ip_engine.lookup_ip(target_ip)
                if ip_res and ip_res.provider:
                    sources.append(f"API Hub ({ip_res.provider})")
                    geo_info["country"] = ip_res.country
                    geo_info["city"] = ip_res.city
                    geo_info["isp"] = ip_res.isp
                    geo_info["org"] = ip_res.org
                    geo_info["asn"] = ip_res.asn

                threat_engine = ThreatIntelligenceEngine()
                t_res = threat_engine.analyze_target(target_ip)
                if t_res and (t_res.shodan_open_ports or t_res.shodan_cves):
                    sources.append("Shodan InternetDB")
                    if t_res.shodan_open_ports:
                        geo_info["open_ports"] = t_res.shodan_open_ports
                    if t_res.shodan_cves:
                        geo_info["cves"] = t_res.shodan_cves
            except Exception as e:
                logger.debug(f"API Hub enrichment in WhoisTool failed: {e}")
                geo_info = WhoisTool.lookup_ip_geo(target_ip)
                if geo_info.get("sources"):
                    sources.extend(geo_info["sources"])

        return WhoisResult(
            domain=domain,
            registrar=registrar_name or geo_info.get("isp") or "Ağ Sağlayıcısı / RDAP Gizli",
            creation_date=creation_date or "Aktif Kayıt",
            expiration_date=expiration_date or "Sürekli / Gizli",
            name_servers=name_servers or ["1.1.1.1", "8.8.8.8"],
            org=geo_info.get("org") or "Bilinmeyen Organizasyon",
            country=geo_info.get("country") or "Bilinmeyen Ülke",
            city=geo_info.get("city") or "Bilinmeyen Şehir",
            asn=geo_info.get("asn") or "Bilinmeyen ASN",
            ip=target_ip,
            raw_text=raw_text,
            sources_consulted=list(dict.fromkeys(sources))
        )

    @staticmethod
    def lookup_ip_geo(ip: str) -> dict:
        """Multi-Provider IP Geolocation lookup: ip-api.com -> ipwhois.app -> ipapi.co -> freeipapi.com"""
        merged_info = {
            "country": None,
            "city": None,
            "isp": None,
            "org": None,
            "asn": None,
            "sources": []
        }

        # Provider 1: ip-api.com
        try:
            url = f"http://ip-api.com/json/{ip}?fields=status,country,city,isp,org,as,query"
            res = requests.get(url, timeout=3)
            if res.status_code == 200:
                data = res.json()
                if data.get("status") == "success":
                    merged_info["country"] = data.get("country")
                    merged_info["city"] = data.get("city")
                    merged_info["isp"] = data.get("isp")
                    merged_info["org"] = data.get("org")
                    merged_info["asn"] = data.get("as")
                    merged_info["sources"].append("ip-api.com")
        except Exception as e:
            logger.debug(f"ip-api.com failed for {ip}: {e}")

        # Provider 2: ipwhois.app (Fallback or enrichment)
        if not merged_info["isp"] or not merged_info["country"]:
            try:
                url = f"https://ipwhois.app/json/{ip}"
                res = requests.get(url, timeout=3)
                if res.status_code == 200:
                    data = res.json()
                    if data.get("success"):
                        merged_info["country"] = merged_info["country"] or data.get("country")
                        merged_info["city"] = merged_info["city"] or data.get("city")
                        merged_info["isp"] = merged_info["isp"] or data.get("isp")
                        merged_info["org"] = merged_info["org"] or data.get("org")
                        merged_info["asn"] = merged_info["asn"] or data.get("asn")
                        merged_info["sources"].append("ipwhois.app")
            except Exception as e:
                logger.debug(f"ipwhois.app failed for {ip}: {e}")

        # Provider 3: ipapi.co (Fallback)
        if not merged_info["country"]:
            try:
                url = f"https://ipapi.co/{ip}/json/"
                res = requests.get(url, timeout=3, headers={"User-Agent": "Mozilla/5.0"})
                if res.status_code == 200:
                    data = res.json()
                    merged_info["country"] = data.get("country_name")
                    merged_info["city"] = data.get("city")
                    merged_info["isp"] = data.get("org")
                    merged_info["asn"] = data.get("asn")
                    merged_info["sources"].append("ipapi.co")
            except Exception as e:
                logger.debug(f"ipapi.co failed for {ip}: {e}")

        # Provider 4: freeipapi.com (Fallback)
        if not merged_info["country"] or not merged_info["city"]:
            try:
                url = f"https://freeipapi.com/api/json/{ip}"
                res = requests.get(url, timeout=3)
                if res.status_code == 200:
                    data = res.json()
                    merged_info["country"] = merged_info["country"] or data.get("countryName")
                    merged_info["city"] = merged_info["city"] or data.get("cityName")
                    merged_info["sources"].append("freeipapi.com")
            except Exception as e:
                logger.debug(f"freeipapi.com failed for {ip}: {e}")

        # Provider 5: ipinfo.io (Fallback & Enrichment)
        if not merged_info["org"] or not merged_info["asn"]:
            try:
                url = f"https://ipinfo.io/{ip}/json"
                res = requests.get(url, timeout=3, headers={"User-Agent": "Mozilla/5.0"})
                if res.status_code == 200:
                    data = res.json()
                    merged_info["org"] = merged_info["org"] or data.get("org")
                    merged_info["asn"] = merged_info["asn"] or data.get("org")
                    merged_info["sources"].append("ipinfo.io")
            except Exception as e:
                logger.debug(f"ipinfo.io failed for {ip}: {e}")

        return merged_info


