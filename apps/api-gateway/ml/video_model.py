"""
Video / Face Deepfake CNN — Architecture + Inference

Trained on:  xhlulu/140k-real-and-fake-faces  (Kaggle)
Input:       RGB face crop  (128 × 128 × 3)  float32 in [0, 1]
Output:      sigmoid  →  P(fake)  ∈ [0, 1]
"""
from __future__ import annotations

import logging
from typing import List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# ── PyTorch architecture ─────────────────────────────────────────
# Catch ALL exceptions — on Windows, torch can fail with OSError/DLL errors
TORCH_AVAILABLE = False
try:
    import torch
    import torch.nn as nn

    class FaceDeepfakeCNN(nn.Module):
        def __init__(self):
            super().__init__()
            self.features = nn.Sequential(
                nn.Conv2d(3, 32, 3, padding=1), nn.ReLU(True), nn.MaxPool2d(2),
                nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(True), nn.MaxPool2d(2),
                nn.Conv2d(64, 128, 3, padding=1), nn.ReLU(True), nn.MaxPool2d(2),
                nn.Conv2d(128, 256, 3, padding=1), nn.ReLU(True), nn.MaxPool2d(2),
                nn.AdaptiveAvgPool2d((4, 4)),
            )
            self.classifier = nn.Sequential(
                nn.Flatten(),
                nn.Linear(256 * 4 * 4, 512),
                nn.ReLU(True),
                nn.Dropout(0.5),
                nn.Linear(512, 1),
                nn.Sigmoid(),
            )

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            return self.classifier(self.features(x))

    TORCH_AVAILABLE = True
    logger.info("PyTorch available for video model")

except Exception as e:
    # Catches ImportError, OSError (DLL failures on Windows), etc.
    logger.info("PyTorch not available (%s: %s) — using Keras only", type(e).__name__, e)
    FaceDeepfakeCNN = None  # type: ignore

    # Dummy nn module so isinstance checks don't crash
    class _DummyModule:
        pass

    class _DummyNN:
        Module = _DummyModule

    nn = _DummyNN()  # type: ignore


# ── Detect model's expected input size ────────────────────────────
def get_model_input_shape(model) -> Tuple[int, int]:
    """Auto-detect the spatial input size the model expects. Returns (height, width)."""
    try:
        if hasattr(model, "input_shape"):
            shape = model.input_shape
            if isinstance(shape, list):
                shape = shape[0]
            if shape is not None and len(shape) == 4:
                h, w = shape[1], shape[2]
                if h is not None and w is not None:
                    return (int(h), int(w))
    except Exception:
        pass

    return (128, 128)


# ── Single-face prediction ────────────────────────────────────────
def predict_face(
    model,
    face_img: np.ndarray,
    target_size: Optional[Tuple[int, int]] = None,
) -> float:
    """
    Classify a single face crop.

    Parameters
    ----------
    model       : loaded Keras model or PyTorch module
    face_img    : (H, W, 3) float32 in [0, 1]  (RGB)
    target_size : (h, w) to resize before inference

    Returns
    -------
    P(fake) ∈ [0, 1]
    """
    try:
        img = face_img.astype(np.float32)

        if target_size and (img.shape[0] != target_size[0]
                            or img.shape[1] != target_size[1]):
            import cv2
            img = cv2.resize(img, (target_size[1], target_size[0]),
                             interpolation=cv2.INTER_LINEAR)

        # ── Keras / TensorFlow ──
        if hasattr(model, "predict"):
            if img.ndim == 3:
                inp = img[np.newaxis, ...]  # (1, H, W, 3)
            else:
                inp = img
            pred = model.predict(inp, verbose=0)
            return float(np.squeeze(pred))

        # ── PyTorch ──
        if TORCH_AVAILABLE and isinstance(model, nn.Module):
            model.eval()
            if img.ndim == 3:
                inp = np.transpose(img, (2, 0, 1))  # HWC → CHW
                inp = inp[np.newaxis, ...]           # (1, 3, H, W)
            else:
                inp = img
            with torch.no_grad():
                tensor = torch.from_numpy(inp).float()
                pred = model(tensor)
            return float(pred.squeeze().item())

    except Exception as e:
        logger.error("Face inference failed: %s", e)

    return 0.5


# ── Batch prediction ──────────────────────────────────────────────
def predict_faces_batch(
    model,
    faces: List[np.ndarray],
    target_size: Optional[Tuple[int, int]] = None,
) -> List[float]:
    """Run prediction on a list of face crops. Returns list of P(fake)."""
    if not faces:
        return []

    if target_size is None:
        target_size = get_model_input_shape(model)

    # ── Batch inference for Keras (faster) ──
    if hasattr(model, "predict") and len(faces) > 1:
        try:
            import cv2
            batch = []
            for f in faces:
                img = f.astype(np.float32)
                if img.shape[0] != target_size[0] or img.shape[1] != target_size[1]:
                    img = cv2.resize(img, (target_size[1], target_size[0]),
                                     interpolation=cv2.INTER_LINEAR)
                batch.append(img)
            batch_arr = np.array(batch)  # (N, H, W, 3)
            preds = model.predict(batch_arr, verbose=0,
                                  batch_size=min(len(batch), 32))
            return [float(np.squeeze(p)) for p in preds]
        except Exception as e:
            logger.warning("Batch inference failed, per-face fallback: %s", e)

    # ── Per-face fallback ──
    return [predict_face(model, f, target_size) for f in faces]