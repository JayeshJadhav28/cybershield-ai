"""
Image Analyzer — Deepfake face detection on a single image.

Reuses the same model as video analysis (video_deepfake_detector.h5)
which was trained on 140k-real-and-fake-faces dataset (individual face images).

Returns ai_score and rule_score separately; the scoring engine
applies the 75% AI / 25% rules weighting.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np

from config import settings

logger = logging.getLogger(__name__)


@dataclass
class ImageAnalysisResult:
    """Raw outputs from the image analyzer (before fusion)."""
    ai_probability: float = 0.5       # P(deepfake) from ML model [0, 1]
    rule_score: float = 0.0           # heuristic risk score       [0, 1]
    confidence: float = 0.0           # model confidence
    features: Dict = field(default_factory=dict)
    flags: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    per_face_scores: List[float] = field(default_factory=list)
    model_available: bool = False


class ImageAnalyzer:
    """Stateless analyzer — safe to instantiate once and reuse."""

    def __init__(self):
        from ml.model_loader import ModelLoader
        self._loader = ModelLoader()

    def analyze(self, file_path: str) -> ImageAnalysisResult:
        """
        Full analysis pipeline for one image file.

        Parameters
        ----------
        file_path : path to a PNG/JPG/JPEG/WEBP/BMP file on disk.

        Returns
        -------
        ImageAnalysisResult with ai_probability, rule_score, etc.
        """
        from utils.image_preprocessing import (
            preprocess_image,
            compute_image_heuristics,
        )
        from ml.video_model import predict_faces_batch, get_model_input_shape

        result = ImageAnalysisResult()

        # 1. Preprocess — detect faces, crop, normalize
        try:
            face_crops, meta = preprocess_image(file_path)
            result.metadata = meta
        except Exception as e:
            logger.error("Image preprocessing failed: %s", e)
            result.flags.append("preprocessing_error")
            result.rule_score = 0.5
            return result

        if not face_crops:
            result.flags.append("no_faces_found")
            result.ai_probability = 0.5
            result.rule_score = 0.3
            return result

        # 2. ML inference — reuse the video/face deepfake model
        model = self._loader.get_video_model()

        if model is not None:
            try:
                target_size = get_model_input_shape(model)
                scores = predict_faces_batch(model, face_crops, target_size)
                result.per_face_scores = scores
                result.model_available = True

                if scores:
                    # If multiple faces, take the max (most suspicious)
                    result.ai_probability = float(max(scores))
                    # Also store the average
                    result.metadata["mean_score"] = round(float(np.mean(scores)), 4)
                    result.metadata["max_score"] = round(float(max(scores)), 4)
                    result.confidence = abs(result.ai_probability - 0.5) * 2.0

                    logger.info(
                        "Image model predictions: %s (max=%.3f, mean=%.3f)",
                        [round(s, 3) for s in scores],
                        max(scores), np.mean(scores),
                    )
                else:
                    result.ai_probability = 0.5
            except Exception as e:
                logger.error("Image model inference failed: %s", e)
                result.flags.append("inference_error")
                result.ai_probability = 0.5
        else:
            logger.warning("Video/face model NOT loaded — heuristics only")
            result.flags.append("model_not_loaded")
            result.ai_probability = 0.5

        # 3. Heuristic features + rule score
        try:
            heuristic_feats = compute_image_heuristics(
                file_path, face_crops, meta
            )
            result.features = heuristic_feats
            result.rule_score, rule_flags = self._compute_rule_score(
                heuristic_feats, meta
            )
            result.flags.extend(rule_flags)
        except Exception as e:
            logger.warning("Image heuristic extraction failed: %s", e)
            result.rule_score = 0.0

        # 4. Add face count info
        result.metadata["faces_analyzed"] = len(face_crops)
        if result.per_face_scores:
            result.metadata["per_face_scores"] = [
                round(s, 4) for s in result.per_face_scores
            ]

        logger.info(
            "Image analysis complete: ai=%.3f rule=%.3f flags=%s",
            result.ai_probability, result.rule_score, result.flags,
        )

        return result

    @staticmethod
    def _compute_rule_score(
        feats: Dict, metadata: Dict
    ) -> tuple[float, list[str]]:
        """
        Map heuristic features to a risk score in [0, 1].
        Higher → more likely deepfake.
        """
        score = 0.0
        flags: list[str] = []

        # No face detected — could be non-face content or heavily manipulated
        if feats.get("faces_found", 0) == 0:
            score += 0.10
            flags.append("no_face_detected")

        # Unusually sharp faces (GAN faces are often too sharp)
        mean_blur = feats.get("mean_face_blur", 100)
        if mean_blur > 800:
            score += 0.20
            flags.append("unusually_sharp_face")
        elif mean_blur > 500:
            score += 0.10
            flags.append("sharp_face")

        # Low edge density (deepfakes → smoother skin texture)
        ed = feats.get("mean_edge_density", 0.5)
        if ed < 0.04:
            score += 0.20
            flags.append("very_smooth_texture")
        elif ed < 0.08:
            score += 0.10
            flags.append("smooth_texture")

        # Abnormal saturation (GAN images sometimes have unnatural colors)
        sat_std = feats.get("saturation_std", 50)
        if sat_std < 15:
            score += 0.10
            flags.append("uniform_saturation")
        elif sat_std > 80:
            score += 0.10
            flags.append("extreme_saturation_variance")

        # Very low resolution
        if feats.get("is_low_resolution", False):
            score += 0.05
            flags.append("low_resolution")

        # High noise level can indicate manipulation
        noise = feats.get("noise_level", 20)
        if noise > 60:
            score += 0.10
            flags.append("high_noise_level")
        elif noise < 5:
            score += 0.10
            flags.append("suspiciously_low_noise")

        return min(score, 1.0), flags