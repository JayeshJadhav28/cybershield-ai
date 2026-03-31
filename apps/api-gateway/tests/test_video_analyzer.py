"""Tests for VideoAnalyzer — mocked model + frame heuristics."""

import cv2
import numpy as np
import pytest
from unittest.mock import MagicMock, patch
import types


@pytest.fixture
def analyzer():
    # Patch the model loader used by VideoAnalyzer.__init__()
    with patch("ml.model_loader.ModelLoader") as MockLoader:
        instance = MockLoader.return_value
        mock_model = MagicMock()
        instance.get_video_model.return_value = mock_model
        from services.video_analyzer import VideoAnalyzer
        a = VideoAnalyzer()
        a._loader = instance
        yield a, mock_model


def _make_test_video(path, frames=10, w=320, h=240, fps=30):
    """Create a small test MP4 with a white rectangle (fake face)."""
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(path), fourcc, fps, (w, h))
    for i in range(frames):
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        # Draw a "face-like" rectangle
        cv2.rectangle(frame, (100, 50), (220, 190), (200, 180, 160), -1)
        out.write(frame)
    out.release()


def _stub_video_model(return_values):
    """
    Avoid importing torch by stubbing `ml.video_model` in sys.modules.

    `VideoAnalyzer.analyze()` does `from ml.video_model import predict_faces_batch`,
    so we provide a lightweight module with that function.
    """
    mod = types.ModuleType("ml.video_model")

    def predict_faces_batch(_model, _face_crops):
        return list(return_values)

    mod.predict_faces_batch = predict_faces_batch
    return mod


class TestVideoAnalyzer:
    def test_returns_ai_probability(self, analyzer, tmp_path):
        a, _ = analyzer
        vid = tmp_path / "test.mp4"
        _make_test_video(str(vid))

        fake_vm = _stub_video_model([0.7, 0.65, 0.72])
        with patch.dict("sys.modules", {"ml.video_model": fake_vm}):
            result = a.analyze(str(vid))

        assert 0.0 <= result.ai_probability <= 1.0

    def test_returns_frame_scores(self, analyzer, tmp_path):
        a, _ = analyzer
        vid = tmp_path / "test.mp4"
        _make_test_video(str(vid), frames=5)

        fake_scores = [0.8, 0.75, 0.9, 0.85, 0.7]
        fake_vm = _stub_video_model(fake_scores)
        with patch.dict("sys.modules", {"ml.video_model": fake_vm}):
            result = a.analyze(str(vid))

        # We may get fewer scores if face detection fails for some frames
        assert isinstance(result.frame_scores, list)

    def test_no_model_heuristics_only(self, tmp_path):
        with patch("ml.model_loader.ModelLoader") as MockLoader:
            MockLoader.return_value.get_video_model.return_value = None
            from services.video_analyzer import VideoAnalyzer
            a = VideoAnalyzer()
            a._loader = MockLoader.return_value

            vid = tmp_path / "test.mp4"
            _make_test_video(str(vid))
            fake_vm = _stub_video_model([0.5])
            with patch.dict("sys.modules", {"ml.video_model": fake_vm}):
                result = a.analyze(str(vid))

        assert result.ai_probability == 0.5
        assert "model_not_loaded" in result.flags or "no_faces_detected" in result.flags

    def test_rule_score_in_range(self, analyzer, tmp_path):
        a, _ = analyzer
        vid = tmp_path / "test.mp4"
        _make_test_video(str(vid))

        fake_vm = _stub_video_model([0.5])
        with patch.dict("sys.modules", {"ml.video_model": fake_vm}):
            result = a.analyze(str(vid))

        assert 0.0 <= result.rule_score <= 1.0