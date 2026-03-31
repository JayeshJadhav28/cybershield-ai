"""
Tests for phishing detection — URL heuristics, QR decoder, email analyzer.
"""

import pytest
from utils.text_preprocessing import (
    clean_text,
    extract_urls_from_text,
    extract_urgency_phrases,
    analyze_sender_domain,
    build_combined_text,
    _is_lookalike,
)
from ml.url_heuristics import URLHeuristicsEngine
from ml.qr_decoder import QRDecoder
from services.email_analyzer import EmailAnalyzer
from services.url_analyzer import URLAnalyzer


# ═══════════════════════════════════════════
# TEXT PREPROCESSING TESTS
# ═══════════════════════════════════════════

class TestTextPreprocessing:

    def test_clean_text_lowercase(self):
        assert clean_text("HELLO WORLD") == "hello world"

    def test_clean_text_removes_html(self):
        result = clean_text("<b>Click</b> <a href='x'>here</a>")
        assert "<b>" not in result
        assert "click" in result

    def test_clean_text_normalizes_whitespace(self):
        result = clean_text("too   many    spaces")
        assert "  " not in result

    def test_extract_urls_from_text(self):
        text = "Visit https://google.com or http://example.org for more info"
        urls = extract_urls_from_text(text)
        assert len(urls) >= 2
        assert any("google.com" in u for u in urls)

    def test_extract_urgency_phrases_found(self):
        text = "URGENT: Your account will be suspended. Enter your OTP immediately."
        findings = extract_urgency_phrases(text)
        assert len(findings) > 0
        categories = [category for _, category in findings]
        assert "urgency" in categories

    def test_extract_urgency_phrases_clean_text(self):
        text = "Your monthly statement is ready. Please log in to view."
        findings = extract_urgency_phrases(text)
        assert len(findings) == 0

    def test_analyze_sender_legitimate_domain(self):
        result = analyze_sender_domain("alerts@sbi.co.in")
        assert result["is_legitimate"] is True
        assert result["risk_score"] == 0.0

    def test_analyze_sender_suspicious_domain(self):
        result = analyze_sender_domain("security@sbi-verify-account.xyz")
        assert result["risk_score"] > 0.3
        assert len(result["flags"]) > 0

    def test_analyze_sender_bank_name_abuse(self):
        result = analyze_sender_domain("noreply@hdfc-secure.xyz")
        assert any("bank_name" in f for f in result["flags"])
        assert result["risk_score"] > 0.3

    def test_analyze_sender_invalid_email(self):
        result = analyze_sender_domain("not-an-email")
        assert "invalid_email_format" in result["flags"]

    def test_lookalike_detection_sbi(self):
        assert _is_lookalike("sb1.co.in", "sbi.co.in") is True

    def test_lookalike_not_triggered_for_legit(self):
        assert _is_lookalike("sbi.co.in", "sbi.co.in") is False

    def test_lookalike_substring_match(self):
        assert _is_lookalike("sbi-alert.com", "sbi.co.in") is True


# ═══════════════════════════════════════════
# URL HEURISTICS TESTS
# ═══════════════════════════════════════════

