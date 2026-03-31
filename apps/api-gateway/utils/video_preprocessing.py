"""
Video preprocessing — ZERO MediaPipe dependency.

Uses OpenCV-only face detection with 4-tier fallback strategy:
  1. OpenCV DNN SSD face detector (most accurate)
  2. Haar Cascade default (haarcascade_frontalface_default)
  3. Haar Cascade alt2 with relaxed params
  4. Center-crop fallback (guarantees model always gets input)

Training data (140k-real-and-fake-faces) used face crops.
Model expects: (128, 128, 3) float32 in [0, 1]  (RGB)
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

from config import settings

logger = logging.getLogger(__name__)


# =====================================================================
# Robust Face Detector — NO MEDIAPIPE
# =====================================================================
class RobustFaceDetector:
    """
    Multi-strategy OpenCV face detector.
    Guaranteed to work on any platform without extra dependencies.
    """

    _instance: Optional["RobustFaceDetector"] = None

    def __new__(cls) -> "RobustFaceDetector":
        if cls._instance is None:
            inst = super().__new__(cls)
            inst._initialized = False
            cls._instance = inst
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        # ── Strategy 1: OpenCV DNN face detector ──
        self._dnn_net = self._load_dnn_detector()

        # ── Strategy 2 & 3: Haar cascades (bundled with OpenCV) ──
        haar_dir = cv2.data.haarcascades
        self._haar_default = cv2.CascadeClassifier(
            os.path.join(haar_dir, "haarcascade_frontalface_default.xml")
        )
        self._haar_alt2 = cv2.CascadeClassifier(
            os.path.join(haar_dir, "haarcascade_frontalface_alt2.xml")
        )
        self._haar_profile = cv2.CascadeClassifier(
            os.path.join(haar_dir, "haarcascade_profileface.xml")
        )

        logger.info(
            "FaceDetector ready: DNN=%s, Haar=loaded",
            "loaded" if self._dnn_net is not None else "unavailable",
        )

    # ------------------------------------------------------------------
    # DNN loader
    # ------------------------------------------------------------------
    @staticmethod
    def _load_dnn_detector():
        """
        Try to load OpenCV's built-in DNN face detector.
        Works with OpenCV 4.x+ if the model files are present.
        """
        # Common locations for the DNN model files
        search_dirs = [
            Path(settings.MODEL_DIR),
            Path(__file__).parent.parent / "data",
            Path.home() / ".cybershield" / "models",
            Path("/usr/share/opencv4/"),
        ]

        prototxt_name = "deploy.prototxt"
        model_name = "res10_300x300_ssd_iter_140000.caffemodel"

        for d in search_dirs:
            proto = d / prototxt_name
            model = d / model_name
            if proto.is_file() and model.is_file():
                try:
                    net = cv2.dnn.readNetFromCaffe(str(proto), str(model))
                    logger.info("DNN face detector loaded from %s", d)
                    return net
                except Exception as e:
                    logger.warning("DNN load failed from %s: %s", d, e)

        # Try OpenCV's FaceDetectorYN (available in OpenCV 4.5.4+)
        try:
            onnx_paths = [
                Path(settings.MODEL_DIR) / "face_detection_yunet_2023mar.onnx",
                Path(settings.MODEL_DIR) / "yunet.onnx",
            ]
            for p in onnx_paths:
                if p.is_file():
                    detector = cv2.FaceDetectorYN.create(str(p), "", (300, 300))
                    logger.info("YuNet face detector loaded from %s", p)
                    return ("yunet", detector)
        except AttributeError:
            pass  # OpenCV version too old

        logger.info("DNN face detector not available — Haar cascade only")
        return None

    # ------------------------------------------------------------------
    # Detection strategies
    # ------------------------------------------------------------------
    def detect(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces using all strategies in order of accuracy.

        Returns list of (x, y, w, h) bounding boxes.
        """
        # ── Strategy 1: DNN ──
        if self._dnn_net is not None:
            faces = self._detect_dnn(frame)
            if faces:
                return faces

        # ── Strategy 2: Haar default, strict ──
        gray = self._preprocess_gray(frame)
        faces = self._detect_haar(
            self._haar_default, gray,
            scale_factor=1.1, min_neighbors=5, min_size=(30, 30)
        )
        if faces:
            return faces

        # ── Strategy 3: Haar alt2, relaxed ──
        faces = self._detect_haar(
            self._haar_alt2, gray,
            scale_factor=1.05, min_neighbors=3, min_size=(20, 20)
        )
        if faces:
            return faces

        # ── Strategy 4: Haar default, very relaxed ──
        faces = self._detect_haar(
            self._haar_default, gray,
            scale_factor=1.03, min_neighbors=2, min_size=(15, 15)
        )
        if faces:
            return faces

        # ── Strategy 5: Haar profile face ──
        faces = self._detect_haar(
            self._haar_profile, gray,
            scale_factor=1.05, min_neighbors=2, min_size=(20, 20)
        )
        if faces:
            return faces

        # ── Strategy 6: histogram equalized retry ──
        eq_gray = cv2.equalizeHist(gray)
        faces = self._detect_haar(
            self._haar_default, eq_gray,
            scale_factor=1.05, min_neighbors=2, min_size=(20, 20)
        )
        if faces:
            return faces

        return []  # all strategies exhausted

    def _preprocess_gray(self, frame: np.ndarray) -> np.ndarray:
        """Convert to grayscale with optional CLAHE for better detection."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return gray

    def _detect_haar(
        self,
        cascade: cv2.CascadeClassifier,
        gray: np.ndarray,
        scale_factor: float = 1.1,
        min_neighbors: int = 5,
        min_size: Tuple[int, int] = (30, 30),
    ) -> List[Tuple[int, int, int, int]]:
        """Run Haar cascade detection."""
        try:
            detections = cascade.detectMultiScale(
                gray,
                scaleFactor=scale_factor,
                minNeighbors=min_neighbors,
                minSize=min_size,
                flags=cv2.CASCADE_SCALE_IMAGE,
            )
            if detections is not None and len(detections) > 0:
                return [tuple(d) for d in detections]
        except Exception as e:
            logger.debug("Haar detection failed: %s", e)
        return []

    def _detect_dnn(
        self, frame: np.ndarray, confidence_threshold: float = 0.5
    ) -> List[Tuple[int, int, int, int]]:
        """Run OpenCV DNN SSD face detection."""
        try:
            if isinstance(self._dnn_net, tuple) and self._dnn_net[0] == "yunet":
                return self._detect_yunet(frame)

            h, w = frame.shape[:2]
            blob = cv2.dnn.blobFromImage(
                cv2.resize(frame, (300, 300)),
                1.0, (300, 300),
                (104.0, 177.0, 123.0),
            )
            self._dnn_net.setInput(blob)
            detections = self._dnn_net.forward()

            faces = []
            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                if confidence > confidence_threshold:
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    x1, y1, x2, y2 = box.astype(int)
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(w, x2), min(h, y2)
                    faces.append((x1, y1, x2 - x1, y2 - y1))
            return faces
        except Exception as e:
            logger.debug("DNN detection failed: %s", e)
            return []

    def _detect_yunet(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Run YuNet detection."""
        try:
            _, detector = self._dnn_net
            h, w = frame.shape[:2]
            detector.setInputSize((w, h))
            _, faces = detector.detect(frame)
            if faces is None:
                return []
            result = []
            for face in faces:
                x, y, fw, fh = int(face[0]), int(face[1]), int(face[2]), int(face[3])
                result.append((x, y, fw, fh))
            return result
        except Exception as e:
            logger.debug("YuNet detection failed: %s", e)
            return []


