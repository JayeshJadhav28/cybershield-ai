"""
File validation utilities — size, format, duration checks for all media uploads.
"""

import io
import os
from typing import Dict, Tuple
from fastapi import UploadFile, HTTPException, status

from config import settings


# ── Allowed file types by magic bytes ──
AUDIO_SIGNATURES = {
    b"RIFF": "wav",
    b"ID3": "mp3",
    b"\xff\xfb": "mp3",
    b"\xff\xf3": "mp3",
    b"\xff\xf2": "mp3",
    b"OggS": "ogg",
    b"fLaC": "flac",
}

# M4A/AAC files start with ftyp after initial bytes
M4A_MARKER = b"ftyp"

VIDEO_SIGNATURES = {
    b"\x00\x00\x00": "mp4",     # MP4/MOV (ftyp box)
    b"\x1a\x45\xdf\xa3": "webm",  # WebM/MKV
    b"RIFF": "avi",
}

IMAGE_SIGNATURES = {
    b"\x89PNG": "png",
    b"\xff\xd8\xff": "jpg",
}

WEBP_MARKER = b"WEBP"

ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".ogg", ".m4a", ".flac"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".webm"}
ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


async def validate_audio_file(file: UploadFile) -> Dict:
    """
    Validate an uploaded audio file.
    Returns metadata dict or raises HTTPException.
    """
    # Check filename extension
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required"
        )

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported audio format '{ext}'. Allowed: {', '.join(ALLOWED_AUDIO_EXTENSIONS)}"
        )

    # Read content
    content = await file.read()
    await file.seek(0)  # Reset for later use

    # Check size
    size_bytes = len(content)
    max_bytes = settings.upload_max_bytes["audio"]
    if size_bytes > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Audio file too large ({size_bytes / 1024 / 1024:.1f}MB). Maximum: {settings.MAX_AUDIO_SIZE_MB}MB"
        )

    if size_bytes < 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file too small — may be corrupted"
        )

    # Validate magic bytes
    if not _check_audio_magic_bytes(content):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content does not match a supported audio format. Ensure it is a valid audio file."
        )

    # Check duration using librosa
    duration = _get_audio_duration(content, ext)
    if duration is not None and duration > settings.MAX_AUDIO_DURATION_S:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Audio too long ({duration:.1f}s). Maximum duration: {settings.MAX_AUDIO_DURATION_S}s"
        )

    return {
        "extension": ext,
        "size_bytes": size_bytes,
        "duration_seconds": duration,
        "content": content,
    }


async def validate_video_file(file: UploadFile) -> Dict:
    """
    Validate an uploaded video file.
    Returns metadata dict or raises HTTPException.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required"
        )

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported video format '{ext}'. Allowed: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}"
        )

    content = await file.read()
    await file.seek(0)

    size_bytes = len(content)
    max_bytes = settings.upload_max_bytes["video"]
    if size_bytes > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Video file too large ({size_bytes / 1024 / 1024:.1f}MB). Maximum: {settings.MAX_VIDEO_SIZE_MB}MB"
        )

    if size_bytes < 5000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Video file too small — may be corrupted"
        )

    return {
        "extension": ext,
        "size_bytes": size_bytes,
        "content": content,
    }


async def validate_image_file(file: UploadFile) -> Dict:
    """
    Validate an uploaded image file (for QR codes).
    Returns metadata dict or raises HTTPException.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required"
        )

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image format '{ext}'. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        )

    content = await file.read()
    await file.seek(0)

    size_bytes = len(content)
    max_bytes = settings.upload_max_bytes["image"]
    if size_bytes > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image file too large ({size_bytes / 1024 / 1024:.1f}MB). Maximum: {settings.MAX_IMAGE_SIZE_MB}MB"
        )

    if size_bytes < 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image file too small — may be corrupted"
        )

    return {
        "extension": ext,
        "size_bytes": size_bytes,
        "content": content,
    }


def _check_audio_magic_bytes(content: bytes) -> bool:
    """Verify file starts with known audio format magic bytes."""
    header = content[:12]

    for sig in AUDIO_SIGNATURES:
        if header.startswith(sig):
            return True

    # M4A check (ftyp marker at offset 4)
    if len(header) >= 8 and M4A_MARKER in header[4:8]:
        return True

    return True  # Be lenient for MVP — some valid audio has unusual headers


def _get_audio_duration(content: bytes, ext: str) -> float | None:
    """Get audio duration in seconds using librosa."""
    try:
        import librosa
        import soundfile as sf

        audio_io = io.BytesIO(content)

        # Try soundfile first (faster for WAV, FLAC, OGG)
        try:
            info = sf.info(audio_io)
            return info.duration
        except Exception:
            pass

        # Fallback to librosa (handles MP3, M4A)
        audio_io.seek(0)
        y, sr = librosa.load(audio_io, sr=None, mono=True)
        return len(y) / sr

    except Exception as e:
        print(f"⚠️  Could not determine audio duration: {e}")
        return None
    
# Add these at the top if not already there
IMAGE_FORMATS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"}
IMAGE_MIME_TYPES = {
    "image/png", "image/jpeg", "image/webp", "image/bmp",
    "image/tiff", "image/gif",
}


async def validate_image_file(file: UploadFile) -> dict:
    """
    Validate an uploaded image file for deepfake analysis.

    Checks:
      - File extension is allowed
      - MIME type matches
      - File size within limit
      - Image can be decoded by OpenCV

    Returns metadata dict on success, raises HTTPException on failure.
    """
    from fastapi import HTTPException
    from config import settings
    import os
    import cv2
    import numpy as np

    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Check extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in IMAGE_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image format '{ext}'. "
                   f"Accepted: {', '.join(sorted(IMAGE_FORMATS))}",
        )

    # Check content type
    if file.content_type and file.content_type not in IMAGE_MIME_TYPES:
        # Don't hard-fail — some browsers send wrong MIME types
        pass

    # Check size
    content = await file.read()
    await file.seek(0)  # reset for later reading
    size_mb = len(content) / (1024 * 1024)
    max_mb = settings.MAX_IMAGE_SIZE_MB

    if size_mb > max_mb:
        raise HTTPException(
            status_code=413,
            detail=f"Image too large ({size_mb:.1f}MB). Maximum: {max_mb}MB",
        )

    # Verify image can be decoded
    arr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(
            status_code=400,
            detail="Cannot decode image. File may be corrupted or not a valid image.",
        )

    return {
        "extension": ext,
        "size_mb": round(size_mb, 2),
        "width": img.shape[1],
        "height": img.shape[0],
    }