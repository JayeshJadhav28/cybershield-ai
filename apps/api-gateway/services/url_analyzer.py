"""
URL analysis service — fully self-contained heuristic engine.
No ML model dependencies. Analyzes URLs for phishing indicators.
"""

import re
import time
import math
import socket
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, parse_qs, unquote

logger = logging.getLogger(__name__)

# ── Known-bad / suspicious lists ──────────────────────────────────────

SUSPICIOUS_TLDS = {
    ".tk", ".ml", ".ga", ".cf", ".gq",   # free TLDs
    ".buzz", ".top", ".xyz", ".club", ".online", ".site", ".icu",
    ".work", ".click", ".link", ".info", ".pw", ".cc",
    ".ws", ".loan", ".racing", ".win", ".download", ".stream",
    ".date", ".faith", ".review", ".party", ".science", ".trade",
    ".bid", ".accountant", ".cricket",
}

URL_SHORTENERS = {
    "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd",
    "buff.ly", "adf.ly", "bit.do", "mcaf.ee", "su.pr", "db.tt",
    "qr.ae", "cur.lv", "ity.im", "lnkd.in", "shorte.st", "v.gd",
    "rb.gy", "cutt.ly", "shorturl.at", "rebrand.ly",
}

PHISHING_KEYWORDS = [
    "login", "signin", "sign-in", "verify", "verification",
    "secure", "security", "account", "update", "confirm",
    "banking", "password", "credential", "suspend", "alert",
    "unusual", "activity", "restore", "unlock", "validate",
    "authenticate", "wallet", "paypal", "apple", "microsoft",
    "amazon", "netflix", "facebook", "instagram", "google",
    "ebay", "chase", "wells", "citi", "hsbc",
]

LEGITIMATE_DOMAINS = {
    "google.com", "youtube.com", "facebook.com", "amazon.com",
    "apple.com", "microsoft.com", "github.com", "stackoverflow.com",
    "wikipedia.org", "twitter.com", "x.com", "linkedin.com",
    "reddit.com", "netflix.com", "paypal.com", "ebay.com",
    "instagram.com", "whatsapp.com", "zoom.us",
}


@dataclass
class URLAnalysisResult:
    """Result from URL analysis."""
    probability: float
    confidence: float
    flags: List[str] = field(default_factory=list)
    features: Dict[str, Any] = field(default_factory=dict)
    highlights: List[Dict] = field(default_factory=list)
    rule_score: float = 0.0
    processing_time_ms: int = 0


