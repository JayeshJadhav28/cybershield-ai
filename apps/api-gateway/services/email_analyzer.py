"""
Email phishing analysis service.
Pure heuristic / rule-based — NO ML model required.
Combines text analysis, URL heuristics, and sender analysis.
"""

import time
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass, field

from utils.text_preprocessing import (
    clean_text,
    extract_urgency_phrases,
    analyze_sender_domain,
    build_combined_text,
    extract_urls_from_text,
)

logger = logging.getLogger(__name__)


@dataclass
class EmailAnalysisResult:
    """Result from email phishing analysis."""

    probability: float = 0.0
    confidence: float = 0.0
    flags: List[str] = field(default_factory=list)
    features: Dict = field(default_factory=dict)
    highlighted_phrases: List[Dict] = field(default_factory=list)
    flagged_urls: List[Dict] = field(default_factory=list)
    sender_analysis: Dict = field(default_factory=dict)
    processing_time_ms: int = 0


class EmailAnalyzer:
    """Analyzes emails for phishing indicators using rules only."""

    def analyze(
        self,
        subject: str,
        body: str,
        sender: str,
        urls: Optional[List[str]] = None,
    ) -> EmailAnalysisResult:
        """
        Pure heuristic phishing analysis pipeline.

        1. Extract urgency / manipulation phrases
        2. URL heuristic analysis
        3. Sender domain analysis
        4. Score aggregation from all rule signals
        """
        start_time = time.time()
        urls = urls or []

        # ── Step 1: Text / Urgency Analysis ──
        full_text = subject + " " + body
        urgency_findings = extract_urgency_phrases(full_text)

        # ── Step 2: URL Analysis ──
        body_urls = extract_urls_from_text(body)
        all_urls = list(set(urls + body_urls))

        url_results = []
        max_url_risk = 0.0

        try:
            from ml.url_heuristics import analyze_url

            for url in all_urls:
                url_result = analyze_url(url)
                url_results.append({"url": url, **url_result})
                max_url_risk = max(
                    max_url_risk, url_result.get("probability", 0.0)
                )
        except ImportError:
            logger.warning("url_heuristics not available — skipping URL analysis")
            # Basic fallback: flag non-https URLs
            for url in all_urls:
                risk = 0.0
                url_flags = []
                if url.startswith("http://"):
                    risk = 0.3
                    url_flags.append("non_https")
                url_results.append(
                    {"url": url, "probability": risk, "flags": url_flags}
                )
                max_url_risk = max(max_url_risk, risk)
        except Exception as e:
            logger.error("URL analysis failed: %s", e)

        # ── Step 3: Sender Analysis ──
        sender_analysis = analyze_sender_domain(sender)

        # ── Step 4: Build Flags + Highlights ──
        flags: List[str] = []
        highlighted_phrases: List[Dict] = []

        categories_found: set = set()
        for phrase, category in urgency_findings:
            if category not in categories_found:
                flags.append(category)
                categories_found.add(category)
            highlighted_phrases.append(
                {
                    "text": phrase,
                    "reason": self._get_phrase_reason(category),
                }
            )

        # Sender flags
        sender_flags = sender_analysis.get("flags") or []
        flags.extend(sender_flags)

        # URL flags
        flagged_urls: List[Dict] = []
        for url_result in url_results:
            url_flags = url_result.get("flags") or []
            url_prob = url_result.get("probability", 0.0)
            if url_flags or url_prob > 0.3:
                flagged_urls.append(
                    {
                        "url": url_result["url"],
                        "flags": [
                            self._flag_to_human_readable(f) for f in url_flags
                        ],
                    }
                )

        # ── Step 5: Compute Heuristic Probability ──
        sender_risk = min(1.0, sender_analysis.get("risk_score", 0.0))

        # Start from urgency phrase score
        text_risk = self._compute_text_risk(urgency_findings, full_text)

        # Weighted combination of all heuristic signals
        if all_urls:
            combined_prob = (
                text_risk * 0.40
                + max_url_risk * 0.35
                + sender_risk * 0.25
            )
        else:
            # No URLs → text and sender matter more
            combined_prob = text_risk * 0.55 + sender_risk * 0.45

        # Hard-boost if multiple strong signals
        strong_signals = 0
        if text_risk > 0.6:
            strong_signals += 1
        if max_url_risk > 0.6:
            strong_signals += 1
        if sender_risk > 0.5:
            strong_signals += 1
        if len(urgency_findings) >= 3:
            strong_signals += 1
        if flagged_urls:
            strong_signals += 1

        if strong_signals >= 3:
            combined_prob = max(combined_prob, 0.85)
        elif strong_signals >= 2:
            combined_prob = max(combined_prob, 0.60)

        combined_prob = max(0.0, min(1.0, combined_prob))

        # Confidence: heuristics-only → 0.6 base, higher with more signals
        confidence = min(0.9, 0.5 + (len(flags) * 0.05))

        processing_time_ms = int((time.time() - start_time) * 1000)

        return EmailAnalysisResult(
            probability=combined_prob,
            confidence=confidence,
            flags=flags,
            features={
                "text_risk": round(text_risk, 4),
                "max_url_risk": round(max_url_risk, 4),
                "sender_risk": round(sender_risk, 4),
                "urgency_phrase_count": len(urgency_findings),
                "url_count": len(all_urls),
                "strong_signals": strong_signals,
                "subject_word_count": len(subject.split()),
                "model_loaded": False,  # pure heuristic
            },
            highlighted_phrases=highlighted_phrases,
            flagged_urls=flagged_urls,
            sender_analysis=sender_analysis,
            processing_time_ms=processing_time_ms,
        )

    # ------------------------------------------------------------------
    def _compute_text_risk(
        self, urgency_findings: list, full_text: str
    ) -> float:
        """
        Score text content for phishing signals.
        Returns risk in [0, 1].
        """
        score = 0.0
        text_lower = full_text.lower()

        # Urgency phrase density
        n = len(urgency_findings)
        if n >= 5:
            score += 0.40
        elif n >= 3:
            score += 0.25
        elif n >= 1:
            score += 0.12

        # Category diversity (more categories = more suspicious)
        categories = set(cat for _, cat in urgency_findings)
        if len(categories) >= 3:
            score += 0.20
        elif len(categories) >= 2:
            score += 0.10

        # Credential / OTP request keywords
        cred_keywords = [
            "password", "otp", "pin", "cvv", "credential",
            "login", "sign in", "verify your", "confirm your",
            "update your", "enter your", "provide your",
        ]
        cred_hits = sum(1 for k in cred_keywords if k in text_lower)
        if cred_hits >= 3:
            score += 0.25
        elif cred_hits >= 1:
            score += 0.12

        # Threat / punishment language
        threat_keywords = [
            "suspend", "block", "close", "restrict", "frozen",
            "terminate", "legal action", "penalty", "arrest",
            "permanent", "immediately", "within 24",
        ]
        threat_hits = sum(1 for k in threat_keywords if k in text_lower)
        if threat_hits >= 3:
            score += 0.20
        elif threat_hits >= 1:
            score += 0.10

        # Reward / prize language
        reward_keywords = [
            "won", "winner", "prize", "lottery", "cashback",
            "reward", "selected", "lucky", "congratulation",
            "claim your", "free",
        ]
        reward_hits = sum(1 for k in reward_keywords if k in text_lower)
        if reward_hits >= 2:
            score += 0.20
        elif reward_hits >= 1:
            score += 0.10

        return min(1.0, score)

    # ------------------------------------------------------------------
    def _get_phrase_reason(self, category: str) -> str:
        reasons = {
            "urgency": "Creates artificial urgency to pressure quick action",
            "credential_request": "Requests sensitive credentials — banks never ask via email",
            "financial_scam": "Uses financial reward tactics common in advance-fee scams",
        }
        return reasons.get(category, "Suspicious language pattern detected")

    def _flag_to_human_readable(self, flag: str) -> str:
        mappings = {
            "non_https": "Non-HTTPS link (insecure)",
            "ip_address_domain": "IP address used as domain",
            "suspicious_tld": "Suspicious domain extension",
            "url_shortener": "URL shortener detected",
            "excessive_subdomains": "Excessive subdomains",
            "domain_keyword_stuffing": "Suspicious keywords in domain",
            "homoglyph_characters": "Look-alike characters in domain",
        }
        base_flag = flag.split(":")[0]
        if "bank_name_abuse" in flag:
            bank = flag.split(":")[1] if ":" in flag else ""
            return f"Bank name '{bank}' in non-official domain"
        if "lookalike_domain" in flag:
            ref = flag.split("(")[1].rstrip(")") if "(" in flag else ""
            return f"Domain looks like '{ref}' (typosquatting)"
        return mappings.get(base_flag, flag.replace("_", " ").title())


# Singleton
email_analyzer = EmailAnalyzer()