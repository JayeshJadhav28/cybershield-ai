"""
Audio preprocessing — must match training pipeline exactly.

Training params (birdy654/deep-voice dataset):
    sr         = 16 000 Hz
    duration   = 4.0 s   (pad / trim)
    n_mels     = 128
    hop_length = 512
    output     = (128, 128)  float32  in [0, 1]
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np

from config import settings

logger = logging.getLogger(__name__)


def load_and_preprocess(
    file_path: str,
    sr: int | None = None,
    duration: float | None = None,
    n_mels: int | None = None,
    hop_length: int | None = None,
    target_shape: Tuple[int, int] | None = None,
) -> Tuple[np.ndarray, Dict]:
    """
    Load an audio file and return (spectrogram, metadata).

    Returns
    -------
    spectrogram : np.ndarray  (H, W)  float32 in [0, 1]
    metadata    : dict  with duration_seconds, sample_rate, etc.
    """
    import librosa

    sr = sr or settings.AUDIO_SAMPLE_RATE
    duration = duration or settings.AUDIO_DURATION_S
    n_mels = n_mels or settings.AUDIO_N_MELS
    hop_length = hop_length or settings.AUDIO_HOP_LENGTH
    target_shape = target_shape or tuple(settings.AUDIO_SPEC_SHAPE)

    # 1. Load + resample to mono
    y, _actual_sr = librosa.load(file_path, sr=sr, mono=True)
    raw_duration = len(y) / sr if sr else 0.0

    # 2. Trim silence
    y_trimmed, _ = librosa.effects.trim(y, top_db=25)
    if len(y_trimmed) > sr * 0.5:  # keep trimmed if still > 0.5 s
        y = y_trimmed

    # 3. Pad / truncate to fixed length
    target_len = int(sr * duration)
    if len(y) < target_len:
        y = np.pad(y, (0, target_len - len(y)), mode="constant")
    else:
        y = y[:target_len]

    # 4. Mel-spectrogram -> dB -> [0, 1]
    S = librosa.feature.melspectrogram(
        y=y,
        sr=sr,
        n_mels=n_mels,
        hop_length=hop_length,
        fmax=sr // 2,
    )
    S_db = librosa.power_to_db(S, ref=np.max)
    s_min, s_max = float(S_db.min()), float(S_db.max())
    S_norm = (S_db - s_min) / (s_max - s_min + 1e-8)

    # 5. Resize to target shape (e.g. 128x128)
    import cv2

    # cv2.resize expects (width, height)
    out_w, out_h = int(target_shape[1]), int(target_shape[0])
    S_resized = cv2.resize(
        S_norm.astype(np.float32),
        (out_w, out_h),
        interpolation=cv2.INTER_LINEAR,
    )

    metadata = {
        "duration_seconds": round(raw_duration, 2),
        "sample_rate": sr,
        "n_mels": n_mels,
        "hop_length": hop_length,
        "trimmed_duration": round(len(y) / sr, 2),
        "format": Path(file_path).suffix.lstrip("."),
        "num_samples": int(len(y)),
        "rms_energy": float(np.sqrt(np.mean(y**2))) if len(y) else 0.0,
        "is_silent": float(np.sqrt(np.mean(y**2))) < 0.001 if len(y) else True,
    }

    return S_resized.astype(np.float32), metadata


def extract_heuristic_features(file_path: str) -> Dict:
    """
    Compute rule-based / heuristic features from raw audio.

    Returns dict with numeric indicators used by the rule scorer.
    """
    import librosa

    sr = settings.AUDIO_SAMPLE_RATE
    y, _ = librosa.load(file_path, sr=sr, mono=True)
    duration = len(y) / sr if sr else 0.0

    features: Dict[str, Any] = {"duration_seconds": round(duration, 2)}

    # Spectral flatness (synthetic audio -> higher flatness)
    sf = librosa.feature.spectral_flatness(y=y)
    features["spectral_flatness_mean"] = float(np.mean(sf))

    # Zero-crossing rate variance (monotone -> low variance)
    zcr = librosa.feature.zero_crossing_rate(y)
    features["zcr_variance"] = float(np.var(zcr))

    # RMS energy variance (robotic -> low variance)
    rms = librosa.feature.rms(y=y)
    features["rms_variance"] = float(np.var(rms))

    # High-frequency energy ratio (vocoders drop HF energy)
    fft_vals = np.abs(np.fft.rfft(y))
    freqs = np.fft.rfftfreq(len(y), 1.0 / sr) if len(y) and sr else np.array([])
    hf_mask = freqs > 4000
    total_energy = float(np.sum(fft_vals**2) + 1e-12)
    hf_energy = float(np.sum((fft_vals[hf_mask]) ** 2)) if hf_mask.size else 0.0
    features["high_freq_ratio"] = float(hf_energy / total_energy) if total_energy else 0.0

    # Spectral bandwidth mean
    bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)
    features["spectral_bandwidth_mean"] = float(np.mean(bw))

    return features


def compute_mel_spectrogram(
    y: np.ndarray,
    sr: int = settings.AUDIO_SAMPLE_RATE,
    n_mels: int = settings.AUDIO_N_MELS,
    hop_length: int = settings.AUDIO_HOP_LENGTH,
    n_fft: int = 2048,
) -> np.ndarray:
    import librosa
    y_trimmed, _ = librosa.effects.trim(y, top_db=25)
    if len(y_trimmed) < sr * 0.5:
        y_trimmed = y

    mel = librosa.feature.melspectrogram(
        y=y_trimmed, sr=sr, n_mels=n_mels,
        n_fft=n_fft, hop_length=hop_length, fmax=sr // 2,
    )
    mel_db = librosa.power_to_db(mel, ref=np.max)
    return mel_db


def prepare_spectrogram_for_model(
    mel_db: np.ndarray,
    target_height: int = settings.AUDIO_N_MELS,
    target_width: int = int(tuple(settings.AUDIO_SPEC_SHAPE)[1]),
) -> np.ndarray:
    """Returns shape (1, target_height, target_width) normalized to [0,1]."""
    mel_min = mel_db.min()
    mel_max = mel_db.max()
    if mel_max - mel_min > 0:
        mel_norm = (mel_db - mel_min) / (mel_max - mel_min)
    else:
        mel_norm = np.zeros_like(mel_db)

    current_width = mel_norm.shape[1]
    if current_width != target_width:
        indices = np.linspace(0, current_width - 1, target_width).astype(int)
        mel_norm = mel_norm[:, indices]

    if mel_norm.shape[0] != target_height:
        row_indices = np.linspace(0, mel_norm.shape[0] - 1, target_height).astype(int)
        mel_norm = mel_norm[row_indices, :]

    return mel_norm[np.newaxis, :, :].astype(np.float32)


def extract_spectral_features(y: np.ndarray, sr: int = settings.AUDIO_SAMPLE_RATE) -> Dict[str, Any]:
    import librosa
    features = {}
    try:
        cent = librosa.feature.spectral_centroid(y=y, sr=sr)
        features["spectral_centroid_mean"] = float(np.mean(cent))
        features["spectral_centroid_std"] = float(np.std(cent))

        bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        features["spectral_bandwidth_mean"] = float(np.mean(bw))

        rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
        features["spectral_rolloff_mean"] = float(np.mean(rolloff))

        zcr = librosa.feature.zero_crossing_rate(y)
        features["zero_crossing_rate_mean"] = float(np.mean(zcr))

        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        for i in range(13):
            features[f"mfcc_{i}_mean"] = float(np.mean(mfccs[i]))

        f0, voiced_flag, voiced_probs = librosa.pyin(
            y, fmin=librosa.note_to_hz("C2"),
            fmax=librosa.note_to_hz("C7"), sr=sr
        )
        f0_valid = f0[~np.isnan(f0)]
        if len(f0_valid) > 0:
            features["f0_mean"] = float(np.mean(f0_valid))
            features["f0_std"] = float(np.std(f0_valid))
            features["voiced_ratio"] = float(np.sum(~np.isnan(f0)) / len(f0))
        else:
            features["f0_mean"] = 0.0
            features["f0_std"] = 0.0
            features["voiced_ratio"] = 0.0

        mel_full = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=sr // 2)
        total_energy = np.sum(mel_full)
        if total_energy > 0:
            high_freq_bins = mel_full[64:96, :]
            features["high_freq_energy_ratio"] = float(np.sum(high_freq_bins) / total_energy)
        else:
            features["high_freq_energy_ratio"] = 0.0

    except Exception as e:
        logger.warning(f"Feature extraction partial failure: {e}")

    return features


def full_audio_pipeline(file_path: str) -> Dict[str, Any]:
    # Training-aligned spectrogram (H, W) in [0, 1]
    spec_hw, metadata = load_and_preprocess(file_path)

    # Keep the previous shape expected by downstream code: (1, H, W)
    model_input = spec_hw[np.newaxis, :, :].astype(np.float32)

    # Keep existing feature keys used by `spectral_heuristic_score`.
    # (We compute them from the loaded audio to avoid re-reading the file elsewhere.)
    try:
        import librosa

        y, sr = librosa.load(file_path, sr=settings.AUDIO_SAMPLE_RATE, mono=True)
    except Exception:
        y = np.array([], dtype=np.float32)
        sr = settings.AUDIO_SAMPLE_RATE

    spectral_features = extract_spectral_features(y, sr)

    return {
        "metadata": metadata,
        "spectrogram": model_input,
        "features": spectral_features,
        "waveform": y,
        "sr": sr,
    }