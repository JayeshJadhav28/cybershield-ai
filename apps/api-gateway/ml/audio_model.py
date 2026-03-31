"""
Audio Deepfake CNN — Architecture Definitions

Trained on:  birdy654/deep-voice-deepfake-voice-recognition  (Kaggle)
Input:       Mel-spectrogram  (128 × 128 × 1)
Output:      sigmoid  →  P(deepfake)  ∈ [0, 1]
"""
from __future__ import annotations

import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

# ── PyTorch architecture ─────────────────────────────────────────
TORCH_AVAILABLE = False
try:
    import torch
    import torch.nn as nn

    class AudioDeepfakeCNN(nn.Module):
        def __init__(self):
            super().__init__()
            self.features = nn.Sequential(
                nn.Conv2d(1, 32, kernel_size=3),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(2),
                nn.Conv2d(32, 64, kernel_size=3),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(2),
                nn.Conv2d(64, 128, kernel_size=3),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(2),
            )
            self.classifier = nn.Sequential(
                nn.Flatten(),
                nn.Linear(128 * 14 * 14, 128),
                nn.ReLU(inplace=True),
                nn.Dropout(0.5),
                nn.Linear(128, 1),
                nn.Sigmoid(),
            )

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            return self.classifier(self.features(x))

    TORCH_AVAILABLE = True
    logger.info("PyTorch available for audio model")

except Exception as e:
    logger.info("PyTorch not available (%s: %s) — using Keras only", type(e).__name__, e)
    AudioDeepfakeCNN = None  # type: ignore

    class _DummyModule:
        pass

    class _DummyNN:
        Module = _DummyModule

    nn = _DummyNN()  # type: ignore


# ── Keras builder (reference only) ────────────────────────────────
try:
    import tensorflow as tf

    def build_audio_keras_model() -> "tf.keras.Model":
        model = tf.keras.Sequential([
            tf.keras.layers.Conv2D(32, (3, 3), activation="relu",
                                   input_shape=(128, 128, 1)),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Conv2D(64, (3, 3), activation="relu"),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Conv2D(128, (3, 3), activation="relu"),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(128, activation="relu"),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(1, activation="sigmoid"),
        ])
        model.compile(optimizer="adam", loss="binary_crossentropy",
                      metrics=["accuracy"])
        return model

    KERAS_AVAILABLE = True
except ImportError:
    KERAS_AVAILABLE = False
    build_audio_keras_model = None  # type: ignore


# ── Unified predict helper ────────────────────────────────────────
def predict_audio(model, spectrogram: np.ndarray) -> float:
    """
    Run inference on a single mel-spectrogram.

    Parameters
    ----------
    model       : loaded Keras model OR PyTorch AudioDeepfakeCNN
    spectrogram : np.ndarray of shape (128, 128)

    Returns
    -------
    float — P(deepfake) in [0, 1]
    """
    try:
        # ── Keras / TensorFlow ──
        if hasattr(model, "predict"):
            inp = spectrogram.astype(np.float32)
            if inp.ndim == 2:
                inp = inp[np.newaxis, ..., np.newaxis]  # (1, 128, 128, 1)
            elif inp.ndim == 3:
                inp = inp[np.newaxis, ...]
            pred = model.predict(inp, verbose=0)
            return float(np.squeeze(pred))

        # ── PyTorch ──
        if TORCH_AVAILABLE and isinstance(model, nn.Module):
            model.eval()
            inp = spectrogram.astype(np.float32)
            if inp.ndim == 2:
                inp = inp[np.newaxis, np.newaxis, ...]  # (1, 1, 128, 128)
            elif inp.ndim == 3:
                inp = inp[np.newaxis, ...]
            with torch.no_grad():
                tensor = torch.from_numpy(inp)
                pred = model(tensor)
            return float(pred.squeeze().item())

    except Exception as e:
        logger.error("Audio model inference failed: %s", e)

    return 0.5