# =====================================================================
# Module-level singleton
# =====================================================================
_detector = None


def _get_detector() -> RobustFaceDetector:
    global _detector
    if _detector is None:
        _detector = RobustFaceDetector()
    return _detector


# =====================================================================
# Public API
# =====================================================================
def extract_frames(
    video_path: str,
    fps: int | None = None,
    max_frames: int | None = None,
) -> Tuple[List[np.ndarray], Dict]:
    """
    Extract frames from a video file at the target FPS.

    Returns (frames_list, metadata_dict).
    """
    fps = fps or settings.VIDEO_FRAME_RATE
    max_frames = max_frames or settings.VIDEO_MAX_FRAMES

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    video_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_video_frames / video_fps if video_fps else 0

    sample_interval = max(1, int(round(video_fps / fps)))

    frames: List[np.ndarray] = []
    idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if idx % sample_interval == 0:
            frames.append(frame)
            if len(frames) >= max_frames:
                break
        idx += 1
    cap.release()

    metadata = {
        "duration_seconds": round(duration, 2),
        "resolution": f"{width}x{height}",
        "fps": round(video_fps, 1),
        "total_video_frames": total_video_frames,
        "frames_extracted": len(frames),
    }
    return frames, metadata


def detect_and_crop_faces(
    frames: List[np.ndarray],
    face_size: Tuple[int, int] | None = None,
) -> Tuple[List[np.ndarray], Dict]:
    """
    Detect faces in each frame, crop, resize, normalize.

    Uses multi-strategy detection with center-crop fallback.
    If NO face is found in a frame, a center crop is used instead
    so the model always receives input.

    Returns
    -------
    face_crops : list of (H, W, 3) float32 in [0, 1]  (RGB)
    info       : dict
    """
    face_size = face_size or tuple(settings.VIDEO_FACE_SIZE)
    detector = _get_detector()

    face_crops: List[np.ndarray] = []
    detection_method: List[str] = []
    frames_with_real_face = 0
    frames_with_center_crop = 0

    for frame in frames:
        detections = detector.detect(frame)

        if detections:
            # Take largest face by area
            x, y, w, h = max(detections, key=lambda d: d[2] * d[3])
            frames_with_real_face += 1
            method = "detected"

            # Add 25% margin around the face
            margin_x = int(0.25 * w)
            margin_y = int(0.25 * h)
            fh, fw = frame.shape[:2]
            x1 = max(0, x - margin_x)
            y1 = max(0, y - margin_y)
            x2 = min(fw, x + w + margin_x)
            y2 = min(fh, y + h + margin_y)
            crop = frame[y1:y2, x1:x2]
        else:
            # ── CENTER CROP FALLBACK ──
            # Take the center 60% of the frame (likely contains the face)
            fh, fw = frame.shape[:2]
            margin_x = int(fw * 0.2)
            margin_y = int(fh * 0.15)
            crop = frame[margin_y : fh - margin_y, margin_x : fw - margin_x]
            frames_with_center_crop += 1
            method = "center_crop"

        # Ensure crop is valid
        if crop.size == 0 or crop.shape[0] < 10 or crop.shape[1] < 10:
            crop = frame  # absolute fallback: use full frame
            method = "full_frame"

        # Convert BGR → RGB, resize, normalize
        crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        crop_resized = cv2.resize(
            crop_rgb, face_size, interpolation=cv2.INTER_LINEAR
        )
        crop_norm = crop_resized.astype(np.float32) / 255.0
        face_crops.append(crop_norm)
        detection_method.append(method)

    info = {
        "faces_detected": frames_with_real_face,
        "center_crop_fallback": frames_with_center_crop,
        "total_frames_processed": len(frames),
        "detection_methods": detection_method,
        "face_detection_rate": (
            frames_with_real_face / max(len(frames), 1)
        ),
    }

    logger.info(
        "Face detection: %d/%d frames had faces, %d used center crop",
        frames_with_real_face, len(frames), frames_with_center_crop,
    )

    return face_crops, info


