"""
Test Pydantic schema validation.
"""

import pytest
from pydantic import ValidationError

from schemas.auth import (
    RequestOTPRequest,
    VerifyOTPRequest,
    UserProfileUpdate,
)
from schemas.analysis import (
    EmailAnalysisRequest,
    URLAnalysisRequest,
    AnalysisResponse,
    AnalysisExplanation,
    ContributingFactor,
)
from schemas.quiz import (
    StartQuizSessionRequest,
    SubmitQuizAnswersRequest,
    QuizAnswerInput,
)
from schemas.common import RiskLabel, QuizCategory


# ═══════════════════════════════════════════
# AUTH SCHEMAS
# ═══════════════════════════════════════════

class TestAuthSchemas:

    def test_request_otp_valid(self):
        req = RequestOTPRequest(email="user@example.com", purpose="login")
        assert req.email == "user@example.com"
        assert req.purpose == "login"

    def test_request_otp_invalid_email(self):
        with pytest.raises(ValidationError):
            RequestOTPRequest(email="not-an-email", purpose="login")

    def test_request_otp_invalid_purpose(self):
        with pytest.raises(ValidationError):
            RequestOTPRequest(email="user@test.com", purpose="invalid")

    def test_verify_otp_valid(self):
        req = VerifyOTPRequest(email="user@test.com", otp="123456", purpose="login")
        assert req.otp == "123456"

    def test_verify_otp_non_numeric(self):
        with pytest.raises(ValidationError):
            VerifyOTPRequest(email="user@test.com", otp="abcdef", purpose="login")

    def test_verify_otp_wrong_length(self):
        with pytest.raises(ValidationError):
            VerifyOTPRequest(email="user@test.com", otp="12345", purpose="login")

    def test_verify_otp_too_long(self):
        with pytest.raises(ValidationError):
            VerifyOTPRequest(email="user@test.com", otp="1234567", purpose="login")

    def test_user_profile_update_valid(self):
        update = UserProfileUpdate(display_name="New Name", phone="+919876543210")
        assert update.display_name == "New Name"

    def test_user_profile_update_empty_allowed(self):
        update = UserProfileUpdate()
        assert update.display_name is None
        assert update.phone is None


# ═══════════════════════════════════════════
# EMAIL ANALYSIS SCHEMAS
# ═══════════════════════════════════════════

class TestEmailAnalysisSchemas:

    def test_valid_email_analysis(self):
        req = EmailAnalysisRequest(
            subject="Test Subject",
            body="This is a test body",
            sender="sender@example.com",
            urls=["https://example.com"]
        )
        assert req.subject == "Test Subject"
        assert len(req.urls) == 1

    def test_email_subject_stripped(self):
        req = EmailAnalysisRequest(
            subject="  Padded Subject  ",
            body="body",
            sender="a@b.com"
        )
        assert req.subject == "Padded Subject"

    def test_email_empty_subject_rejected(self):
        with pytest.raises(ValidationError):
            EmailAnalysisRequest(
                subject="   ",
                body="body",
                sender="a@b.com"
            )

    def test_email_empty_body_rejected(self):
        with pytest.raises(ValidationError):
            EmailAnalysisRequest(
                subject="Subject",
                body="  ",
                sender="a@b.com"
            )

    def test_email_invalid_sender_rejected(self):
        with pytest.raises(ValidationError):
            EmailAnalysisRequest(
                subject="Subject",
                body="Body",
                sender="not-an-email"
            )

    def test_email_urls_cleaned(self):
        req = EmailAnalysisRequest(
            subject="Test",
            body="Body",
            sender="a@b.com",
            urls=["  https://example.com  ", "", "  http://test.com"]
        )
        assert req.urls == ["https://example.com", "http://test.com"]

    def test_email_no_urls_defaults_empty(self):
        req = EmailAnalysisRequest(
            subject="Test",
            body="Body",
            sender="a@b.com"
        )
        assert req.urls == []

    def test_email_subject_max_length(self):
        with pytest.raises(ValidationError):
            EmailAnalysisRequest(
                subject="A" * 501,
                body="Body",
                sender="a@b.com"
            )

    def test_email_body_max_length(self):
        with pytest.raises(ValidationError):
            EmailAnalysisRequest(
                subject="Sub",
                body="A" * 50001,
                sender="a@b.com"
            )