class URLAnalyzer:
    """Analyzes URLs for phishing and malicious indicators using heuristics."""

    def analyze(self, url: str) -> URLAnalysisResult:
        """Analyze a single URL with comprehensive heuristic checks."""
        start_time = time.time()
        flags: List[str] = []
        features: Dict[str, Any] = {}
        highlights: List[Dict] = []
        score = 0.0  # 0 = safe, 1 = malicious

        # ── Normalise ──
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            parsed = urlparse(url)
        except Exception:
            return URLAnalysisResult(
                probability=0.8,
                rule_score=0.8,
                confidence=0.9,
                flags=["invalid_url_format"],
                features={"error": "Could not parse URL"},
                processing_time_ms=int((time.time() - start_time) * 1000),
            )

        hostname = (parsed.hostname or "").lower()
        path = parsed.path.lower()
        query = parsed.query.lower()
        full_url_lower = url.lower()

        features["scheme"] = parsed.scheme
        features["hostname"] = hostname
        features["path"] = parsed.path
        features["query"] = parsed.query
        features["url_length"] = len(url)

        # ─────────────────────────────────────────────────────────
        # 1. HTTPS check
        # ─────────────────────────────────────────────────────────
        if parsed.scheme == "http":
            score += 0.10
            flags.append("no_https")
            highlights.append({
                "type": "scheme",
                "value": "http",
                "reason": "Connection is not encrypted (HTTP)",
            })
        features["is_https"] = parsed.scheme == "https"

        # ─────────────────────────────────────────────────────────
        # 2. IP address instead of domain
        # ─────────────────────────────────────────────────────────
        is_ip = self._is_ip_address(hostname)
        features["uses_ip_address"] = is_ip
        if is_ip:
            score += 0.30
            flags.append("ip_address_url")
            highlights.append({
                "type": "hostname",
                "value": hostname,
                "reason": "URL uses IP address instead of domain name",
            })

        # ─────────────────────────────────────────────────────────
        # 3. Suspicious TLD
        # ─────────────────────────────────────────────────────────
        tld = self._get_tld(hostname)
        features["tld"] = tld
        if tld in SUSPICIOUS_TLDS:
            score += 0.15
            flags.append("suspicious_tld")
            highlights.append({
                "type": "tld",
                "value": tld,
                "reason": f"TLD '{tld}' is commonly used in phishing",
            })

        # ─────────────────────────────────────────────────────────
        # 4. URL length
        # ─────────────────────────────────────────────────────────
        url_len = len(url)
        if url_len > 150:
            score += 0.10
            flags.append("long_url")
        if url_len > 250:
            score += 0.05
            flags.append("very_long_url")
        features["url_length_category"] = (
            "short" if url_len < 50
            else "normal" if url_len < 100
            else "long" if url_len < 200
            else "very_long"
        )

        # ─────────────────────────────────────────────────────────
        # 5. Subdomain count
        # ─────────────────────────────────────────────────────────
        subdomain_count = self._count_subdomains(hostname)
        features["subdomain_count"] = subdomain_count
        if subdomain_count >= 3:
            score += 0.10
            flags.append("excessive_subdomains")
        if subdomain_count >= 5:
            score += 0.10
            flags.append("highly_nested_subdomains")

        # ─────────────────────────────────────────────────────────
        # 6. URL shortener
        # ─────────────────────────────────────────────────────────
        if hostname in URL_SHORTENERS:
            score += 0.15
            flags.append("url_shortener")
            highlights.append({
                "type": "hostname",
                "value": hostname,
                "reason": "URL shortener hides the real destination",
            })
        features["is_shortener"] = hostname in URL_SHORTENERS

        # ─────────────────────────────────────────────────────────
        # 7. Non-standard port
        # ─────────────────────────────────────────────────────────
        port = parsed.port
        features["port"] = port
        if port and port not in (80, 443, None):
            score += 0.15
            flags.append("non_standard_port")
            highlights.append({
                "type": "port",
                "value": str(port),
                "reason": f"Non-standard port :{port}",
            })

        # ─────────────────────────────────────────────────────────
        # 8. Special characters: @, //, -, encoded chars
        # ─────────────────────────────────────────────────────────
        if "@" in parsed.netloc:
            score += 0.25
            flags.append("at_symbol_in_url")
            highlights.append({
                "type": "character",
                "value": "@",
                "reason": "'@' in URL can redirect to a different domain",
            })

        dash_count = hostname.count("-")
        features["hostname_dashes"] = dash_count
        if dash_count >= 3:
            score += 0.10
            flags.append("many_hyphens_in_hostname")

        dot_count = hostname.count(".")
        features["hostname_dots"] = dot_count

        # Double slash in path (not at start)
        if "//" in path[1:]:
            score += 0.05
            flags.append("double_slash_in_path")

        # Percent-encoded characters in hostname
        if "%" in parsed.netloc:
            score += 0.15
            flags.append("encoded_hostname")

        # ─────────────────────────────────────────────────────────
        # 9. Phishing keywords
        # ─────────────────────────────────────────────────────────
        keyword_hits = []
        for kw in PHISHING_KEYWORDS:
            if kw in full_url_lower:
                keyword_hits.append(kw)
        features["phishing_keywords"] = keyword_hits
        if keyword_hits:
            kw_score = min(len(keyword_hits) * 0.05, 0.20)
            score += kw_score
            flags.append(f"phishing_keywords_found ({len(keyword_hits)})")

        # ─────────────────────────────────────────────────────────
        # 10. Punycode / IDN homograph attack
        # ─────────────────────────────────────────────────────────
        if hostname.startswith("xn--") or any(
            part.startswith("xn--") for part in hostname.split(".")
        ):
            score += 0.25
            flags.append("punycode_domain")
            highlights.append({
                "type": "hostname",
                "value": hostname,
                "reason": "Punycode domain may be a homograph attack",
            })
        features["is_punycode"] = "xn--" in hostname

        # ─────────────────────────────────────────────────────────
        # 11. Data URI / javascript
        # ─────────────────────────────────────────────────────────
        if url.lower().startswith(("data:", "javascript:")):
            score = 0.95
            flags.append("dangerous_uri_scheme")

        # ─────────────────────────────────────────────────────────
        # 12. Brand impersonation in subdomain
        # ─────────────────────────────────────────────────────────
        brand_impersonation = self._check_brand_impersonation(hostname)
        if brand_impersonation:
            score += 0.20
            flags.append(f"possible_brand_impersonation: {brand_impersonation}")
            highlights.append({
                "type": "hostname",
                "value": hostname,
                "reason": f"Possible impersonation of '{brand_impersonation}'",
            })
        features["brand_impersonation"] = brand_impersonation

        # ─────────────────────────────────────────────────────────
        # 13. Entropy of hostname (random-looking domains)
        # ─────────────────────────────────────────────────────────
        hostname_no_tld = hostname.rsplit(".", 1)[0] if "." in hostname else hostname
        entropy = self._shannon_entropy(hostname_no_tld)
        features["hostname_entropy"] = round(entropy, 3)
        if entropy > 4.0:
            score += 0.10
            flags.append("high_entropy_hostname")

        # ─────────────────────────────────────────────────────────
        # 14. Legitimate domain bonus (reduce false positives)
        # ─────────────────────────────────────────────────────────
        base_domain = self._get_base_domain(hostname)
        features["base_domain"] = base_domain
        if base_domain in LEGITIMATE_DOMAINS:
            score = max(score - 0.40, 0.0)
            if "possible_brand_impersonation" in str(flags):
                # Remove brand impersonation flag for legit domains
                flags = [f for f in flags if "brand_impersonation" not in f]
            features["is_known_legitimate"] = True
        else:
            features["is_known_legitimate"] = False

        # ─────────────────────────────────────────────────────────
        # 15. Query string analysis
        # ─────────────────────────────────────────────────────────
        if query:
            qs_params = parse_qs(parsed.query)
            features["query_param_count"] = len(qs_params)
            # Check for redirect params
            redirect_params = {"redirect", "url", "next", "return", "goto", "dest", "rurl"}
            for param in qs_params:
                if param.lower() in redirect_params:
                    score += 0.10
                    flags.append(f"redirect_param: {param}")
                    break

        # ── Clamp final score ──
        final_score = round(min(max(score, 0.0), 1.0), 4)

        # Confidence is higher when more signals are detected
        signal_count = len(flags)
        confidence = min(0.55 + signal_count * 0.05, 0.95)

        processing_time_ms = int((time.time() - start_time) * 1000)

        return URLAnalysisResult(
            probability=final_score,
            rule_score=final_score,
            confidence=round(confidence, 2),
            flags=flags,
            features=features,
            highlights=highlights,
            processing_time_ms=processing_time_ms,
        )

    # ── Helper methods ────────────────────────────────────────────

    @staticmethod
    def _is_ip_address(hostname: str) -> bool:
        """Check if hostname is an IP address."""
        # Remove brackets for IPv6
        h = hostname.strip("[]")
        try:
            socket.inet_pton(socket.AF_INET, h)
            return True
        except (socket.error, OSError):
            pass
        try:
            socket.inet_pton(socket.AF_INET6, h)
            return True
        except (socket.error, OSError):
            pass
        # Also check numeric-only patterns like 192.168.1.1
        return bool(re.match(r"^\d{1,3}(\.\d{1,3}){3}$", hostname))

    @staticmethod
    def _get_tld(hostname: str) -> str:
        """Extract TLD from hostname."""
        parts = hostname.rsplit(".", 1)
        return f".{parts[-1]}" if len(parts) > 1 else ""

    @staticmethod
    def _get_base_domain(hostname: str) -> str:
        """Get base domain (last two parts)."""
        parts = hostname.split(".")
        if len(parts) >= 2:
            return ".".join(parts[-2:])
        return hostname

    @staticmethod
    def _count_subdomains(hostname: str) -> int:
        """Count subdomains (parts before the base domain)."""
        parts = hostname.split(".")
        return max(0, len(parts) - 2)

    @staticmethod
    def _shannon_entropy(text: str) -> float:
        """Calculate Shannon entropy of a string."""
        if not text:
            return 0.0
        freq: Dict[str, int] = {}
        for ch in text:
            freq[ch] = freq.get(ch, 0) + 1
        length = len(text)
        entropy = 0.0
        for count in freq.values():
            p = count / length
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy

    @staticmethod
    def _check_brand_impersonation(hostname: str) -> Optional[str]:
        """Check if a well-known brand appears in subdomain of a different domain."""
        brands = [
            "google", "facebook", "apple", "microsoft", "amazon",
            "netflix", "paypal", "instagram", "whatsapp", "twitter",
            "chase", "wellsfargo", "bankofamerica", "citibank",
            "linkedin", "dropbox", "yahoo", "outlook", "office365",
        ]
        parts = hostname.split(".")
        base = ".".join(parts[-2:]) if len(parts) >= 2 else hostname

        for brand in brands:
            # Brand in subdomain but not the actual domain
            if brand in hostname and brand not in base:
                return brand
        return None


# Singleton instance
url_analyzer = URLAnalyzer()