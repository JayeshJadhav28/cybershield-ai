"""
Tests for AudioAnalyzer — mocked model + real heuristics.
"""

import math
import wave
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest


@pytest.fixture
def analyzer():
    # Patch the model loader used by AudioAnalyzer.__init__()
    with patch("ml.model_loader.ModelLoader") as MockLoader:
        instance = MockLoader.return_value

        # Simulate a model that returns a fixed deepfake probability
        mock_model = MagicMock()
        instance.get_audio_model.return_value = mock_model

        from services.audio_analyzer import AudioAnalyzer

        a = AudioAnalyzer()
        a._loader = instance
        yield a, mock_model


def _make_sine_wav(path: str | Path, sr: int = 16000, duration: float = 3.0, freq: float = 440.0):
    """Write a simple sine-wave WAV for testing (no external deps)."""
    path = str(path)
    n_samples = int(sr * duration)
    t = np.arange(n_samples, dtype=np.float32) / float(sr)
    y = 0.5 * np.sin(2.0 * math.pi * freq * t)
    pcm = (y * 32767).astype(np.int16)

    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit PCM
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())


class TestAudioAnalyzer:
    def test_returns_ai_probability_from_model(self, analyzer, tmp_path):
        a, _ = analyzer
        wav = tmp_path / "test.wav"
        _make_sine_wav(wav)

        with patch("ml.audio_model.predict_audio", return_value=0.82):
            result = a.analyze(str(wav))

        assert 0.0 <= result.ai_probability <= 1.0
        assert result.model_available or "model_not_loaded" in result.flags

    def test_returns_rule_score(self, analyzer, tmp_path):
        a, _ = analyzer
        wav = tmp_path / "test.wav"
        _make_sine_wav(wav)

        with patch("ml.audio_model.predict_audio", return_value=0.5):
            result = a.analyze(str(wav))

        assert 0.0 <= result.rule_score <= 1.0

    def test_very_short_audio_flagged(self, analyzer, tmp_path):
        a, _ = analyzer
        wav = tmp_path / "short.wav"
        _make_sine_wav(wav, duration=0.3)

        with patch("ml.audio_model.predict_audio", return_value=0.5):
            result = a.analyze(str(wav))

        assert "very_short_audio" in result.flags

    def test_no_model_still_returns_result(self, tmp_path):
        """When model can't load, heuristics still produce a result."""
        with patch("ml.model_loader.ModelLoader") as MockLoader:
            MockLoader.return_value.get_audio_model.return_value = None

            from services.audio_analyzer import AudioAnalyzer

            a = AudioAnalyzer()
            a._loader = MockLoader.return_value

            wav = tmp_path / "test.wav"
            _make_sine_wav(wav)
            result = a.analyze(str(wav))

        assert result.ai_probability == 0.5
        assert "model_not_loaded" in result.flags
        assert 0.0 <= result.rule_score <= 1.0

"""
Tests for audio deepfake detection — preprocessing, model, and service.
"""

import io
import struct
import pytest
import numpy as np

from utils.audio_preprocessing import (
    extract_mel_spectrogram,
    extract_spectral_features,
    get_audio_metadata,
    load_audio,
    TARGET_SR,
    N_MELS,
    SPECTROGRAM_WIDTH,
)
from services.audio_analyzer import AudioAnalyzerService


def _generate_wav_bytes(
    duration_s: float = 2.0,
    sample_rate: int = 16000,
    frequency: float = 440.0,
) -> bytes:
    """
    Generate a valid WAV file in memory for testing.
    Creates a pure sine wave tone.
    """
    n_samples = int(duration_s * sample_rate)
    t = np.linspace(0, duration_s, n_samples, endpoint=False)
    audio = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)

    buf = io.BytesIO()
    # WAV header
    n_channels = 1
    sample_width = 2  # 16-bit
    data_size = n_samples * n_channels * sample_width

    buf.write(b"RIFF")
    buf.write(struct.pack("<I", 36 + data_size))
    buf.write(b"WAVE")
    buf.write(b"fmt ")
    buf.write(struct.pack("<I", 16))          # chunk size
    buf.write(struct.pack("<H", 1))           # PCM format
    buf.write(struct.pack("<H", n_channels))
    buf.write(struct.pack("<I", sample_rate))
    buf.write(struct.pack("<I", sample_rate * n_channels * sample_width))
    buf.write(struct.pack("<H", n_channels * sample_width))
    buf.write(struct.pack("<H", sample_width * 8))
    buf.write(b"data")
    buf.write(struct.pack("<I", data_size))
    buf.write(audio.tobytes())

    return buf.getvalue()


