"""
Lazy-singleton model loader with post-load validation.
"""
from __future__ import annotations

import logging
import os
import threading
from pathlib import Path
from typing import Any, Optional

import numpy as np

from config import settings

logger = logging.getLogger(__name__)

# Suppress TF noise at import time
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")


class ModelLoader:
    _instance: Optional["ModelLoader"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "ModelLoader":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    inst = super().__new__(cls)
                    inst._cache: dict[str, Any] = {}
                    cls._instance = inst
        return cls._instance

    # ------------------------------------------------------------------
    @staticmethod
    def _try_keras(path: Path):
        import tensorflow as tf
        tf.get_logger().setLevel("ERROR")
        model = tf.keras.models.load_model(str(path), compile=False)
        logger.info(
            "Loaded Keras model: %s  input=%s  output=%s",
            path.name, model.input_shape, model.output_shape,
        )
        return model

    @staticmethod
    def _try_torch_full(path: Path):
        try:
            import torch
        except Exception as e:
            logger.debug("PyTorch unavailable: %s", e)
            return None
        model = torch.load(str(path), map_location="cpu", weights_only=False)
        if hasattr(model, "eval"):
            model.eval()
        logger.info("Loaded PyTorch model (full) from %s", path.name)
        return model

    @staticmethod
    def _try_torch_statedict(path: Path, arch_cls):
        if arch_cls is None:
            return None
        try:
            import torch
        except Exception as e:
            logger.debug("PyTorch unavailable: %s", e)
            return None
        model = arch_cls()
        state = torch.load(str(path), map_location="cpu", weights_only=True)
        model.load_state_dict(state)
        model.eval()
        logger.info("Loaded PyTorch state-dict from %s", path.name)
        return model

    # ------------------------------------------------------------------
    @staticmethod
    def _validate_video_model(model) -> bool:
        try:
            if hasattr(model, "predict"):
                dummy = np.random.rand(1, 128, 128, 3).astype(np.float32)
                out = model.predict(dummy, verbose=0)
                val = float(np.squeeze(out))
                logger.info("Video model validation OK: dummy=%.4f", val)
                return 0.0 <= val <= 1.0
            else:
                import torch
                dummy = torch.randn(1, 3, 128, 128)
                with torch.no_grad():
                    out = model(dummy)
                val = float(out.squeeze().item())
                logger.info("Video model validation OK: dummy=%.4f", val)
                return 0.0 <= val <= 1.0
        except Exception as e:
            logger.error("Video model validation FAILED: %s", e)
            return False

    @staticmethod
    def _validate_audio_model(model) -> bool:
        try:
            if hasattr(model, "predict"):
                dummy = np.random.rand(1, 128, 128, 1).astype(np.float32)
                out = model.predict(dummy, verbose=0)
                val = float(np.squeeze(out))
                logger.info("Audio model validation OK: dummy=%.4f", val)
                return 0.0 <= val <= 1.0
            else:
                import torch
                dummy = torch.randn(1, 1, 128, 128)
                with torch.no_grad():
                    out = model(dummy)
                val = float(out.squeeze().item())
                logger.info("Audio model validation OK: dummy=%.4f", val)
                return 0.0 <= val <= 1.0
        except Exception as e:
            logger.error("Audio model validation FAILED: %s", e)
            return False

    # ------------------------------------------------------------------
    def _load(self, key: str, h5_path: Path, pt_path: Path,
              torch_arch_cls=None, validator=None):
        if key in self._cache:
            return self._cache[key]

        model = None

        # 1) Keras .h5  (preferred — always works on this system)
        if h5_path.is_file():
            try:
                model = self._try_keras(h5_path)
            except Exception as e:
                logger.warning("Keras load failed for %s: %s", h5_path.name, e)

        # 2) PyTorch .pt  (skip if torch is broken)
        if model is None and pt_path.is_file():
            try:
                model = self._try_torch_full(pt_path)
            except Exception:
                if torch_arch_cls is not None:
                    try:
                        model = self._try_torch_statedict(pt_path, torch_arch_cls)
                    except Exception as e2:
                        logger.warning("PyTorch load failed: %s", e2)

        # Validate
        if model is not None and validator is not None:
            if not validator(model):
                logger.error("Model [%s] failed validation — discarding", key)
                model = None

        if model is None:
            logger.warning(
                "No model for [%s]. Checked: %s, %s",
                key, h5_path, pt_path,
            )

        self._cache[key] = model
        return model

    # ------------------------------------------------------------------
    def get_audio_model(self):
        from ml.audio_model import AudioDeepfakeCNN
        return self._load(
            "audio",
            settings.audio_model_path("h5"),
            settings.audio_model_path("pt"),
            torch_arch_cls=AudioDeepfakeCNN,
            validator=self._validate_audio_model,
        )

    def get_video_model(self):
        from ml.video_model import FaceDeepfakeCNN
        return self._load(
            "video",
            settings.video_model_path("h5"),
            settings.video_model_path("pt"),
            torch_arch_cls=FaceDeepfakeCNN,
            validator=self._validate_video_model,
        )

    def get_phishing_model(self):
        if "phishing" in self._cache:
            return self._cache["phishing"]
        vec_path = settings.phishing_vectorizer_path()
        clf_path = settings.phishing_classifier_path()
        try:
            import joblib
            vectorizer = joblib.load(str(vec_path))
            classifier = joblib.load(str(clf_path))
            logger.info("Loaded phishing vectorizer + classifier")
            self._cache["phishing"] = (vectorizer, classifier)
            return (vectorizer, classifier)
        except Exception as e:
            logger.warning("Phishing model load failed: %s", e)
            self._cache["phishing"] = (None, None)
            return (None, None)

    def is_loaded(self, key: str) -> bool:
        val = self._cache.get(key)
        if val is None:
            return False
        if isinstance(val, tuple):
            return val[0] is not None
        return True