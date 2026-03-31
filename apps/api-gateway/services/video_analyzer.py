"""
Video Analyzer — per-frame face deepfake detection + heuristics.

ZERO MediaPipe dependency. Uses OpenCV-only face detection.
Returns ai_score and rule_score separately for the scoring engine
to apply 75% AI / 25% rules weighting.

Calibrated thresholds: Safe ≤ 0.35, Suspicious 0.35–0.65, Dangerous ≥ 0.65
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np

from config import settings

logger = logging.getLogger(__name__)


@dataclass
class VideoAnalysisResult:
    ai_probability: float = 0.5
    rule_score: float = 0.0
    confidence: float = 0.0
    features: Dict = field(default_factory=dict)
    flags: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    frame_scores: List[float] = field(default_factory=list)
    model_available: bool = False


class VideoAnalyzer:
    # Calibrated thresholds for video deepfake model
    SAFE_UPPER: float = 0.35
    DANGEROUS_LOWER: float = 0.65

    def __init__(self):
        from ml.model_loader import ModelLoader
        self._loader = ModelLoader()

    def analyze(self, file_path: str) -> VideoAnalysisResult:
        from utils.video_preprocessing import (
            extract_frames,
            detect_and_crop_faces,
            compute_frame_heuristics,
        )
        from ml.video_model import predict_faces_batch, get_model_input_shape

        result = VideoAnalysisResult()

        # ── 1. Extract frames ──────────────────────────────────────
        try:
            frames, vid_meta = extract_frames(file_path)
            result.metadata = vid_meta
            logger.info(
                "Extracted %d frames from %s (%.1fs)",
                len(frames), file_path, vid_meta.get("duration_seconds", 0),
            )
        except Exception as e:
            logger.error("Frame extraction failed: %s", e)
            result.flags.append("frame_extraction_error")
            result.ai_probability = 0.5
            result.rule_score = 0.5
            return result

        if not frames:
            result.flags.append("no_frames_extracted")
            result.ai_probability = 0.5
            result.rule_score = 0.5
            return result

        # ── 2. Detect and crop faces ───────────────────────────────
        try:
            face_crops, face_info = detect_and_crop_faces(frames)
            result.metadata.update(face_info)
            logger.info(
                "Face detection: %d detected, %d center-crop fallback",
                face_info.get("faces_detected", 0),
                face_info.get("center_crop_fallback", 0),
            )
        except Exception as e:
            logger.error("Face detection/cropping failed: %s", e)
            result.flags.append("face_detection_error")
            face_crops = []
            face_info = {
                "faces_detected": 0,
                "center_crop_fallback": 0,
                "total_frames_processed": len(frames),
                "face_detection_rate": 0.0,
            }

        # ── 3. ML inference ────────────────────────────────────────
        model = self._loader.get_video_model()

        if model is not None and face_crops:
            try:
                target_size = get_model_input_shape(model)
                scores = predict_faces_batch(model, face_crops, target_size)
                result.frame_scores = scores
                result.model_available = True

                if scores:
                    # Weighted aggregation — detected faces weigh more than fallback crops
                    methods = face_info.get("detection_methods", [])
                    weights = []
                    for i, s in enumerate(scores):
                        if i < len(methods):
                            if methods[i] == "detected":
                                weights.append(1.0)
                            elif methods[i] == "center_crop":
                                weights.append(0.5)
                            else:
                                weights.append(0.3)
                        else:
                            weights.append(0.5)

                    w_arr = np.array(weights)
                    s_arr = np.array(scores)
                    raw_avg = float(np.average(s_arr, weights=w_arr))
                    result.ai_probability = raw_avg

                    # Confidence = distance from decision boundary (0.5)
                    # BUT calibrated to our threshold midpoint (0.50)
                    result.confidence = self._compute_confidence(raw_avg, scores)

                    logger.info(
                        "Model predictions: min=%.3f max=%.3f mean=%.3f weighted=%.3f confidence=%.3f",
                        min(scores), max(scores), np.mean(scores),
                        raw_avg, result.confidence,
                    )
                else:
                    result.ai_probability = 0.5
                    result.confidence = 0.0

            except Exception as e:
                logger.error("Model inference failed: %s", e)
                result.flags.append("inference_error")
                result.ai_probability = 0.5
                result.confidence = 0.0

        elif model is None:
            logger.warning("Video model NOT loaded — heuristics only")
            result.flags.append("model_not_loaded")
            result.ai_probability = 0.5
            result.confidence = 0.0

        elif not face_crops:
            result.flags.append("no_face_crops")
            result.ai_probability = 0.5
            result.confidence = 0.0

        # ── 4. Heuristic scoring ───────────────────────────────────
        try:
            h_feats = compute_frame_heuristics(frames, face_crops, face_info)
            result.features = h_feats
            result.rule_score, rule_flags = self._compute_rule_score(
                h_feats, face_info, result.frame_scores
            )
            result.flags.extend(rule_flags)
        except Exception as e:
            logger.warning("Video heuristics failed: %s", e)
            result.rule_score = 0.3

        # ── 5. Additional calibration-aware flags ──────────────────
        self._add_calibration_flags(result)

        # ── 6. Summary metadata ────────────────────────────────────
        if result.frame_scores:
            suspicious = [s for s in result.frame_scores if s > 0.5]
            result.metadata["suspicious_frames"] = len(suspicious)
            result.metadata["frames_analyzed"] = len(result.frame_scores)
            result.metadata["mean_score"] = round(
                float(np.mean(result.frame_scores)), 4
            )
            result.metadata["max_score"] = round(
                float(max(result.frame_scores)), 4
            )
            result.metadata["calibration"] = {
                "safe_threshold": self.SAFE_UPPER,
                "dangerous_threshold": self.DANGEROUS_LOWER,
                "score_band": self._get_band(result.ai_probability),
            }

        logger.info(
            "Video analysis complete: ai=%.3f rule=%.3f confidence=%.3f flags=%s",
            result.ai_probability, result.rule_score,
            result.confidence, result.flags,
        )

        return result

    # ------------------------------------------------------------------
    def _compute_confidence(
        self, weighted_avg: float, all_scores: List[float]
    ) -> float:
        """
        Compute model confidence based on:
        1. Distance from calibrated thresholds (not from 0.5)
        2. Score consistency across frames (low std = higher confidence)

        Returns value in [0, 1].
        """
        # Distance from nearest threshold
        if weighted_avg <= self.SAFE_UPPER:
            dist = (self.SAFE_UPPER - weighted_avg) / self.SAFE_UPPER
        elif weighted_avg >= self.DANGEROUS_LOWER:
            dist = (weighted_avg - self.DANGEROUS_LOWER) / (1.0 - self.DANGEROUS_LOWER)
        else:
            # In suspicious band — low confidence by design
            band_mid = (self.SAFE_UPPER + self.DANGEROUS_LOWER) / 2
            dist = abs(weighted_avg - band_mid) / ((self.DANGEROUS_LOWER - self.SAFE_UPPER) / 2)
            dist *= 0.5  # cap confidence in suspicious band

        # Penalise inconsistency across frames
        if len(all_scores) >= 3:
            std = float(np.std(all_scores))
            consistency_bonus = max(0.0, 0.3 - std)
        else:
            consistency_bonus = 0.0

        return min(1.0, dist + consistency_bonus)

    def _get_band(self, score: float) -> str:
        if score <= self.SAFE_UPPER:
            return "safe"
        elif score >= self.DANGEROUS_LOWER:
            return "dangerous"
        return "suspicious"

    def _add_calibration_flags(self, result: VideoAnalysisResult) -> None:
        """
        Add flags that help the scoring engine communicate uncertainty.
        """
        band = self._get_band(result.ai_probability)

        if band == "suspicious":
            result.flags.append("borderline_score")

        # Score very close to thresholds → especially uncertain
        if abs(result.ai_probability - self.SAFE_UPPER) < 0.05:
            result.flags.append("near_safe_threshold")
        elif abs(result.ai_probability - self.DANGEROUS_LOWER) < 0.05:
            result.flags.append("near_dangerous_threshold")

        # High frame score variance → model is inconsistent
        if len(result.frame_scores) >= 3:
            std = float(np.std(result.frame_scores))
            if std > 0.20:
                if "temporal_score_inconsistency" not in result.flags:
                    result.flags.append("temporal_score_inconsistency")

    # ------------------------------------------------------------------
    @staticmethod
    def _compute_rule_score(
        feats: Dict,
        face_info: Dict,
        frame_scores: List[float],
    ) -> tuple[float, list[str]]:
        """
        Heuristic risk score in [0, 1].
        Higher = more likely deepfake.
        """
        score = 0.0
        flags: list[str] = []

        # Low face detection rate
        det_rate = feats.get("face_detection_rate", 1.0)
        if det_rate < 0.3:
            score += 0.15
            flags.append("very_low_face_detection")
        elif det_rate < 0.6:
            score += 0.08
            flags.append("low_face_detection_rate")

        # Unusually sharp faces (GANs produce super-sharp faces)
        mean_blur = feats.get("mean_face_blur", 100)
        if mean_blur > 800:
            score += 0.20
            flags.append("unusually_sharp_faces")
        elif mean_blur > 400:
            score += 0.10
            flags.append("sharp_faces")

        # Inconsistent blur across frames (splice indicator)
        blur_var = feats.get("blur_variance", 0)
        if blur_var > 10000:
            score += 0.15
            flags.append("inconsistent_face_quality")
        elif blur_var > 3000:
            score += 0.08

        # Brightness flicker
        bv = feats.get("brightness_variance", 0)
        if bv > 200:
            score += 0.10
            flags.append("brightness_flicker")

        # Low edge density (deepfakes → smoother skin texture)
        ed = feats.get("mean_edge_density", 0.5)
        if ed < 0.05:
            score += 0.15
            flags.append("smooth_texture_anomaly")
        elif ed < 0.10:
            score += 0.08

        # High color variance across crops (inconsistent manipulation)
        cv = feats.get("color_variance", 0)
        if cv > 0.01:
            score += 0.10
            flags.append("color_inconsistency")

        # Temporal inconsistency in model scores
        if len(frame_scores) >= 3:
            sc_arr = np.array(frame_scores)
            std = float(np.std(sc_arr))
            if std > 0.25:
                score += 0.15
                flags.append("temporal_score_inconsistency")
            elif std > 0.15:
                score += 0.08

            # If majority of frames score high, boost rule score
            high_pct = float(np.mean(sc_arr > 0.5))
            if high_pct > 0.6:
                score += 0.10
                flags.append("majority_frames_suspicious")

        return min(score, 1.0), flags