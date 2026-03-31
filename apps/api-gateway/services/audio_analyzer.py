"""
Audio Analyzer - ML inference + heuristic scoring for deepfake detection.

Returns ai_score and rule_score separately; the scoring engine
applies the 75 / 25 weighting.

Calibrated thresholds: Safe ≤ 0.30, Suspicious 0.30–0.70, Dangerous ≥ 0.70
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

from config import settings

logger = logging.getLogger(__name__)


@dataclass
class AudioAnalysisResult:
    """Raw outputs from the audio analyzer (before fusion)."""

    ai_probability: float = 0.5
    rule_score: float = 0.0
    confidence: float = 0.0
    features: Dict = field(default_factory=dict)
    flags: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    model_available: bool = False


class AudioAnalyzer:
    """Stateless analyzer - safe to instantiate once and reuse."""

    # Calibrated thresholds for audio deepfake model
    SAFE_UPPER: float = 0.30
    DANGEROUS_LOWER: float = 0.70

    def __init__(self):
        from ml.model_loader import ModelLoader
        self._loader = ModelLoader()

    def analyze(self, file_path: str) -> AudioAnalysisResult:
        """
        Full analysis pipeline for one audio file.

        Parameters
        ----------
        file_path : path to a WAV/MP3/OGG/M4A/FLAC file on disk.

        Returns
        -------
        AudioAnalysisResult with ai_probability, rule_score, etc.
        """
        from utils.audio_preprocessing import (
            extract_heuristic_features,
            load_and_preprocess,
        )
        from ml.audio_model import predict_audio

        result = AudioAnalysisResult()

        # 1. Preprocess -> mel-spectrogram
        try:
            spectrogram, meta = load_and_preprocess(file_path)
            result.metadata = meta
        except Exception as e:
            logger.error("Audio preprocessing failed: %s", e)
            result.flags.append("preprocessing_error")
            result.rule_score = 0.5
            return result

        # 2. ML inference
        model = self._loader.get_audio_model()
        if model is not None:
            ai_prob = predict_audio(model, spectrogram)
            result.ai_probability = ai_prob
            result.confidence = self._compute_confidence(ai_prob)
            result.model_available = True
            logger.info("Audio model prediction: %.4f (confidence: %.4f)",
                        ai_prob, result.confidence)
        else:
            result.ai_probability = 0.5
            result.confidence = 0.0
            result.flags.append("model_not_loaded")
            logger.warning("Audio model NOT loaded — heuristics only")

        # 3. Heuristic features + rule score
        try:
            heuristic_feats = extract_heuristic_features(file_path)
            result.features = heuristic_feats
            result.rule_score, rule_flags = self._compute_rule_score(heuristic_feats)
            result.flags.extend(rule_flags)
            logger.info("Audio heuristics: rule_score=%.3f flags=%s",
                        result.rule_score, rule_flags)
        except Exception as e:
            logger.warning("Heuristic extraction failed: %s", e)
            result.rule_score = 0.0

        # 4. Add calibration-aware flags
        self._add_calibration_flags(result)

        # 5. Store calibration metadata for UI
        result.metadata["calibration"] = {
            "safe_threshold": self.SAFE_UPPER,
            "dangerous_threshold": self.DANGEROUS_LOWER,
            "score_band": self._get_band(result.ai_probability),
        }

        return result

    # ------------------------------------------------------------------
    def _compute_confidence(self, raw_p: float) -> float:
        """
        Compute model confidence using calibrated thresholds.

        Scores in the suspicious band (0.30–0.70) get lower confidence
        than scores clearly in safe or dangerous territory.
        """
        if raw_p <= self.SAFE_UPPER:
            # How far into the safe zone
            return min(1.0, (self.SAFE_UPPER - raw_p) / self.SAFE_UPPER + 0.3)
        elif raw_p >= self.DANGEROUS_LOWER:
            # How far into the dangerous zone
            return min(1.0, (raw_p - self.DANGEROUS_LOWER) / (1.0 - self.DANGEROUS_LOWER) + 0.3)
        else:
            # Suspicious band — inherently low confidence
            band_mid = (self.SAFE_UPPER + self.DANGEROUS_LOWER) / 2
            dist_from_mid = abs(raw_p - band_mid) / ((self.DANGEROUS_LOWER - self.SAFE_UPPER) / 2)
            return dist_from_mid * 0.4  # cap at 0.4 in suspicious band

    def _get_band(self, score: float) -> str:
        if score <= self.SAFE_UPPER:
            return "safe"
        elif score >= self.DANGEROUS_LOWER:
            return "dangerous"
        return "suspicious"

    def _add_calibration_flags(self, result: AudioAnalysisResult) -> None:
        """Add flags to communicate uncertainty to the scoring engine."""
        band = self._get_band(result.ai_probability)

        if band == "suspicious":
            result.flags.append("borderline_score")

        if abs(result.ai_probability - self.SAFE_UPPER) < 0.05:
            result.flags.append("near_safe_threshold")
        elif abs(result.ai_probability - self.DANGEROUS_LOWER) < 0.05:
            result.flags.append("near_dangerous_threshold")

    # ------------------------------------------------------------------
    @staticmethod
    def _compute_rule_score(feats: Dict) -> tuple[float, list[str]]:
        """
        Map heuristic features to a risk score in [0, 1].
        Higher -> more likely deepfake / synthetic.
        """
        score = 0.0
        flags: list[str] = []

        # Very short clips are suspicious
        dur = feats.get("duration_seconds", 0)
        if dur < 1.0:
            score += 0.15
            flags.append("very_short_audio")

        # High spectral flatness -> synthetic-sounding
        sf = feats.get("spectral_flatness_mean", 0)
        if sf > 0.35:
            score += 0.20
            flags.append("high_spectral_flatness")
        elif sf > 0.20:
            score += 0.10

        # Very low ZCR variance -> monotone / robotic
        zcr_var = feats.get("zcr_variance", 1)
        if zcr_var < 0.0005:
            score += 0.15
            flags.append("uniform_zero_crossings")

        # Very low RMS variance -> unnaturally even volume
        rms_var = feats.get("rms_variance", 1)
        if rms_var < 0.0001:
            score += 0.10
            flags.append("flat_energy_envelope")

        # Low high-frequency content -> vocoder artefact
        hf = feats.get("high_freq_ratio", 1)
        if hf < 0.05:
            score += 0.20
            flags.append("low_high_freq_energy")
        elif hf < 0.10:
            score += 0.10

        # Low spectral bandwidth -> narrow-band / synthetic
        bw = feats.get("spectral_bandwidth_mean", 5000)
        if bw < 1500:
            score += 0.15
            flags.append("narrow_spectral_bandwidth")

        return min(score, 1.0), flags