class TestURLHeuristics:

    def setup_method(self):
        self.engine = URLHeuristicsEngine()

    def test_legitimate_sbi_url(self):
        result = self.engine.analyze("https://www.sbi.co.in/web/personal-banking")
        assert result["probability"] < 0.3

    def test_ip_address_url(self):
        result = self.engine.analyze("http://192.168.1.1/banking/login")
        assert result["probability"] > 0.4
        assert "ip_address_domain" in result["flags"]

    def test_http_not_https(self):
        result = self.engine.analyze("http://mybank.com/login")
        assert "non_https" in result["flags"]

    def test_suspicious_tld_xyz(self):
        result = self.engine.analyze("https://bank-verify.xyz/login")
        assert "suspicious_tld:.xyz" in result["flags"]
        assert result["probability"] > 0.2

    def test_url_shortener_detection(self):
        result = self.engine.analyze("https://bit.ly/3xyz123")
        assert "url_shortener" in result["flags"]

    def test_bank_name_abuse(self):
        result = self.engine.analyze("https://sbi-kyc-verify.com/login")
        assert any("bank_name_abuse" in f for f in result["flags"])
        assert result["probability"] > 0.5

    def test_keyword_stuffing(self):
        result = self.engine.analyze("https://secure-verify-login-account.com")
        assert result["probability"] > 0.3

    def test_legitimate_hdfc_url(self):
        result = self.engine.analyze("https://netbanking.hdfcbank.com/netbanking/")
        assert result["probability"] < 0.3

    def test_upi_url_valid(self):
        result = self.engine.analyze("upi://pay?pa=merchant@oksbi&pn=ShopName&am=100&cu=INR")
        # Valid UPI should have low risk
        assert result["probability"] < 0.4

    def test_upi_url_suspicious_handle(self):
        result = self.engine.analyze("upi://pay?pa=suspicious@unknownbank&pn=x&am=5000")
        assert result["probability"] > 0.1

    def test_excessive_subdomains(self):
        result = self.engine.analyze("https://login.secure.verify.bank.suspicious.com/kyc")
        assert "excessive_subdomains" in result["flags"]

    def test_empty_url(self):
        result = self.engine.analyze("")
        assert result["probability"] == 0.0

    def test_probability_bounded(self):
        # Even worst-case URL should be ≤ 1.0
        result = self.engine.analyze("http://192.168.1.1/sbi/secure/verify/login/account/kyc.xyz")
        assert 0.0 <= result["probability"] <= 1.0

    def test_highlights_generated_for_suspicious(self):
        result = self.engine.analyze("http://sbi-verify.xyz/login/account")
        assert len(result["highlights"]) > 0

    def test_legitimate_url_no_flags(self):
        result = self.engine.analyze("https://www.hdfcbank.com/personal/login")
        # Legitimate domain should have low or zero flags
        assert result["probability"] < 0.3


# ═══════════════════════════════════════════
# QR DECODER TESTS
# ═══════════════════════════════════════════

class TestQRDecoder:

    def setup_method(self):
        self.decoder = QRDecoder()

    def test_classify_upi_url(self):
        content_type, parsed = self.decoder._classify_and_parse(
            "upi://pay?pa=test@oksbi&pn=TestMerchant&am=100&cu=INR"
        )
        assert content_type == "upi"
        assert parsed["upi_id"] == "test@oksbi"
        assert parsed["payee_name"] == "TestMerchant"
        assert parsed["amount"] == "100"

    def test_classify_http_url(self):
        content_type, parsed = self.decoder._classify_and_parse("https://example.com")
        assert content_type == "url"
        assert parsed["url"] == "https://example.com"

    def test_classify_text(self):
        content_type, parsed = self.decoder._classify_and_parse("Hello World")
        assert content_type == "text"

    def test_parse_upi_all_fields(self):
        url = "upi://pay?pa=merchant@ybl&pn=QuickShop&am=500&cu=INR&tn=Payment&mc=1234"
        parsed = self.decoder._parse_upi_url(url)
        assert parsed["upi_id"] == "merchant@ybl"
        assert parsed["payee_name"] == "QuickShop"
        assert parsed["amount"] == "500"
        assert parsed["currency"] == "INR"
        assert parsed["note"] == "Payment"
        assert parsed["merchant_code"] == "1234"

    def test_parse_upi_missing_fields(self):
        url = "upi://pay?pa=test@oksbi"
        parsed = self.decoder._parse_upi_url(url)
        assert parsed["upi_id"] == "test@oksbi"
        assert parsed["payee_name"] is None
        assert parsed["amount"] is None

    def test_decode_invalid_image(self):
        result = self.decoder.decode_image(b"not-an-image")
        assert result["success"] is False
        assert result["error"] is not None

    def test_decode_empty_bytes(self):
        result = self.decoder.decode_image(b"")
        assert result["success"] is False


