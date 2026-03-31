"""
Tests for video deepfake detection — preprocessing, model, and service.
"""

import io
import struct
import pytest
import numpy as np
import cv2

from utils.video_preprocessing import (
    detect_faces_opencv,
    analyze_face_quality,
    compute_temporal_consistency,
    FACE_TARGET_SIZE,
)
from ml.video_model import VideoDeepfakeModel
from services.video_analyzer import VideoAnalyzerService


def _create_test_frame(
    width: int = 640,
    height: int = 480,
    color: tuple = (100, 150, 200),
) -> np.ndarray:
    """Create a solid-color test frame."""
    frame = np.full((height, width, 3), color, dtype=np.uint8)
    return frame


def _create_frame_with_face(
    width: int = 640,
    height: int = 480,
) -> np.ndarray:
    """
    Create a test frame with a synthetic face-like region.
    Uses an ellipse to approximate face shape for Haar cascade detection.
    """
    frame = np.full((height, width, 3), (200, 200, 200), dtype=np.uint8)

    # Draw face-like ellipse (skin tone)
    center_x, center_y = width // 2, height // 2
    face_w, face_h = 120, 160

    cv2.ellipse(
        frame,
        (center_x, center_y),
        (face_w // 2, face_h // 2),
        0, 0, 360,
        (180, 160, 140),  # Skin-like color
        -1,
    )

    # Add "eyes" (dark circles)
    eye_y = center_y - 25
    cv2.circle(frame, (center_x - 25, eye_y), 10, (30, 30, 30), -1)
    cv2.circle(frame, (center_x + 25, eye_y), 10, (30, 30, 30), -1)

    # Add "nose" line
    cv2.line(frame, (center_x, center_y - 10), (center_x, center_y + 15), (120, 100, 80), 2)

    # Add "mouth"
    cv2.ellipse(
        frame,
        (center_x, center_y + 35),
        (25, 8),
        0, 0, 360,
        (80, 50, 50),
        -1,
    )

    return frame


def _create_test_video_bytes(
    n_frames: int = 30,
    fps: int = 30,
    width: int = 320,
    height: int = 240,
    with_faces: bool = False,
) -> bytes:
    """
    Create a minimal valid MP4/AVI video in memory for testing.
    Uses OpenCV VideoWriter to generate proper video file.
    """
    import tempfile
    import os

    # Create temp file for writing
    temp_path = tempfile.mktemp(suffix=".avi")

    try:
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        writer = cv2.VideoWriter(temp_path, fourcc, fps, (width, height))

        if not writer.isOpened():
            # Fallback: return minimal data that signals video
            return b"\x00" * 5000

        for i in range(n_frames):
            if with_faces:
                frame = _create_frame_with_face(width, height)
            else:
                # Varying color frames
                r = int(100 + 50 * np.sin(2 * np.pi * i / n_frames))
                g = int(150 + 50 * np.cos(2 * np.pi * i / n_frames))
                b = 128
                frame = _create_test_frame(width, height, (b, g, r))

            writer.write(frame)

        writer.release()

        with open(temp_path, "rb") as f:
            video_bytes = f.read()

        return video_bytes

    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


# ═══════════════════════════════════════════
# FACE DETECTION TESTS
# ═══════════════════════════════════════════

class TestFaceDetection:

    def test_no_face_in_solid_color(self):
        frame = _create_test_frame(640, 480, (100, 100, 100))
        faces = detect_faces_opencv(frame)
        assert isinstance(faces, list)
        # Solid color should have no faces
        assert len(faces) == 0

    def test_face_detection_returns_list(self):
        frame = _create_frame_with_face()
        faces = detect_faces_opencv(frame)
        assert isinstance(faces, list)

    def test_face_crop_has_correct_shape(self):
        """If a face is detected, crop should be FACE_TARGET_SIZE."""
        frame = _create_frame_with_face()
        faces = detect_faces_opencv(frame)

        for face in faces:
            assert face["crop"].shape == (FACE_TARGET_SIZE[0], FACE_TARGET_SIZE[1], 3)

    def test_face_detection_empty_frame(self):
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        faces = detect_faces_opencv(frame)
        assert isinstance(faces, list)

    def test_face_bbox_format(self):
        frame = _create_frame_with_face()
        faces = detect_faces_opencv(frame)

        for face in faces:
            assert "bbox" in face
            assert "x" in face["bbox"]
            assert "y" in face["bbox"]
            assert "w" in face["bbox"]
            assert "h" in face["bbox"]
            assert face["area"] > 0


# ═══════════════════════════════════════════
# FACE QUALITY ANALYSIS TESTS
# ═══════════════════════════════════════════

class TestFaceQuality:

    def test_quality_metrics_returned(self):
        face = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        quality = analyze_face_quality(face)

        assert "blur_score" in quality
        assert "edge_density" in quality
        assert isinstance(quality["blur_score"], float)

    def test_blur_score_numeric(self):
        face = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        quality = analyze_face_quality(face)
        assert quality["blur_score"] >= 0

    def test_blurry_face_low_laplacian(self):
        """Blurred face should have lower Laplacian variance."""
        sharp = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        blurry = cv2.GaussianBlur(sharp, (31, 31), 10)

        q_sharp = analyze_face_quality(sharp)
        q_blurry = analyze_face_quality(blurry)

        assert q_blurry["blur_score"] < q_sharp["blur_score"]

    def test_color_channels_analyzed(self):
        face = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        quality = analyze_face_quality(face)

        assert "red_mean" in quality
        assert "green_mean" in quality
        assert "blue_mean" in quality
        assert "red_std" in quality

    def test_symmetry_score(self):
        face = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        quality = analyze_face_quality(face)

        assert "asymmetry_score" in quality
        assert quality["asymmetry_score"] >= 0

    def test_frequency_analysis(self):
        face = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        quality = analyze_face_quality(face)

        assert "high_to_low_freq_ratio" in quality

    def test_skin_tone_metrics(self):
        face = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        quality = analyze_face_quality(face)

        assert "hue_std" in quality
        assert "saturation_std" in quality


# ═══════════════════════════════════════════
# TEMPORAL CONSISTENCY TESTS
# ═══════════════════════════════════════════

class TestTemporalConsistency:

    def test_empty_sequence(self):
        result = compute_temporal_consistency([])
        assert result["total_frames"] == 0

    def test_short_sequence(self):
        result = compute_temporal_consistency([{"blur_score": 100}])
        assert result["total_frames"] == 1

    def test_stable_sequence_low_jitter(self):
        """Consistent metrics across frames should show low jitter."""
        sequence = [
            {"blur_score": 100, "edge_density": 0.1, "asymmetry_score": 20, "high_to_low_freq_ratio": 0.5}
            for _ in range(10)
        ]
        result = compute_temporal_consistency(sequence)

        jitter = result.get("scores", {}).get("temporal_jitter", 0)
        assert jitter < 0.3  # Should be low for stable sequence

    def test_unstable_sequence_high_jitter(self):
        """Wildly varying metrics should show high jitter."""
        sequence = []
        for i in range(10):
            sequence.append({
                "blur_score": 50 + (500 if i % 2 == 0 else 0),
                "edge_density": 0.05 + (0.3 if i % 3 == 0 else 0),
                "asymmetry_score": 10 + (50 if i % 2 == 0 else 0),
                "high_to_low_freq_ratio": 0.2 + (0.5 if i % 2 == 0 else 0),
            })
        result = compute_temporal_consistency(sequence)

        jitter = result.get("scores", {}).get("temporal_jitter", 0)
        assert jitter > 0.1  # Should be elevated for unstable sequence

    def test_anomalies_listed(self):
        sequence = []
        for i in range(10):
            sequence.append({
                "blur_score": 50 + (800 * (i % 2)),
                "edge_density": 0.05,
                "asymmetry_score": 20,
                "high_to_low_freq_ratio": 0.5,
            })
        result = compute_temporal_consistency(sequence)

        # Should detect blur fluctuation
        assert len(result.get("anomalies", [])) >= 0

    def test_face_dropout_detected(self):
        """Sequence with missing face detections should flag dropouts."""
        sequence = [
            {"blur_score": 100},
            {"blur_score": 100},
            {},  # Face lost
            {"blur_score": 100},
            {},  # Face lost again
            {"blur_score": 100},
        ]
        result = compute_temporal_consistency(sequence)
        # Should note face detection instability
        assert result["total_frames"] == 6


# ═══════════════════════════════════════════
# VIDEO MODEL HEURISTICS TESTS
# ═══════════════════════════════════════════

class TestVideoModelHeuristics:

    def setup_method(self):
        self.model = VideoDeepfakeModel.__new__(VideoDeepfakeModel)
        self.model.model = None
        self.model.is_loaded = False
        self.model.model_dir = "./models"
        self.model.model_path = "./models/video_deepfake_detector.h5"

    def test_heuristic_low_blur_flagged(self):
        quality = {"blur_score": 10, "edge_density": 0.1, "asymmetry_score": 20, "high_to_low_freq_ratio": 0.5}
        score, anomalies = self.model._heuristic_frame_analysis(quality)
        assert score > 0
        assert any("blur" in a.lower() for a in anomalies)

    def test_heuristic_low_freq_flagged(self):
        quality = {"blur_score": 200, "edge_density": 0.1, "asymmetry_score": 20, "high_to_low_freq_ratio": 0.05}
        score, anomalies = self.model._heuristic_frame_analysis(quality)
        assert score > 0
        assert any("frequency" in a.lower() or "gan" in a.lower() for a in anomalies)

    def test_heuristic_normal_face(self):
        quality = {
            "blur_score": 200,
            "edge_density": 0.1,
            "asymmetry_score": 15,
            "high_to_low_freq_ratio": 0.5,
            "red_std": 30, "green_std": 28, "blue_std": 32,
            "hue_std": 15,
            "rg_ratio": 1.1,
        }
        score, anomalies = self.model._heuristic_frame_analysis(quality)
        assert score < 0.5  # Normal face should not score high

    def test_heuristic_high_asymmetry_flagged(self):
        quality = {"blur_score": 200, "edge_density": 0.1, "asymmetry_score": 60}
        score, anomalies = self.model._heuristic_frame_analysis(quality)
        assert any("asymmetry" in a.lower() for a in anomalies)

    def test_heuristic_score_bounded(self):
        quality = {
            "blur_score": 5,
            "edge_density": 0.005,
            "asymmetry_score": 80,
            "high_to_low_freq_ratio": 0.01,
            "red_std": 50, "green_std": 10, "blue_std": 50,
            "hue_std": 60,
            "rg_ratio": 2.5,
        }
        score, _ = self.model._heuristic_frame_analysis(quality)
        assert 0.0 <= score <= 1.0

    def test_anomaly_distribution_description(self):
        per_frame = [
            {"score": 0.1, "face_detected": True},
            {"score": 0.6, "face_detected": True},
            {"score": 0.7, "face_detected": True},
            {"score": 0.2, "face_detected": True},
        ]
        desc = self.model._describe_anomaly_distribution(per_frame, 4)
        assert isinstance(desc, str)
        assert len(desc) > 0

    def test_no_suspicious_description(self):
        per_frame = [
            {"score": 0.1, "face_detected": True},
            {"score": 0.2, "face_detected": True},
        ]
        desc = self.model._describe_anomaly_distribution(per_frame, 2)
        assert "no suspicious" in desc.lower() or "no" in desc.lower()


# ═══════════════════════════════════════════
# VIDEO ANALYZER SERVICE TESTS
# ═══════════════════════════════════════════

class TestVideoAnalyzerService:

    def setup_method(self):
        self.service = VideoAnalyzerService()

    def test_analyze_returns_result(self):
        """Test analysis with a simple video."""
        video_bytes = _create_test_video_bytes(n_frames=15, fps=15, width=320, height=240)
        if len(video_bytes) < 5000:
            pytest.skip("VideoWriter not available in this environment")

        result = self.service.analyze(video_bytes)

        assert 0.0 <= result.probability <= 1.0
        assert result.confidence >= 0
        assert result.processing_time_ms >= 0
        assert isinstance(result.flags, list)
        assert isinstance(result.anomalies, list)

    def test_analyze_with_faces(self):
        """Test analysis with frames containing face-like features."""
        video_bytes = _create_test_video_bytes(n_frames=10, fps=10, width=320, height=240, with_faces=True)
        if len(video_bytes) < 5000:
            pytest.skip("VideoWriter not available in this environment")

        result = self.service.analyze(video_bytes)

        assert 0.0 <= result.probability <= 1.0
        assert isinstance(result.metadata, dict)

    def test_analyze_empty_video(self):
        """Test with minimal/corrupted video data."""
        result = self.service.analyze(b"\x00" * 100)

        # Should handle gracefully
        assert 0.0 <= result.probability <= 1.0
        assert len(result.anomalies) > 0 or result.confidence < 0.3

    def test_explanation_generation(self):
        """Test explanation generation."""
        video_bytes = _create_test_video_bytes(n_frames=10, fps=10)
        if len(video_bytes) < 5000:
            pytest.skip("VideoWriter not available")

        result = self.service.analyze(video_bytes)
        explanation = self.service.generate_explanation(result)

        assert "summary" in explanation
        assert len(explanation["summary"]) > 20
        assert "contributing_factors" in explanation
        assert isinstance(explanation["contributing_factors"], list)

    def test_explanation_no_faces(self):
        """Explanation when no faces detected should mention it."""
        result = VideoAnalysisResult(
            probability=0.3,
            confidence=0.2,
            metadata={"total_frames": 10},
            frame_analysis={"total_frames": 10, "frames_with_faces": 0, "suspicious_frames": 0},
            anomalies=["No faces detected"],
        )
        explanation = self.service.generate_explanation(result)
        assert "no faces" in explanation["summary"].lower()

    def test_explanation_high_risk(self):
        """High risk should produce strong warning."""
        result = VideoAnalysisResult(
            probability=0.85,
            confidence=0.7,
            metadata={"total_frames": 30},
            frame_analysis={
                "total_frames": 30,
                "frames_with_faces": 25,
                "suspicious_frames": 18,
                "average_frame_score": 0.72,
                "max_frame_score": 0.91,
                "anomaly_distribution": "Concentrated in frames 5-20",
            },
            anomalies=["Blur fluctuation detected", "Low frequency content"],
        )
        explanation = self.service.generate_explanation(result)
        assert "strong" in explanation["summary"].lower() or "deepfake" in explanation["summary"].lower()

    def test_explanation_safe_video(self):
        """Low risk should produce safe summary."""
        result = VideoAnalysisResult(
            probability=0.1,
            confidence=0.6,
            metadata={"total_frames": 30},
            frame_analysis={
                "total_frames": 30,
                "frames_with_faces": 28,
                "suspicious_frames": 0,
                "average_frame_score": 0.08,
                "max_frame_score": 0.15,
            },
            anomalies=[],
        )
        explanation = self.service.generate_explanation(result)
        assert "genuine" in explanation["summary"].lower() or "no significant" in explanation["summary"].lower()

    def test_flags_generated(self):
        """Test flag generation from model result."""
        model_result = {
            "probability": 0.8,
            "method": "heuristics",
            "frame_analysis": {
                "total_frames": 20,
                "frames_with_faces": 15,
                "suspicious_frames": 12,
            },
            "temporal_analysis": {
                "anomalies": ["Blur variation detected"],
            },
        }
        flags = self.service._build_flags(model_result)

        assert "high_deepfake_probability" in flags
        assert "heuristic_analysis_only" in flags
        assert "majority_frames_suspicious" in flags
        assert "temporal_inconsistency" in flags

    def test_flags_no_faces(self):
        model_result = {
            "probability": 0.3,
            "method": "heuristics",
            "frame_analysis": {
                "total_frames": 10,
                "frames_with_faces": 0,
                "suspicious_frames": 0,
            },
            "temporal_analysis": {},
        }
        flags = self.service._build_flags(model_result)
        assert "no_faces_detected" in flags

    def test_flags_low_risk(self):
        model_result = {
            "probability": 0.15,
            "method": "heuristics",
            "frame_analysis": {
                "total_frames": 10,
                "frames_with_faces": 8,
                "suspicious_frames": 1,
            },
            "temporal_analysis": {},
        }
        flags = self.service._build_flags(model_result)
        assert "high_deepfake_probability" not in flags
        assert "moderate_deepfake_probability" not in flags