# ═══════════════════════════════════════════
# URL ANALYSIS SCHEMAS
# ═══════════════════════════════════════════

class TestURLAnalysisSchemas:

    def test_valid_url(self):
        req = URLAnalysisRequest(url="https://example.com")
        assert req.url == "https://example.com"

    def test_url_without_scheme_gets_https(self):
        req = URLAnalysisRequest(url="example.com")
        assert req.url == "https://example.com"

    def test_http_url_preserved(self):
        req = URLAnalysisRequest(url="http://suspicious.xyz")
        assert req.url == "http://suspicious.xyz"

    def test_upi_url_preserved(self):
        req = URLAnalysisRequest(url="upi://pay?pa=test@upi")
        assert req.url == "upi://pay?pa=test@upi"

    def test_empty_url_rejected(self):
        with pytest.raises(ValidationError):
            URLAnalysisRequest(url="")

    def test_whitespace_url_rejected(self):
        with pytest.raises(ValidationError):
            URLAnalysisRequest(url="   ")


# ═══════════════════════════════════════════
# ANALYSIS RESPONSE SCHEMAS
# ═══════════════════════════════════════════

class TestAnalysisResponseSchemas:

    def test_valid_response(self):
        resp = AnalysisResponse(
            analysis_id="test-uuid",
            risk_score=75,
            risk_label=RiskLabel.DANGEROUS,
            processing_time_ms=1200,
            explanation=AnalysisExplanation(
                summary="This is dangerous",
                contributing_factors=[
                    ContributingFactor(
                        factor="test_factor",
                        weight=0.5,
                        description="Test description"
                    )
                ]
            ),
            tip="Be careful"
        )
        assert resp.risk_score == 75
        assert resp.risk_label == "dangerous"

    def test_score_out_of_range_rejected(self):
        with pytest.raises(ValidationError):
            AnalysisResponse(
                analysis_id="test",
                risk_score=101,
                risk_label=RiskLabel.SAFE,
                processing_time_ms=100,
                explanation=AnalysisExplanation(summary="test"),
                tip="tip"
            )

    def test_score_negative_rejected(self):
        with pytest.raises(ValidationError):
            AnalysisResponse(
                analysis_id="test",
                risk_score=-1,
                risk_label=RiskLabel.SAFE,
                processing_time_ms=100,
                explanation=AnalysisExplanation(summary="test"),
                tip="tip"
            )


# ═══════════════════════════════════════════
# QUIZ SCHEMAS
# ═══════════════════════════════════════════

class TestQuizSchemas:

    def test_start_quiz_valid(self):
        req = StartQuizSessionRequest(category=QuizCategory.PHISHING)
        assert req.category == "phishing"
        assert req.language == "en"

    def test_start_quiz_invalid_category(self):
        with pytest.raises(ValidationError):
            StartQuizSessionRequest(category="invalid_cat")

    def test_submit_answers_valid(self):
        req = SubmitQuizAnswersRequest(
            answers=[
                QuizAnswerInput(question_id="q1", selected_option_index=0),
                QuizAnswerInput(question_id="q2", selected_option_index=2),
            ]
        )
        assert len(req.answers) == 2

    def test_submit_answers_empty_rejected(self):
        with pytest.raises(ValidationError):
            SubmitQuizAnswersRequest(answers=[])

    def test_submit_answers_duplicate_question_rejected(self):
        with pytest.raises(ValidationError):
            SubmitQuizAnswersRequest(
                answers=[
                    QuizAnswerInput(question_id="q1", selected_option_index=0),
                    QuizAnswerInput(question_id="q1", selected_option_index=1),
                ]
            )

    def test_answer_option_out_of_range_rejected(self):
        with pytest.raises(ValidationError):
            QuizAnswerInput(question_id="q1", selected_option_index=4)

    def test_answer_option_negative_rejected(self):
        with pytest.raises(ValidationError):
            QuizAnswerInput(question_id="q1", selected_option_index=-1)


# ═══════════════════════════════════════════
# RISK LABEL ENUM
# ═══════════════════════════════════════════

class TestRiskLabel:

    def test_valid_labels(self):
        assert RiskLabel.SAFE == "safe"
        assert RiskLabel.SUSPICIOUS == "suspicious"
        assert RiskLabel.DANGEROUS == "dangerous"

    def test_invalid_label(self):
        with pytest.raises(ValueError):
            RiskLabel("critical")