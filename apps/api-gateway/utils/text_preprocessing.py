"""
Text preprocessing utilities for phishing detection.
Cleans, normalizes, and extracts features from email/URL text.
"""

import re
import string
from typing import List, Tuple, Dict
from urllib.parse import urlparse


# ── Phishing keyword lists ──
URGENCY_PHRASES = [
    "urgent", "immediate", "immediately", "act now", "action required",
    "verify now", "confirm now", "limited time", "expires soon",
    "account suspended", "account blocked", "account locked",
    "within 24 hours", "within 48 hours", "last chance",
    "final notice", "important notice", "security alert",
    "unusual activity", "suspicious activity", "unauthorized access",
]

CREDENTIAL_PHRASES = [
    "enter your password", "confirm your password", "verify your identity",
    "enter your otp", "share your otp", "provide your otp",
    "enter your pin", "confirm your details", "update your kyc",
    "complete your kyc", "kyc verification", "click here to verify",
    "click the link", "login to verify", "verify your account",
    "enter your credentials", "enter your card", "enter your cvv",
    "bank account details", "debit card number", "credit card number",
]

FINANCIAL_SCAM_PHRASES = [
    "you have won", "congratulations", "prize money", "lottery",
    "selected for", "claim your reward", "free money", "cash prize",
    "government refund", "income tax refund", "tds refund",
    "insurance claim", "emi waiver", "loan approved",
    "upi cashback", "gpay offer", "phonepe offer", "paytm offer",
]

# Indian bank names used in phishing
INDIAN_BANKS = [
    "sbi", "hdfc", "icici", "axis", "kotak", "pnb", "canara",
    "bank of baroda", "union bank", "idbi", "yes bank", "indusind",
    "federal bank", "rbl", "bandhan", "au bank", "navi bank",
]

# Suspicious TLDs commonly used in phishing
SUSPICIOUS_TLDS = {
    ".xyz", ".tk", ".ml", ".ga", ".cf", ".gq", ".pw",
    ".top", ".club", ".online", ".site", ".info", ".biz",
    ".link", ".click", ".download", ".stream", ".gdn",
}

# URL shorteners commonly abused
URL_SHORTENERS = {
    "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly",
    "is.gd", "buff.ly", "adf.ly", "tiny.cc", "cutt.ly",
    "rb.gy", "shorturl.at", "tiny.one", "short.io",
}

# Known legitimate Indian financial domains
LEGITIMATE_DOMAINS = {
    "sbi.co.in", "onlinesbi.sbi", "sbicards.com",
    "hdfcbank.com", "netbanking.hdfc.com",
    "icicibank.com", "infinityicici.com",
    "axisbank.com", "retail.axisbank.co.in",
    "kotakbank.com", "kotak.com",
    "phonepe.com", "paytm.com", "googlepay.com",
    "upi.npci.org.in", "npci.org.in",
    "cybercrime.gov.in", "sbi.gov.in",
    "incometax.gov.in", "irs.gov",
}


def clean_text(text: str) -> str:
    """
    Clean and normalize text for feature extraction.
    Preserves important tokens while removing noise.
    """
    if not text:
        return ""
    # Lowercase
    text = text.lower()
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep important punctuation
    text = re.sub(r'[^\w\s@.\-:/]', ' ', text)
    return text.strip()


def extract_urls_from_text(text: str) -> List[str]:
    """Extract all URLs from text content."""
    url_pattern = re.compile(
        r'https?://[^\s<>"{}|\\^`\[\]]+|'
        r'www\.[^\s<>"{}|\\^`\[\]]+'
    )
    urls = url_pattern.findall(text)
    return [url.rstrip('.,)>') for url in urls]


def extract_urgency_phrases(text: str) -> List[Tuple[str, str]]:
    """
    Find urgency/manipulation phrases in text.
    Returns list of (phrase, category) tuples.
    """
    text_lower = text.lower()
    found = []

    for phrase in URGENCY_PHRASES:
        if phrase in text_lower:
            found.append((phrase, "urgency"))

    for phrase in CREDENTIAL_PHRASES:
        if phrase in text_lower:
            found.append((phrase, "credential_request"))

    for phrase in FINANCIAL_SCAM_PHRASES:
        if phrase in text_lower:
            found.append((phrase, "financial_scam"))

    return found


