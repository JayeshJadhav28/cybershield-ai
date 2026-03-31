"""
Hybrid Scoring Engine
=====================

Combines **AI model predictions (75 %)** with **heuristic / rule-based
scores (25 %)** to produce the final risk assessment.

    final_score  =  AI_WEIGHT × ai_score  +  RULE_WEIGHT × rule_score
                 =  0.75 × ai  +  0.25 × rules

Calibrated thresholds per modality to handle mis-calibration:
  - Video: Safe ≤ 0.35, Dangerous ≥ 0.65
  - Audio: Safe ≤ 0.30, Dangerous ≥ 0.70
  - Phish: Safe ≤ 0.30, Dangerous ≥ 0.70

The UI receives the blended score, confidence level, and calibration
note so it can display uncertainty to the user.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from config import settings

logger = logging.getLogger(__name__)


# ── Calibrated thresholds per modality ────────────────────────────
MODALITY_THRESHOLDS: Dict[str, Dict[str, float]] = {
    "audio": {"safe_upper": 0.30, "dangerous_lower": 0.70},
    "video": {"safe_upper": 0.35, "dangerous_lower": 0.65},
    "phish": {"safe_upper": 0.30, "dangerous_lower": 0.70},
}


# ── Data Structures ────────────────────────────────────────────────
@dataclass
class ModalityResult:
    """Output from a single analysis modality."""

    ai_probability: float = 0.5  # ML model's P(threat)    [0, 1]
    rule_score: float = 0.0      # Heuristic risk score     [0, 1]
    confidence: float = 0.0      # How sure the model is    [0, 1]
    features: Dict = field(default_factory=dict)
    flags: List[str] = field(default_factory=list)
    model_available: bool = False


@dataclass
class ScoringInput:
    """Assembled input for the scoring engine."""

    audio_result: Optional[ModalityResult] = None
    video_result: Optional[ModalityResult] = None
    phish_result: Optional[ModalityResult] = None
    analysis_type: str = ""  # "email" | "url" | "qr" | "audio" | "video"
    contextual_flags: List[str] = field(default_factory=list)


@dataclass
class ScoringOutput:
    risk_score: int = 0               # 0-100
    risk_label: str = "safe"          # "safe" | "suspicious" | "dangerous"
    confidence_level: str = "high"    # "high" | "medium" | "low"
    calibration_note: str = ""        # shown to user when uncertain
    ai_score_raw: float = 0.0         # weighted AI contribution (0-100)
    rule_score_raw: float = 0.0       # weighted rule contribution (0-100)
    contributing_factors: List[Dict] = field(default_factory=list)
    model_scores: Dict = field(default_factory=dict)
    explanation_summary: str = ""
    breakdown: Dict = field(default_factory=dict)


# ── Engine ─────────────────────────────────────────────────────────
class ScoringEngine:
    def __init__(self, config: Dict | None = None):
        cfg = config or {}
        self.ai_weight = cfg.get("ai_weight", settings.AI_WEIGHT)
        self.rule_weight = cfg.get("rule_weight", settings.RULE_WEIGHT)
        self.safe_threshold = cfg.get("safe_threshold", settings.SAFE_THRESHOLD)
        self.dangerous_threshold = cfg.get(
            "dangerous_threshold", settings.DANGEROUS_THRESHOLD
        )

        # Per-modality importance (only matters when >1 modality is present)
        self.modality_weights = {
            "audio": cfg.get("audio_weight", 0.35),
            "video": cfg.get("video_weight", 0.35),
            "phish": cfg.get("phish_weight", 0.30),
        }

    # ------------------------------------------------------------------
    def compute(self, inp: ScoringInput) -> ScoringOutput:
        """
        Main scoring pipeline.

        1. For each modality apply calibrated band mapping THEN blend:
               blended = 0.75 × calibrated_ai  +  0.25 × rule_score
        2. If multiple modalities → weighted average of blended scores.
        3. Apply contextual flag adjustments.
        4. Map to 0-100 int → risk label.
        5. Compute confidence level and calibration note.
        """
        modalities: Dict[str, ModalityResult] = {}
        if inp.audio_result:
            modalities["audio"] = inp.audio_result
        if inp.video_result:
            modalities["video"] = inp.video_result
        if inp.phish_result:
            modalities["phish"] = inp.phish_result

        if not modalities:
            return ScoringOutput(
                risk_score=0,
                risk_label="safe",
                confidence_level="high",
                explanation_summary="No analysis input provided.",
            )

        # ── Step 1: per-modality calibrated blended scores ──────────
        blended: Dict[str, float] = {}
        raw_ai: Dict[str, float] = {}
        raw_rule: Dict[str, float] = {}
        factors: List[Dict] = []
        model_confidences: List[float] = []

        for key, res in modalities.items():
            ai_raw = res.ai_probability
            rl = res.rule_score
            model_confidences.append(res.confidence)

            # Apply calibrated band mapping before blending
            calibrated_ai = self._calibrate_score(ai_raw, key)

            b = self.ai_weight * calibrated_ai + self.rule_weight * rl
            blended[key] = b
            raw_ai[key] = ai_raw
            raw_rule[key] = rl

            factors.append(
                {
                    "factor": f"{key}_ai_model",
                    "weight": self.ai_weight,
                    "raw_score": round(ai_raw, 4),
                    "calibrated_score": round(calibrated_ai, 4),
                    "contribution": round(self.ai_weight * calibrated_ai * 100, 2),
                    "description": (
                        f"{key.title()} AI model: raw={ai_raw:.2%}, "
                        f"calibrated={calibrated_ai:.2%}"
                    ),
                }
            )
            factors.append(
                {
                    "factor": f"{key}_rule_score",
                    "weight": self.rule_weight,
                    "raw_score": round(rl, 4),
                    "contribution": round(self.rule_weight * rl * 100, 2),
                    "description": f"{key.title()} heuristic score: {rl:.2%}",
                }
            )

        # ── Step 2: weighted average of blended scores ───────────────
        total_w = sum(self.modality_weights[k] for k in blended)
        if total_w == 0:
            base_score = 0.0
        else:
            base_score = (
                sum(blended[k] * self.modality_weights[k] for k in blended)
                / total_w
            ) * 100

        # ── Step 3: contextual flag adjustments ──────────────────────
        adjustment = 0
        ctx_flags = inp.contextual_flags or []

        if "blocklisted_domain" in ctx_flags:
            adjustment += 20
            factors.append(
                {
                    "factor": "rule_adjustment",
                    "description": "Domain on known scam blocklist (+20)",
                }
            )
        if "urgency_language" in ctx_flags and "credential_request" in ctx_flags:
            adjustment += 10
            factors.append(
                {
                    "factor": "rule_adjustment",
                    "description": "Urgency + credential request combo (+10)",
                }
            )
        if "non_https" in ctx_flags:
            adjustment += 5
            factors.append(
                {
                    "factor": "rule_adjustment",
                    "description": "Non-HTTPS link (+5)",
                }
            )
        if "upi_mismatch" in ctx_flags:
            adjustment += 15
            factors.append(
                {
                    "factor": "rule_adjustment",
                    "description": "UPI payee mismatch (+15)",
                }
            )

        # ── Step 4: final score + label ─────────────────────────────
        risk_score = int(min(100, max(0, round(base_score + adjustment))))

        if risk_score < self.safe_threshold:
            risk_label = "safe"
        elif risk_score >= self.dangerous_threshold:
            risk_label = "dangerous"
        else:
            risk_label = "suspicious"

        # ── Step 5: confidence level ─────────────────────────────────
        avg_model_confidence = (
            sum(model_confidences) / len(model_confidences)
            if model_confidences else 0.0
        )
        confidence_level, calibration_note = self._compute_confidence(
            risk_label=risk_label,
            avg_model_confidence=avg_model_confidence,
            raw_ai_scores=raw_ai,
            analysis_type=inp.analysis_type,
        )

        # ── Step 6: build explanation ────────────────────────────────
        avg_ai = sum(raw_ai.values()) / len(raw_ai)
        avg_rule = sum(raw_rule.values()) / len(raw_rule)

        breakdown = {
            "ai_weight": self.ai_weight,
            "rule_weight": self.rule_weight,
            "ai_score": round(avg_ai, 4),
            "rule_score": round(avg_rule, 4),
            "ai_contribution": round(self.ai_weight * avg_ai * 100, 1),
            "rule_contribution": round(self.rule_weight * avg_rule * 100, 1),
            "adjustment": adjustment,
            "formula": f"{self.ai_weight}×calibrated_AI + {self.rule_weight}×Rules + adjustments",
            "confidence_level": confidence_level,
        }

        summary = self._build_summary(
            risk_label, inp.analysis_type, avg_ai, avg_rule, factors,
            confidence_level
        )

        return ScoringOutput(
            risk_score=risk_score,
            risk_label=risk_label,
            confidence_level=confidence_level,
            calibration_note=calibration_note,
            ai_score_raw=round(self.ai_weight * avg_ai * 100, 2),
            rule_score_raw=round(self.rule_weight * avg_rule * 100, 2),
            contributing_factors=factors,
            model_scores={k: round(v, 4) for k, v in raw_ai.items()},
            explanation_summary=summary,
            breakdown=breakdown,
        )

    # ------------------------------------------------------------------
    @staticmethod
    def _calibrate_score(raw_p: float, modality: str) -> float:
        """
        Map raw ML probability to a calibrated score using
        per-modality thresholds.

        Instead of treating 0.5 as the midpoint, we use:
          - Video: safe_upper=0.35, dangerous_lower=0.65
          - Audio: safe_upper=0.30, dangerous_lower=0.70

        This prevents the model's uncertain mid-range scores from
        being treated as high-risk.

        Returns a calibrated float in [0, 1].
        """
        thresholds = MODALITY_THRESHOLDS.get(
            modality,
            {"safe_upper": 0.30, "dangerous_lower": 0.70},
        )
        safe_upper = thresholds["safe_upper"]
        danger_lower = thresholds["dangerous_lower"]

        if raw_p <= safe_upper:
            # Safe band: map [0, safe_upper] → [0, 0.30]
            return (raw_p / safe_upper) * 0.30

        elif raw_p >= danger_lower:
            # Dangerous band: map [danger_lower, 1] → [0.65, 1.0]
            return 0.65 + ((raw_p - danger_lower) / (1.0 - danger_lower)) * 0.35

        else:
            # Suspicious band: map linearly → [0.30, 0.65]
            band = danger_lower - safe_upper
            position = (raw_p - safe_upper) / band
            return 0.30 + position * 0.35

    # ------------------------------------------------------------------
    @staticmethod
    def _compute_confidence(
        risk_label: str,
        avg_model_confidence: float,
        raw_ai_scores: Dict[str, float],
        analysis_type: str,
    ) -> tuple[str, str]:
        """
        Determine confidence level and generate a calibration note.

        Returns: (confidence_level, calibration_note)
        """
        note = ""

        # Model itself is low-confidence (score near 0.5)
        if avg_model_confidence < 0.4:
            confidence_level = "low"
            note = (
                "The AI model's confidence is limited for this sample. "
                "This often happens with unusual formats, heavy compression, "
                "or content outside the model's training distribution. "
                "Consider verifying through other means before taking action."
            )
            return confidence_level, note

        # Score is in the suspicious band → inherently uncertain
        if risk_label == "suspicious":
            confidence_level = "low"
            modality = next(iter(raw_ai_scores), "")
            raw_score = raw_ai_scores.get(modality, 0.5)
            thresholds = MODALITY_THRESHOLDS.get(
                modality, {"safe_upper": 0.30, "dangerous_lower": 0.70}
            )
            note = (
                f"The {analysis_type or modality} analysis returned a borderline score "
                f"({raw_score:.0%}), which falls between the Safe threshold "
                f"({thresholds['safe_upper']:.0%}) and Dangerous threshold "
                f"({thresholds['dangerous_lower']:.0%}). "
                "This result is inconclusive. Exercise caution and verify "
                "through an independent channel before trusting this content."
            )
            return confidence_level, note

        # Dangerous but model confidence is medium
        if risk_label == "dangerous" and avg_model_confidence < 0.7:
            confidence_level = "medium"
            note = (
                "The analysis indicates a likely threat, but model confidence "
                "is moderate. The heuristic rules and contextual flags also "
                "contribute to this rating. Treat with high caution."
            )
            return confidence_level, note

        # Safe but model confidence is medium
        if risk_label == "safe" and avg_model_confidence < 0.7:
            confidence_level = "medium"
            note = (
                "The content appears safe, but the model's confidence is "
                "moderate. If you have doubts, verify through official channels."
            )
            return confidence_level, note

        # High confidence
        confidence_level = "high"
        return confidence_level, note

    # ------------------------------------------------------------------
    @staticmethod
    def _build_summary(
        label: str,
        analysis_type: str,
        ai: float,
        rule: float,
        factors: list,
        confidence_level: str,
    ) -> str:
        type_name = {
            "audio": "audio sample",
            "video": "video clip",
            "email": "email",
            "url": "URL",
            "qr": "QR code",
            "image": "image",
        }.get(analysis_type, "content")

        # For email/URL/QR: don't mention "AI" since it's heuristic-only
        is_heuristic_only = analysis_type in ("email", "url", "qr")

        confidence_suffix = (
            "" if confidence_level == "high"
            else " (moderate confidence)" if confidence_level == "medium"
            else " (low confidence — verify independently)"
        )

        if label == "safe":
            if is_heuristic_only:
                return (
                    f"This {type_name} appears legitimate. "
                    f"No significant phishing indicators were detected."
                )
            return (
                f"Analysis of this {type_name} indicates it appears legitimate"
                f"{confidence_suffix}. "
                f"AI confidence: {ai:.0%}, heuristic risk: {rule:.0%}. "
                "No significant threat indicators were detected."
            )
        elif label == "suspicious":
            if is_heuristic_only:
                signal_count = sum(
                    1 for f in factors
                    if f.get("factor") == "rule_adjustment"
                    or (f.get("raw_score", 0) or 0) > 0.3
                )
                return (
                    f"This {type_name} has {signal_count or 'some'} concerning "
                    f"indicators. Heuristic checks flag {rule:.0%} risk. "
                    f"Verify the sender through official channels before acting."
                )
            return (
                f"This {type_name} has borderline characteristics{confidence_suffix}. "
                f"AI model rates threat at {ai:.0%}; heuristic checks flag {rule:.0%} risk. "
                "The result is inconclusive — further verification is strongly recommended."
            )
        else:
            if is_heuristic_only:
                return (
                    f"Strong phishing indicators detected in this {type_name}. "
                    f"Multiple red flags including suspicious sender, dangerous URLs, "
                    f"and manipulation tactics. Do not click links or share information."
                )
            return (
                f"Strong threat indicators detected in this {type_name}{confidence_suffix}. "
                f"AI model rates threat at {ai:.0%}; heuristic checks flag {rule:.0%} risk. "
                "Do not proceed — verify through trusted channels immediately."
            )