def compute_frame_heuristics(
    frames: List[np.ndarray],
    face_crops: List[np.ndarray],
    face_info: Dict,
) -> Dict:
    """
    Compute heuristic features for rule-based scoring.
    """
    features: Dict = {}

    total = face_info.get("total_frames_processed", 1)
    detected = face_info.get("faces_detected", 0)
    features["face_detection_rate"] = detected / max(total, 1)

    # Blur analysis on face crops
    if face_crops:
        blurs = []
        for fc in face_crops:
            gray = cv2.cvtColor(
                (fc * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY
            )
            blurs.append(float(cv2.Laplacian(gray, cv2.CV_64F).var()))
        features["mean_face_blur"] = float(np.mean(blurs))
        features["blur_variance"] = float(np.var(blurs))
        features["min_blur"] = float(np.min(blurs))
        features["max_blur"] = float(np.max(blurs))
    else:
        features["mean_face_blur"] = 0.0
        features["blur_variance"] = 0.0

    # Brightness consistency
    if len(frames) >= 2:
        brightness = [
            float(np.mean(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)))
            for f in frames
        ]
        features["brightness_variance"] = float(np.var(brightness))
        features["brightness_mean"] = float(np.mean(brightness))
    else:
        features["brightness_variance"] = 0.0

    # Color consistency across face crops
    if len(face_crops) >= 2:
        mean_colors = [np.mean(fc, axis=(0, 1)) for fc in face_crops]
        color_var = np.var(mean_colors, axis=0)
        features["color_variance"] = float(np.mean(color_var))
    else:
        features["color_variance"] = 0.0

    # Edge density in face crops (deepfakes often have smoother textures)
    if face_crops:
        edge_densities = []
        for fc in face_crops:
            gray = cv2.cvtColor(
                (fc * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY
            )
            edges = cv2.Canny(gray, 50, 150)
            edge_densities.append(float(np.mean(edges > 0)))
        features["mean_edge_density"] = float(np.mean(edge_densities))
        features["edge_density_variance"] = float(np.var(edge_densities))
    else:
        features["mean_edge_density"] = 0.0
        features["edge_density_variance"] = 0.0

    return features