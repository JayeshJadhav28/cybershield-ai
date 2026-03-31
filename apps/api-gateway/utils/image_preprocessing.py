"""
Image preprocessing for deepfake face detection.

The video_deepfake_detector model was trained on 140k-real-and-fake-faces
dataset which contains individual face images.

Pipeline:
  1. Load image
  2. Detect face(s) using OpenCV
  3. Crop + resize to model input size (128×128)
  4. Normalize to [0, 1] float32 RGB
"""
from __future__ import annotations

import logging
import os
from typing import Dict, List, Tuple

import cv2
import numpy as np

from config import settings

logger = logging.getLogger(__name__)

# Haar cascade (bundled with OpenCV)
_CASCADE_PATH = os.path.join(
    cv2.data.haarcascades, "haarcascade_frontalface_default.xml"
)
_CASCADE_ALT_PATH = os.path.join(
    cv2.data.haarcascades, "haarcascade_frontalface_alt2.xml"
)
_face_cascade = cv2.CascadeClassifier(_CASCADE_PATH)
_face_cascade_alt = cv2.CascadeClassifier(_CASCADE_ALT_PATH)


def load_image(file_path: str) -> np.ndarray:
    """Load image from disk as BGR numpy array."""
    img = cv2.imread(file_path)
    if img is None:
        raise ValueError(f"Cannot read image: {file_path}")
    return img