def _generate_noise_wav(duration_s: float = 2.0, sample_rate: int = 16000) -> bytes:
    """Generate random noise WAV for testing."""
    n_samples = int(duration_s * sample_rate)
    noise = (np.random.randn(n_samples) * 5000).astype(np.int16)

    buf = io.BytesIO()
    n_channels = 1
    sample_width = 2
    data_size = n_samples * n_channels * sample_width

    buf.write(b"RIFF")
    buf.write(struct.pack("<I", 36 + data_size))
    buf.write(b"WAVE")
    buf.write(b"fmt ")
    buf.write(struct.pack("<I", 16))
    buf.write(struct.pack("<H", 1))
    buf.write(struct.pack("<H", n_channels))
    buf.write(struct.pack("<I", sample_rate))
    buf.write(struct.pack("<I", sample_rate * n_channels * sample_width))
    buf.write(struct.pack("<H", n_channels * sample_width))
    buf.write(struct.pack("<H", sample_width * 8))
    buf.write(b"data")
    buf.write(struct.pack("<I", data_size))
    buf.write(noise.tobytes())

    return buf.getvalue()


def _generate_speech_like_wav(duration_s: float = 3.0, sample_rate: int = 16000) -> bytes:
    """Generate speech-like signal (multi-frequency with modulation) for testing."""
    n_samples = int(duration_s * sample_rate)
    t = np.linspace(0, duration_s, n_samples, endpoint=False)

    # Speech-like: multiple harmonics with amplitude modulation
    f0 = 150  # Fundamental frequency
    signal = np.zeros(n_samples)
    for harmonic in range(1, 6):
        freq = f0 * harmonic
        amp = 1.0 / harmonic
        signal += amp * np.sin(2 * np.pi * freq * t)

    # Amplitude modulation (simulates speech rhythm)
    envelope = 0.5 + 0.5 * np.sin(2 * np.pi * 3 * t)
    signal *= envelope

    audio = (signal / np.max(np.abs(signal)) * 20000).astype(np.int16)

    buf = io.BytesIO()
    n_channels = 1
    sample_width = 2
    data_size = n_samples * n_channels * sample_width

    buf.write(b"RIFF")
    buf.write(struct.pack("<I", 36 + data_size))
    buf.write(b"WAVE")
    buf.write(b"fmt ")
    buf.write(struct.pack("<I", 16))
    buf.write(struct.pack("<H", 1))
    buf.write(struct.pack("<H", n_channels))
    buf.write(struct.pack("<I", sample_rate))
    buf.write(struct.pack("<I", sample_rate * n_channels * sample_width))
    buf.write(struct.pack("<H", n_channels * sample_width))
    buf.write(struct.pack("<H", sample_width * 8))
    buf.write(b"data")
    buf.write(struct.pack("<I", data_size))
    buf.write(audio.tobytes())

    return buf.getvalue()


# ═══════════════════════════════════════════
# AUDIO LOADING TESTS
# ═══════════════════════════════════════════

class TestAudioLoading:

    def test_load_wav_from_bytes(self):
        wav_bytes = _generate_wav_bytes(duration_s=1.0)
        y, sr = load_audio(wav_bytes, target_sr=TARGET_SR)
        assert sr == TARGET_SR
        assert len(y) > 0
        assert isinstance(y, np.ndarray)

    def test_load_wav_resamples(self):
        # Generate at 44100 Hz
        wav_bytes = _generate_wav_bytes(duration_s=1.0, sample_rate=44100)
        y, sr = load_audio(wav_bytes, target_sr=16000)
        assert sr == 16000

    def test_load_wav_trims_silence(self):
        # Generate very quiet audio then normal
        wav_bytes = _generate_wav_bytes(duration_s=2.0, frequency=440.0)
        y, sr = load_audio(wav_bytes)
        # Trimmed audio should not be longer than original
        original_samples = int(2.0 * TARGET_SR)
        assert len(y) <= original_samples + TARGET_SR  # Allow some margin


