"""
Offline URL Feature Extraction and Heuristic Security Analysis Module
Performs 100% local, safe inspection of hyperlinks without external network requests.
"""

import re
from urllib.parse import urlparse
from typing import List, Dict, Any, Optional

# Known URL shortener domains
SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "goo.gl", "ow.ly", "t.co", "is.gd",
    "buff.ly", "adf.ly", "bit.do", "cutt.ly", "rb.gy", "shorturl.at"
}

# Suspicious TLDs commonly seen in low-cost bulk phishing campaigns
SUSPICIOUS_TLDS = {
    "xyz", "top", "work", "loan", "click", "buzz", "gq", "ml", "cf", "ga", "tk", "fit", "rest", "zip"
}

# Regex to detect IP address as host (IPv4)
IPV4_REGEX = re.compile(
    r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
)


def extract_urls(text: str) -> List[str]:
    """
    Extracts all URLs and http/https hyperlinks found in plain text.
    """
    if not isinstance(text, str) or not text:
        return []
    pattern = r"https?://[^\s<>\"'()]+|www\.[^\s<>\"'()]+"
    matches = re.findall(pattern, text)
    cleaned = []
    for m in matches:
        m = m.rstrip(".,;!?:)")
        if m not in cleaned:
            cleaned.append(m)
    return cleaned


def analyze_url(url: str) -> Dict[str, Any]:
    """
    Analyzes an individual URL using offline static heuristics.
    Never initiates network requests.
    """
    url_stripped = url.strip()
    if not (url_stripped.startswith("http://") or url_stripped.startswith("https://")):
        url_parsed = urlparse("http://" + url_stripped)
    else:
        url_parsed = urlparse(url_stripped)

    hostname = (url_parsed.hostname or "").lower()
    path = url_parsed.path or ""

    flags = []
    points = 0.0

    # 1. IP address in hostname
    has_ip = bool(IPV4_REGEX.match(hostname))
    if has_ip:
        flags.append("Host is a direct raw IP address rather than a registered domain")
        points += 0.35

    # 2. URL Length check
    url_length = len(url_stripped)
    if url_length > 75:
        flags.append(f"Unusually long URL structure ({url_length} characters)")
        points += 0.15

    # 3. Excessive subdomains
    domain_parts = [p for p in hostname.split(".") if p]
    subdomain_count = max(0, len(domain_parts) - 2)
    if subdomain_count >= 3:
        flags.append(f"Excessive subdomain layering ({subdomain_count} subdomains)")
        points += 0.20

    # 4. Use of URL shorteners
    is_shortener = hostname in SHORTENER_DOMAINS or any(hostname.endswith("." + s) for s in SHORTENER_DOMAINS)
    if is_shortener:
        flags.append("Employs URL shortening service concealing destination target")
        points += 0.25

    # 5. Suspicious URL encoding and @ symbol
    has_at_symbol = "@" in url_stripped
    has_hex_encoding = bool(re.search(r"%[0-9a-fA-F]{2}", url_stripped))
    if has_at_symbol:
        flags.append("Contains '@' symbol in URL (often used to obscure the true target host)")
        points += 0.30
    if has_hex_encoding:
        flags.append("Uses hex-encoded percent formatting (%xx) to obscure characters")
        points += 0.15

    # 6. Lookalike Punycode (IDN Homograph attacks)
    has_punycode = "xn--" in hostname
    if has_punycode:
        flags.append("Punycode (xn--) detected; possible internationalized homograph impersonation")
        points += 0.30

    # 7. Suspicious / high-risk TLD
    tld = domain_parts[-1] if domain_parts else ""
    is_suspicious_tld = tld in SUSPICIOUS_TLDS
    if is_suspicious_tld:
        flags.append(f"Contains high-abuse Top-Level Domain (.{tld})")
        points += 0.20

    # 8. Suspicious keywords in URL path or hostname
    suspicious_url_keywords = ["login", "verify", "secure", "banking", "update", "account", "confirm", "wallet"]
    found_keywords = [kw for kw in suspicious_url_keywords if kw in url_stripped.lower() and kw not in hostname]
    if found_keywords:
        flags.append(f"Deceptive path keywords observed: {', '.join(found_keywords)}")
        points += 0.15

    heuristic_risk = min(1.0, points)

    return {
        "url": url_stripped,
        "hostname": hostname,
        "length": url_length,
        "has_ip_host": has_ip,
        "subdomain_count": subdomain_count,
        "is_shortener": is_shortener,
        "has_suspicious_encoding": has_hex_encoding or has_at_symbol,
        "has_punycode": has_punycode,
        "tld": tld,
        "risk_score": round(heuristic_risk, 3),
        "flags": flags
    }


def analyze_email_urls(
    email_text: str,
    additional_urls: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Extracts and evaluates all hyperlinks found within the email.
    """
    extracted = extract_urls(email_text)
    if additional_urls:
        for u in additional_urls:
            if u and u.strip() and u.strip() not in extracted:
                extracted.append(u.strip())

    analyzed_urls = [analyze_url(u) for u in extracted]

    max_risk = max([u["risk_score"] for u in analyzed_urls], default=0.0)
    all_flags = []
    for u in analyzed_urls:
        all_flags.extend(u["flags"])

    # Deduplicate flags
    unique_flags = list(dict.fromkeys(all_flags))

    return {
        "total_urls_found": len(analyzed_urls),
        "max_url_risk_score": max_risk,
        "aggregated_flags": unique_flags,
        "url_details": analyzed_urls
    }