def detect_faces(
    img: np.ndarray,
) -> List[Tuple[int, int, int, int]]:
    """
    Detect faces in an image using multi-strategy Haar cascades.

    Returns list of (x, y, w, h) bounding boxes.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Strategy 1: default cascade, strict
    faces = _face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )
    if faces is not None and len(faces) > 0:
        return [tuple(f) for f in faces]

    # Strategy 2: alt2 cascade, relaxed
    faces = _face_cascade_alt.detectMultiScale(
        gray, scaleFactor=1.05, minNeighbors=3, minSize=(20, 20)
    )
    if faces is not None and len(faces) > 0:
        return [tuple(f) for f in faces]

    # Strategy 3: histogram equalized retry
    eq_gray = cv2.equalizeHist(gray)
    faces = _face_cascade.detectMultiScale(
        eq_gray, scaleFactor=1.05, minNeighbors=2, minSize=(20, 20)
    )
    if faces is not None and len(faces) > 0:
        return [tuple(f) for f in faces]

    return []


def crop_face(
    img: np.ndarray,
    bbox: Tuple[int, int, int, int],
    margin: float = 0.25,
    target_size: Tuple[int, int] = (128, 128),
) -> np.ndarray:
    """
    Crop a face region with margin, resize, convert to RGB float32 [0,1].
    """
    x, y, w, h = bbox
    fh, fw = img.shape[:2]

    margin_x = int(margin * w)
    margin_y = int(margin * h)

    x1 = max(0, x - margin_x)
    y1 = max(0, y - margin_y)
    x2 = min(fw, x + w + margin_x)
    y2 = min(fh, y + h + margin_y)

    crop = img[y1:y2, x1:x2]
    if crop.size == 0:
        crop = img

    crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
    crop_resized = cv2.resize(crop_rgb, target_size, interpolation=cv2.INTER_LINEAR)
    return crop_resized.astype(np.float32) / 255.0


def center_crop(
    img: np.ndarray,
    target_size: Tuple[int, int] = (128, 128),
) -> np.ndarray:
    """
    Center-crop 60% of the image as fallback when no face is detected.
    """
    fh, fw = img.shape[:2]
    margin_x = int(fw * 0.2)
    margin_y = int(fh * 0.15)

    crop = img[margin_y : fh - margin_y, margin_x : fw - margin_x]
    if crop.size == 0:
        crop = img

    crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
    crop_resized = cv2.resize(crop_rgb, target_size, interpolation=cv2.INTER_LINEAR)
    return crop_resized.astype(np.float32) / 255.0


def preprocess_image(
    file_path: str,
    target_size: Tuple[int, int] | None = None,
) -> Tuple[List[np.ndarray], Dict]:
    """
    Full preprocessing pipeline for a single image.

    Returns
    -------
    face_crops : list of (H, W, 3) float32 [0,1] RGB arrays
    metadata   : dict with image_width, image_height, faces_found, method, etc.
    """
    target_size = target_size or tuple(settings.VIDEO_FACE_SIZE)

    img = load_image(file_path)
    h, w = img.shape[:2]

    metadata: Dict = {
        "image_width": w,
        "image_height": h,
        "file_path": os.path.basename(file_path),
    }

    # Detect faces
    detections = detect_faces(img)
    face_crops: List[np.ndarray] = []

    if detections:
        metadata["faces_found"] = len(detections)
        metadata["method"] = "face_detection"
        metadata["face_locations"] = [
            {"x": int(x), "y": int(y), "w": int(bw), "h": int(bh)}
            for x, y, bw, bh in detections
        ]

        for bbox in detections:
            crop = crop_face(img, bbox, target_size=target_size)
            face_crops.append(crop)
    else:
        # Fallback: center crop
        metadata["faces_found"] = 0
        metadata["method"] = "center_crop_fallback"
        crop = center_crop(img, target_size=target_size)
        face_crops.append(crop)

    logger.info(
        "Image preprocessed: %dx%d, %d faces found, method=%s",
        w, h, metadata.get("faces_found", 0), metadata["method"],
    )

    return face_crops, metadata


def compute_image_heuristics(
    file_path: str,
    face_crops: List[np.ndarray],
    metadata: Dict,
) -> Dict:
    """
    Compute rule-based heuristic features from the image.
    """
    features: Dict = {}
    img = load_image(file_path)

    # Face detection success
    features["faces_found"] = metadata.get("faces_found", 0)
    features["detection_method"] = metadata.get("method", "unknown")

    # Blur analysis on face crops
    if face_crops:
        blurs = []
        for fc in face_crops:
            gray = cv2.cvtColor(
                (fc * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY
            )
            blurs.append(float(cv2.Laplacian(gray, cv2.CV_64F).var()))
        features["mean_face_blur"] = float(np.mean(blurs))
        features["max_face_blur"] = float(np.max(blurs))
    else:
        features["mean_face_blur"] = 0.0

    # Edge density (deepfakes tend to have smoother skin)
    if face_crops:
        edge_densities = []
        for fc in face_crops:
            gray = cv2.cvtColor(
                (fc * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY
            )
            edges = cv2.Canny(gray, 50, 150)
            edge_densities.append(float(np.mean(edges > 0)))
        features["mean_edge_density"] = float(np.mean(edge_densities))
    else:
        features["mean_edge_density"] = 0.0

    # JPEG compression artifact detection
    gray_full = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dct_vals = cv2.dct(np.float32(gray_full[:8, :8]))
    features["dct_energy"] = float(np.sum(np.abs(dct_vals)))

    # Noise level estimation
    noise = cv2.Laplacian(gray_full, cv2.CV_64F)
    features["noise_level"] = float(np.std(noise))

    # Color distribution (fake faces sometimes have unnatural color ranges)
    if face_crops:
        fc_uint8 = (face_crops[0] * 255).astype(np.uint8)
        hsv = cv2.cvtColor(fc_uint8, cv2.COLOR_RGB2HSV)
        features["saturation_mean"] = float(np.mean(hsv[:, :, 1]))
        features["saturation_std"] = float(np.std(hsv[:, :, 1]))
        features["value_mean"] = float(np.mean(hsv[:, :, 2]))
    else:
        features["saturation_mean"] = 0.0
        features["saturation_std"] = 0.0

    # Image resolution check (very low-res = suspicious)
    features["resolution"] = metadata.get("image_width", 0) * metadata.get("image_height", 0)
    features["is_low_resolution"] = features["resolution"] < 100 * 100

    return features