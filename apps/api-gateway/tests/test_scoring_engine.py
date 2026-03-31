"""
Tests for the hybrid 75 % AI  /  25 % Rules scoring engine.
"""

import pytest

from services.scoring_engine import (
    ModalityResult,
    ScoringEngine,
    ScoringInput,
)


@pytest.fixture
def engine():
    return ScoringEngine(
        {
            "ai_weight": 0.75,
            "rule_weight": 0.25,
            "audio_weight": 0.35,
            "video_weight": 0.35,
            "phish_weight": 0.30,
            "safe_threshold": 30,
            "dangerous_threshold": 70,
        }
    )


# ── 75 / 25 weighting tests ──────────────────────────────────────
class TestHybridWeighting:
    def test_pure_ai_high_threat(self, engine):
        """AI says 1.0 threat, rules say 0 → 0.75×100 = 75 → dangerous."""
        inp = ScoringInput(
            audio_result=ModalityResult(ai_probability=1.0, rule_score=0.0),
            analysis_type="audio",
        )
        out = engine.compute(inp)
        assert out.risk_score == 75
        assert out.risk_label == "dangerous"

    def test_pure_rules_high_threat(self, engine):
        """AI says 0, rules say 1.0 → 0.25×100 = 25 → safe."""
        inp = ScoringInput(
            audio_result=ModalityResult(ai_probability=0.0, rule_score=1.0),
            analysis_type="audio",
        )
        out = engine.compute(inp)
        assert out.risk_score == 25
        assert out.risk_label == "safe"

    def test_both_agree_dangerous(self, engine):
        """AI=0.9, rules=0.8 → 0.75×90+0.25×80 = 87.5 → 88."""
        inp = ScoringInput(
            audio_result=ModalityResult(ai_probability=0.9, rule_score=0.8),
            analysis_type="audio",
        )
        out = engine.compute(inp)
        assert out.risk_score >= 85
        assert out.risk_label == "dangerous"

    def test_both_agree_safe(self, engine):
        """AI=0.1, rules=0.05 → ~9 → safe."""
        inp = ScoringInput(
            video_result=ModalityResult(ai_probability=0.1, rule_score=0.05),
            analysis_type="video",
        )
        out = engine.compute(inp)
        assert out.risk_score < 30
        assert out.risk_label == "safe"

    def test_mid_range_suspicious(self, engine):
        """AI=0.5, rules=0.5 → 50 → suspicious."""
        inp = ScoringInput(
            phish_result=ModalityResult(ai_probability=0.5, rule_score=0.5),
            analysis_type="email",
        )
        out = engine.compute(inp)
        assert 30 <= out.risk_score < 70
        assert out.risk_label == "suspicious"


# ── single vs multi modality ─────────────────────────────────────
class TestModalities:
    def test_single_modality_audio(self, engine):
        inp = ScoringInput(
            audio_result=ModalityResult(ai_probability=0.8, rule_score=0.3),
            analysis_type="audio",
        )
        out = engine.compute(inp)
        expected = 0.75 * 0.8 + 0.25 * 0.3  # 0.675
        assert abs(out.risk_score - int(expected * 100)) <= 1

    def test_multi_modality_averages(self, engine):
        inp = ScoringInput(
            audio_result=ModalityResult(ai_probability=0.9, rule_score=0.5),
            video_result=ModalityResult(ai_probability=0.4, rule_score=0.2),
            analysis_type="audio",
        )
        out = engine.compute(inp)
        assert 30 <= out.risk_score <= 80

    def test_empty_input_safe(self, engine):
        out = engine.compute(ScoringInput())
        assert out.risk_score == 0
        assert out.risk_label == "safe"


# ── contextual adjustments ───────────────────────────────────────
class TestContextualFlags:
    def test_blocklist_boosts_score(self, engine):
        inp = ScoringInput(
            phish_result=ModalityResult(ai_probability=0.5, rule_score=0.3),
            analysis_type="email",
            contextual_flags=["blocklisted_domain"],
        )
        out = engine.compute(inp)
        base = 0.75 * 0.5 + 0.25 * 0.3  # 0.45 → 45
        assert out.risk_score >= 45 + 15  # +20 adjustment

    def test_multiple_flags_stack(self, engine):
        inp = ScoringInput(
            phish_result=ModalityResult(ai_probability=0.4, rule_score=0.2),
            analysis_type="email",
            contextual_flags=["urgency_language", "credential_request", "non_https"],
        )
        out = engine.compute(inp)
        base = int((0.75 * 0.4 + 0.25 * 0.2) * 100)  # 35
        assert out.risk_score >= base + 10


# ── score bounds ─────────────────────────────────────────────────
class TestBounds:
    def test_score_capped_at_100(self, engine):
        inp = ScoringInput(
            phish_result=ModalityResult(ai_probability=1.0, rule_score=1.0),
            analysis_type="email",
            contextual_flags=[
                "blocklisted_domain",
                "urgency_language",
                "credential_request",
                "non_https",
                "upi_mismatch",
            ],
        )
        out = engine.compute(inp)
        assert out.risk_score <= 100

    def test_score_never_negative(self, engine):
        inp = ScoringInput(
            audio_result=ModalityResult(ai_probability=0.0, rule_score=0.0),
            analysis_type="audio",
        )
        out = engine.compute(inp)
        assert out.risk_score >= 0


# ── breakdown / explainability ───────────────────────────────────
class TestBreakdown:
    def test_breakdown_contains_weights(self, engine):
        inp = ScoringInput(
            audio_result=ModalityResult(
                ai_probability=0.7,
                rule_score=0.4,
                model_available=True,
            ),
            analysis_type="audio",
        )
        out = engine.compute(inp)
        assert out.breakdown["ai_weight"] == 0.75
        assert out.breakdown["rule_weight"] == 0.25
        assert "formula" in out.breakdown

    def test_contributing_factors_present(self, engine):
        inp = ScoringInput(
            audio_result=ModalityResult(
                ai_probability=0.7,
                rule_score=0.4,
                flags=["high_spectral_flatness"],
            ),
            analysis_type="audio",
        )
        out = engine.compute(inp)
        assert len(out.contributing_factors) >= 2  # AI + rules entries

    def test_explanation_summary_non_empty(self, engine):
        inp = ScoringInput(
            video_result=ModalityResult(ai_probability=0.85, rule_score=0.6),
            analysis_type="video",
        )
        out = engine.compute(inp)
        assert len(out.explanation_summary) > 20