# ═══════════════════════════════════════════
# MEL SPECTROGRAM TESTS
# ═══════════════════════════════════════════

class TestMelSpectrogram:

    def test_spectrogram_shape(self):
        wav_bytes = _generate_wav_bytes(duration_s=2.0)
        y, sr = load_audio(wav_bytes)
        spec = extract_mel_spectrogram(y, sr)
        assert spec.shape == (N_MELS, SPECTROGRAM_WIDTH, 1)

    def test_spectrogram_normalized(self):
        wav_bytes = _generate_wav_bytes(duration_s=2.0)
        y, sr = load_audio(wav_bytes)
        spec = extract_mel_spectrogram(y, sr)
        assert spec.min() >= 0.0
        assert spec.max() <= 1.0

    def test_short_audio_padded(self):
        # Very short audio (0.5s) should be padded to fixed width
        wav_bytes = _generate_wav_bytes(duration_s=0.5)
        y, sr = load_audio(wav_bytes)
        spec = extract_mel_spectrogram(y, sr)
        assert spec.shape == (N_MELS, SPECTROGRAM_WIDTH, 1)

    def test_long_audio_truncated(self):
        # Longer audio should be center-cropped to fixed width
        wav_bytes = _generate_wav_bytes(duration_s=10.0)
        y, sr = load_audio(wav_bytes)
        spec = extract_mel_spectrogram(y, sr)
        assert spec.shape == (N_MELS, SPECTROGRAM_WIDTH, 1)

    def test_spectrogram_not_all_zeros(self):
        wav_bytes = _generate_wav_bytes(duration_s=2.0, frequency=1000.0)
        y, sr = load_audio(wav_bytes)
        spec = extract_mel_spectrogram(y, sr)
        assert spec.sum() > 0


# ═══════════════════════════════════════════
# SPECTRAL FEATURES TESTS
# ═══════════════════════════════════════════

class TestSpectralFeatures:

    def test_features_extracted(self):
        wav_bytes = _generate_speech_like_wav(duration_s=3.0)
        y, sr = load_audio(wav_bytes)
        features = extract_spectral_features(y, sr)

        assert "spectral_centroid_mean" in features
        assert "spectral_bandwidth_mean" in features
        assert "zero_crossing_rate_mean" in features
        assert "rms_energy_mean" in features
        assert "harmonic_to_noise_ratio" in features

    def test_mfcc_features(self):
        wav_bytes = _generate_speech_like_wav()
        y, sr = load_audio(wav_bytes)
        features = extract_spectral_features(y, sr)

        for i in range(13):
            assert f"mfcc_{i}_mean" in features
            assert f"mfcc_{i}_std" in features

    def test_pitch_features(self):
        wav_bytes = _generate_speech_like_wav()
        y, sr = load_audio(wav_bytes)
        features = extract_spectral_features(y, sr)

        assert "pitch_mean" in features
        assert "pitch_std" in features
        assert "pitch_range" in features
        assert "voiced_fraction" in features

    def test_features_are_numeric(self):
        wav_bytes = _generate_wav_bytes(duration_s=2.0)
        y, sr = load_audio(wav_bytes)
        features = extract_spectral_features(y, sr)

        for key, value in features.items():
            assert isinstance(value, (int, float)), f"{key} is not numeric: {type(value)}"

    def test_features_non_negative_rms(self):
        wav_bytes = _generate_wav_bytes()
        y, sr = load_audio(wav_bytes)
        features = extract_spectral_features(y, sr)
        assert features["rms_energy_mean"] >= 0

    def test_noise_vs_tone_features_differ(self):
        tone_bytes = _generate_wav_bytes(duration_s=2.0, frequency=440.0)
        noise_bytes = _generate_noise_wav(duration_s=2.0)

        y_tone, sr_tone = load_audio(tone_bytes)
        y_noise, sr_noise = load_audio(noise_bytes)

        f_tone = extract_spectral_features(y_tone, sr_tone)
        f_noise = extract_spectral_features(y_noise, sr_noise)

        # Noise should have higher ZCR than pure tone
        assert f_noise["zero_crossing_rate_mean"] > f_tone["zero_crossing_rate_mean"]


# ═══════════════════════════════════════════
# AUDIO METADATA TESTS
# ═══════════════════════════════════════════