def analyze_sender_domain(sender_email: str) -> Dict:
    """
    Analyze sender email domain for suspicious patterns.
    Returns dict of flags and analysis.
    """
    result = {
        "email": sender_email,
        "domain": "",
        "flags": [],
        "is_legitimate": False,
        "risk_score": 0.0,
    }

    if not sender_email or "@" not in sender_email:
        result["flags"].append("invalid_email_format")
        result["risk_score"] = 0.8
        return result

    parts = sender_email.lower().split("@")
    if len(parts) != 2:
        result["flags"].append("invalid_email_format")
        return result

    local_part, domain = parts
    result["domain"] = domain

    # Check against legitimate domains
    if domain in LEGITIMATE_DOMAINS:
        result["is_legitimate"] = True
        return result

    # Check for lookalike domains (typosquatting)
    for legit_domain in LEGITIMATE_DOMAINS:
        if _is_lookalike(domain, legit_domain):
            result["flags"].append(f"lookalike_domain ({legit_domain})")
            result["risk_score"] += 0.4

    # Check suspicious TLD
    for tld in SUSPICIOUS_TLDS:
        if domain.endswith(tld):
            result["flags"].append(f"suspicious_tld ({tld})")
            result["risk_score"] += 0.2
            break

    # Check for excessive subdomains
    parts_count = domain.count(".")
    if parts_count > 2:
        result["flags"].append("excessive_subdomains")
        result["risk_score"] += 0.15

    # Check for bank name in suspicious domain
    for bank in INDIAN_BANKS:
        if bank in domain and domain not in LEGITIMATE_DOMAINS:
            result["flags"].append(f"bank_name_in_suspicious_domain ({bank})")
            result["risk_score"] += 0.35
            break

    # Check for keywords in domain
    suspicious_keywords = ["secure", "verify", "login", "account", "update", "confirm", "kyc"]
    found_keywords = [kw for kw in suspicious_keywords if kw in domain]
    if found_keywords:
        result["flags"].append(f"suspicious_keywords_in_domain ({', '.join(found_keywords)})")
        result["risk_score"] += 0.2

    result["risk_score"] = min(1.0, result["risk_score"])
    return result


def build_combined_text(subject: str, body: str, sender: str, urls: List[str]) -> str:
    """
    Combine all email fields into a single text for TF-IDF vectorization.
    Weights important fields by repeating them.
    """
    # Repeat subject 3x and sender 2x to give them more weight
    parts = [
        subject * 3,
        sender * 2,
        body,
        " ".join(urls),
    ]
    return " ".join(clean_text(p) for p in parts if p)


def _is_lookalike(domain: str, reference: str) -> bool:
    """
    Simple lookalike domain detection.
    Checks for character substitution, insertion, deletion.
    """
    if domain == reference:
        return False

    # Extract base domain (without TLD)
    domain_base = domain.split(".")[0]
    ref_base = reference.split(".")[0]

    if len(domain_base) < 3 or len(ref_base) < 3:
        return False

    # Check if one is substring of other (sbi vs sbi-alert)
    if ref_base in domain_base and domain_base != ref_base:
        return True

    # Simple edit distance check (levenshtein-like)
    if abs(len(domain_base) - len(ref_base)) <= 2:
        differences = sum(1 for a, b in zip(domain_base, ref_base) if a != b)
        if differences <= 2 and len(domain_base) > 3:
            return True

    # Common homoglyph substitutions
    homoglyphs = {'0': 'o', '1': 'l', '3': 'e', '4': 'a', '@': 'a'}
    normalized = domain_base
    for fake, real in homoglyphs.items():
        normalized = normalized.replace(fake, real)
    if normalized == ref_base:
        return True

    return False