# ═══════════════════════════════════════════
# EMAIL ANALYZER TESTS
# ═══════════════════════════════════════════

class TestEmailAnalyzer:

    def setup_method(self):
        self.analyzer = EmailAnalyzer()

    def test_obvious_phishing_email(self):
        result = self.analyzer.analyze(
            subject="URGENT: Your SBI account will be suspended",
            body="Dear customer, verify your SBI account immediately. Enter your password and OTP now. Your account will be blocked in 24 hours if you don't click the link.",
            sender="security@sbi-verify-now.xyz",
            urls=["http://sbi-verify-now.xyz/login"]
        )
        assert result.probability > 0.5
        assert len(result.flags) > 0
        assert len(result.highlighted_phrases) > 0

    def test_safe_email(self):
        result = self.analyzer.analyze(
            subject="Your January 2024 statement is ready",
            body="Dear customer, your account statement for January 2024 is available. Please log in at sbi.co.in to view.",
            sender="statements@sbi.co.in",
            urls=["https://www.sbi.co.in"]
        )
        assert result.probability < 0.5

    def test_urgency_detected(self):
        result = self.analyzer.analyze(
            subject="URGENT action required",
            body="Immediate action required. Your account will be suspended within 24 hours.",
            sender="alert@suspicious.xyz",
        )
        assert "urgency" in result.flags or result.probability > 0.3

    def test_credential_request_detected(self):
        result = self.analyzer.analyze(
            subject="Verify your account",
            body="Please enter your password and OTP to confirm your identity. Enter your credentials now.",
            sender="verify@bank-secure.com",
        )
        assert "credential_request" in result.flags or result.probability > 0.3

    def test_suspicious_url_boosts_score(self):
        result_with_bad_url = self.analyzer.analyze(
            subject="Please verify",
            body="Click the link to verify",
            sender="test@test.com",
            urls=["http://sbi-verify-kyc.xyz/login"]
        )
        result_no_url = self.analyzer.analyze(
            subject="Please verify",
            body="Click the link to verify",
            sender="test@test.com",
            urls=[]
        )
        assert result_with_bad_url.probability >= result_no_url.probability

    def test_legitimate_sender_reduces_risk(self):
        result_legit = self.analyzer.analyze(
            subject="Your statement",
            body="Your statement is ready",
            sender="alerts@sbi.co.in",
        )
        result_suspicious = self.analyzer.analyze(
            subject="Your statement",
            body="Your statement is ready",
            sender="alerts@sbi-fake-bank.xyz",
        )
        assert result_suspicious.probability > result_legit.probability

    def test_probability_bounded(self):
        result = self.analyzer.analyze(
            subject="URGENT URGENT URGENT suspicious",
            body="Enter OTP password credentials immediately account suspended kyc expired",
            sender="fake@scam.xyz",
            urls=["http://192.168.1.1/bank/kyc/verify"]
        )
        assert 0.0 <= result.probability <= 1.0
        assert result.processing_time_ms > 0

    def test_empty_urls_handled(self):
        result = self.analyzer.analyze(
            subject="Test",
            body="Test body",
            sender="test@test.com",
            urls=None
        )
        assert result is not None
        assert result.probability >= 0.0


# ═══════════════════════════════════════════
# URL ANALYZER SERVICE TESTS
# ═══════════════════════════════════════════

class TestURLAnalyzerService:

    def setup_method(self):
        self.analyzer = URLAnalyzer()

    def test_analyze_suspicious_url(self):
        result = self.analyzer.analyze("http://sbi-kyc-verify.xyz/login")
        assert result.probability > 0.3
        assert len(result.flags) > 0

    def test_analyze_legitimate_url(self):
        result = self.analyzer.analyze("https://www.hdfcbank.com/")
        assert result.probability < 0.4

    def test_processing_time_recorded(self):
        result = self.analyzer.analyze("https://example.com")
        assert result.processing_time_ms >= 0

    def test_confidence_set(self):
        result = self.analyzer.analyze("https://example.com")
        assert 0.0 < result.confidence <= 1.0