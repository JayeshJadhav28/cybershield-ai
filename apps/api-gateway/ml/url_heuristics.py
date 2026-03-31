"""
Rule-based URL heuristics engine.
Analyzes URLs for phishing indicators without ML — fast and explainable.
"""

import re
import ipaddress
from typing import Dict, List, Tuple
from urllib.parse import urlparse, parse_qs, unquote

from utils.text_preprocessing import (
    SUSPICIOUS_TLDS,
    URL_SHORTENERS,
    LEGITIMATE_DOMAINS,
    INDIAN_BANKS,
    FINANCIAL_SCAM_PHRASES,
)


# ── Domain blocklist (common scam patterns) ──
# In production, load from file and refresh periodically
DOMAIN_BLOCKLIST = {
    "bit.ly", "tinyurl.com",  # Will check if redirects to malicious
    # Known phishing patterns (partial list for MVP)
}

# Keywords that shouldn't appear in legitimate bank domains
PHISHING_DOMAIN_KEYWORDS = [
    "verify", "secure", "login", "account", "update",
    "confirm", "kyc", "alert", "notification", "banking",
    "netbank", "online", "support", "helpdesk", "customer",
]


class URLHeuristicsEngine:
    """
    Analyzes URLs using rule-based heuristics.
    Returns risk probability and detailed flags.
    """

    def analyze(self, url: str) -> Dict:
        """
        Analyze a URL and return risk assessment.

        Returns:
            {
                probability: float (0-1),
                flags: list of triggered rules,
                details: dict of analysis details,
                highlights: list of flagged elements
            }
        """
        result = {
            "probability": 0.0,
            "flags": [],
            "details": {},
            "highlights": [],
        }

        if not url:
            return result

        url = url.strip()

        # Parse URL
        try:
            parsed = urlparse(url)
        except Exception:
            result["flags"].append("unparseable_url")
            result["probability"] = 0.5
            return result

        domain = parsed.netloc.lower()
        path = parsed.path.lower()
        query = parsed.query.lower()
        scheme = parsed.scheme.lower()

        # Remove port from domain if present
        if ":" in domain:
            domain = domain.split(":")[0]

        result["details"]["domain"] = domain
        result["details"]["scheme"] = scheme
        result["details"]["path"] = path

        risk_score = 0.0

        # ── Rule 1: No HTTPS ──
        if scheme == "http":
            risk_score += 0.10
            result["flags"].append("non_https")
            result["highlights"].append({
                "type": "scheme",
                "value": "HTTP",
                "reason": "Unencrypted connection — legitimate payment/banking sites always use HTTPS"
            })

        # ── Rule 2: IP address instead of domain ──
        if self._is_ip_address(domain):
            risk_score += 0.30
            result["flags"].append("ip_address_domain")
            result["highlights"].append({
                "type": "domain",
                "value": domain,
                "reason": "IP address used instead of domain name — strong phishing indicator"
            })

        # ── Rule 3: Legitimate domain check ──
        if self._is_legitimate_domain(domain):
            # Significantly reduce risk for known legitimate domains
            result["details"]["legitimate_domain"] = True
            risk_score -= 0.3  # Can go negative, will be clamped

        # ── Rule 4: Suspicious TLD ──
        tld_flag = self._check_suspicious_tld(domain)
        if tld_flag:
            risk_score += 0.20
            result["flags"].append(f"suspicious_tld:{tld_flag}")
            result["highlights"].append({
                "type": "domain",
                "value": domain,
                "reason": f"Uses suspicious TLD '{tld_flag}' commonly associated with free/scam domains"
            })

        # ── Rule 5: URL shortener ──
        if self._is_url_shortener(domain):
            risk_score += 0.15
            result["flags"].append("url_shortener")
            result["highlights"].append({
                "type": "domain",
                "value": domain,
                "reason": "URL shortener detected — destination may be hidden"
            })

        # ── Rule 6: Excessive subdomains ──
        subdomain_count = domain.count(".")
        if subdomain_count > 3:
            risk_score += 0.15
            result["flags"].append("excessive_subdomains")
            result["details"]["subdomain_count"] = subdomain_count
            result["highlights"].append({
                "type": "domain",
                "value": domain,
                "reason": f"Excessive subdomains ({subdomain_count}) used to disguise malicious domain"
            })

        # ── Rule 7: Bank name in non-official domain ──
        bank_flag = self._check_bank_name_abuse(domain)
        if bank_flag:
            risk_score += 0.35
            result["flags"].append(f"bank_name_abuse:{bank_flag}")
            result["highlights"].append({
                "type": "domain",
                "value": domain,
                "reason": f"Bank name '{bank_flag}' found in non-official domain — likely impersonation"
            })

        # ── Rule 8: Keyword stuffing in domain ──
        domain_keywords = self._check_domain_keyword_stuffing(domain)
        if len(domain_keywords) >= 2:
            risk_score += 0.20
            result["flags"].append("domain_keyword_stuffing")
            result["details"]["domain_keywords"] = domain_keywords
            result["highlights"].append({
                "type": "domain",
                "value": domain,
                "reason": f"Suspicious keywords in domain: {', '.join(domain_keywords)}"
            })

        # ── Rule 9: Long URL ──
        url_length = len(url)
        if url_length > 200:
            risk_score += 0.10
            result["flags"].append("excessively_long_url")
            result["details"]["url_length"] = url_length

        # ── Rule 10: Suspicious path keywords ──
        path_flags = self._check_path_keywords(path)
        if path_flags:
            risk_score += 0.10
            result["flags"].append("suspicious_path_keywords")
            result["details"]["path_flags"] = path_flags

        # ── Rule 11: Double slash in path (redirection trick) ──
        if "//" in path:
            risk_score += 0.10
            result["flags"].append("double_slash_redirection")

        # ── Rule 12: UPI-specific checks ──
        if url.startswith("upi://"):
            upi_risk = self._check_upi_url(url)
            risk_score += upi_risk["risk_score"]
            result["flags"].extend(upi_risk["flags"])
            result["details"]["upi_analysis"] = upi_risk

        # ── Rule 13: Homoglyph characters ──
        if self._has_homoglyphs(domain):
            risk_score += 0.25
            result["flags"].append("homoglyph_characters")
            result["highlights"].append({
                "type": "domain",
                "value": domain,
                "reason": "Look-alike characters detected in domain (e.g., '0' for 'o', '1' for 'l')"
            })

        # Clamp to [0, 1]
        result["probability"] = max(0.0, min(1.0, risk_score))

        return result

    # ── Private helpers ──

    def _is_ip_address(self, domain: str) -> bool:
        """Check if domain is an IP address."""
        try:
            ipaddress.ip_address(domain)
            return True
        except ValueError:
            return False

    def _is_legitimate_domain(self, domain: str) -> bool:
        """Check if domain is in the legitimate domain whitelist."""
        for legit in LEGITIMATE_DOMAINS:
            if domain == legit or domain.endswith("." + legit):
                return True
        return False

    def _check_suspicious_tld(self, domain: str) -> str:
        """Return the suspicious TLD if found, empty string otherwise."""
        for tld in SUSPICIOUS_TLDS:
            if domain.endswith(tld):
                return tld
        return ""

    def _is_url_shortener(self, domain: str) -> bool:
        """Check if domain is a URL shortener."""
        return domain in URL_SHORTENERS

    def _check_bank_name_abuse(self, domain: str) -> str:
        """Check if domain abuses an Indian bank name."""
        if self._is_legitimate_domain(domain):
            return ""
        for bank in INDIAN_BANKS:
            if bank in domain:
                return bank
        return ""

    def _check_domain_keyword_stuffing(self, domain: str) -> List[str]:
        """Find phishing keywords stuffed in domain."""
        if self._is_legitimate_domain(domain):
            return []
        base_domain = domain.split(".")[0]
        return [kw for kw in PHISHING_DOMAIN_KEYWORDS if kw in base_domain]

    def _check_path_keywords(self, path: str) -> List[str]:
        """Find suspicious keywords in URL path."""
        suspicious = [
            "login", "signin", "verify", "confirm", "secure",
            "account", "update", "kyc", "validate", "authenticate",
            "banking", "netbanking", "credit-card", "debit-card",
        ]
        return [kw for kw in suspicious if kw in path]

    def _check_upi_url(self, url: str) -> Dict:
        """Analyze UPI-specific URL patterns."""
        result = {"risk_score": 0.0, "flags": [], "parsed": {}}

        # Parse UPI URL: upi://pay?pa=vpa&pn=name&am=amount
        query_start = url.find("?")
        if query_start == -1:
            result["flags"].append("malformed_upi_url")
            result["risk_score"] = 0.3
            return result

        query_str = url[query_start + 1:]
        params = {}
        for param in query_str.split("&"):
            if "=" in param:
                k, v = param.split("=", 1)
                params[k] = unquote(v)

        result["parsed"] = params

        # Check VPA (Virtual Payment Address) format
        vpa = params.get("pa", "")
        if not vpa or "@" not in vpa:
            result["flags"].append("invalid_vpa_format")
            result["risk_score"] += 0.25
        else:
            # Check for suspicious VPA patterns
            vpa_domain = vpa.split("@")[1] if "@" in vpa else ""
            suspicious_vpa_domains = ["apl", "ibl", "axl"]  # Less common handles
            if vpa_domain not in [
                "oksbi", "okhdfcbank", "okicici", "okaxis", "ybl", "upi",
                "paytm", "paytmbank", "gpay", "idfcbank", "aubank",
                "sbi", "hdfc", "icici", "axis", "kotak",
            ]:
                result["flags"].append(f"unusual_upi_handle:{vpa_domain}")
                result["risk_score"] += 0.1

        # Check payee name
        payee_name = params.get("pn", "")
        if not payee_name:
            result["flags"].append("missing_payee_name")
            result["risk_score"] += 0.1
        elif len(payee_name) < 2:
            result["flags"].append("suspicious_short_payee_name")
            result["risk_score"] += 0.15

        return result

    def _has_homoglyphs(self, domain: str) -> bool:
        """Detect homoglyph character substitutions in domain."""
        # Check for numeric lookalikes
        homoglyph_patterns = [
            (r'[0-9]', lambda d: bool(re.search(r'[0-9]', d.split(".")[0]))),
        ]
        base = domain.split(".")[0]
        # Simple check: if digits appear where letters expected in known bank names
        for bank in ["sbi", "hdfc", "icici", "axis", "kotak"]:
            # Check normalized version
            normalized = re.sub(r'0', 'o', re.sub(r'1', 'l', re.sub(r'3', 'e', base)))
            if bank in normalized and bank not in base:
                return True
        return False


# Singleton instance
url_heuristics = URLHeuristicsEngine()