class TestAudioMetadata:

    def test_metadata_extraction(self):
        wav_bytes = _generate_wav_bytes(duration_s=3.0, sample_rate=16000)
        metadata = get_audio_metadata(wav_bytes)

        assert "duration_seconds" in metadata
        assert abs(metadata["duration_seconds"] - 3.0) < 0.5
        assert metadata["sample_rate"] == 16000 or metadata["sample_rate"] > 0

    def test_invalid_audio_metadata(self):
        metadata = get_audio_metadata(b"not audio data")
        assert "error" in metadata or metadata["duration_seconds"] == 0.0


# ═══════════════════════════════════════════
# AUDIO ANALYZER SERVICE TESTS
# ═══════════════════════════════════════════

class TestAudioAnalyzerService:

    def setup_method(self):
        self.service = AudioAnalyzerService()

    def test_analyze_sine_wave(self):
        """Pure sine wave should not strongly indicate deepfake."""
        wav_bytes = _generate_wav_bytes(duration_s=2.0, frequency=440.0)
        result = self.service.analyze(wav_bytes)

        assert 0.0 <= result.probability <= 1.0
        assert result.confidence > 0
        assert result.processing_time_ms >= 0
        assert isinstance(result.features, dict)
        assert isinstance(result.metadata, dict)

    def test_analyze_speech_like(self):
        """Speech-like signal should produce reasonable analysis."""
        wav_bytes = _generate_speech_like_wav(duration_s=3.0)
        result = self.service.analyze(wav_bytes)

        assert 0.0 <= result.probability <= 1.0
        assert result.method in ["cnn", "heuristics"]
        assert len(result.anomalies) >= 0

    def test_analyze_noise(self):
        """Random noise analysis."""
        wav_bytes = _generate_noise_wav(duration_s=2.0)
        result = self.service.analyze(wav_bytes)

        assert 0.0 <= result.probability <= 1.0
        assert result.processing_time_ms >= 0

    def test_analyze_returns_flags(self):
        wav_bytes = _generate_wav_bytes(duration_s=2.0)
        result = self.service.analyze(wav_bytes)
        assert isinstance(result.flags, list)

    def test_explanation_generation(self):
        """Test explanation generation from result."""
        wav_bytes = _generate_speech_like_wav(duration_s=2.0)
        result = self.service.analyze(wav_bytes)

        explanation = self.service.generate_explanation(result)

        assert "summary" in explanation
        assert len(explanation["summary"]) > 20
        assert "contributing_factors" in explanation
        assert isinstance(explanation["contributing_factors"], list)

    def test_explanation_safe_audio(self):
        """Low-risk audio should have appropriate explanation."""
        wav_bytes = _generate_wav_bytes(duration_s=2.0, frequency=440.0)
        result = self.service.analyze(wav_bytes)
        result.probability = 0.1  # Force low probability for test

        explanation = self.service.generate_explanation(result)
        assert "genuine" in explanation["summary"].lower() or "no significant" in explanation["summary"].lower()

    def test_explanation_dangerous_audio(self):
        """High-risk audio should have appropriate explanation."""
        wav_bytes = _generate_wav_bytes(duration_s=2.0)
        result = self.service.analyze(wav_bytes)
        result.probability = 0.85  # Force high probability for test

        explanation = self.service.generate_explanation(result)
        assert "strong" in explanation["summary"].lower() or "ai-generated" in explanation["summary"].lower()

    def test_metadata_in_result(self):
        wav_bytes = _generate_wav_bytes(duration_s=2.5)
        result = self.service.analyze(wav_bytes)

        assert result.metadata.get("duration_seconds", 0) > 0

    def test_features_in_result(self):
        wav_bytes = _generate_speech_like_wav(duration_s=2.0)
        result = self.service.analyze(wav_bytes)

        # Should have spectral features
        assert len(result.features) > 0
        assert "spectral_centroid_mean" in result.features or "error" in str(result.metadata)

    def test_multiple_analyses_consistent(self):
        """Same input should produce same output."""
        wav_bytes = _generate_wav_bytes(duration_s=2.0, frequency=440.0)

        result1 = self.service.analyze(wav_bytes)
        result2 = self.service.analyze(wav_bytes)

        assert abs(result1.probability - result2.probability) < 0.01