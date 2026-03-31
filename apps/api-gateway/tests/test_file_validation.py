"""
Tests for file validation utilities.
"""

import io
import struct
import pytest
import numpy as np
from unittest.mock import AsyncMock, MagicMock

from fastapi import UploadFile, HTTPException

from utils.file_validation import (
    validate_audio_file,
    validate_image_file,
    ALLOWED_AUDIO_EXTENSIONS,
    ALLOWED_IMAGE_EXTENSIONS,
)


def _make_upload_file(content: bytes, filename: str) -> UploadFile:
    """Create a mock UploadFile for testing."""
    file_like = io.BytesIO(content)
    return UploadFile(file=file_like, filename=filename)


def _generate_test_wav(duration_s=1.0, sample_rate=16000) -> bytes:
    """Generate minimal WAV file."""
    n_samples = int(duration_s * sample_rate)
    audio = (np.sin(np.linspace(0, 100, n_samples)) * 10000).astype(np.int16)

    buf = io.BytesIO()
    data_size = n_samples * 2

    buf.write(b"RIFF")
    buf.write(struct.pack("<I", 36 + data_size))
    buf.write(b"WAVE")
    buf.write(b"fmt ")
    buf.write(struct.pack("<I", 16))
    buf.write(struct.pack("<H", 1))
    buf.write(struct.pack("<H", 1))
    buf.write(struct.pack("<I", sample_rate))
    buf.write(struct.pack("<I", sample_rate * 2))
    buf.write(struct.pack("<H", 2))
    buf.write(struct.pack("<H", 16))
    buf.write(b"data")
    buf.write(struct.pack("<I", data_size))
    buf.write(audio.tobytes())

    return buf.getvalue()


class TestAudioFileValidation:

    @pytest.mark.asyncio
    async def test_valid_wav_file(self):
        wav = _generate_test_wav(duration_s=2.0)
        file = _make_upload_file(wav, "test.wav")
        result = await validate_audio_file(file)

        assert result["extension"] == ".wav"
        assert result["size_bytes"] > 0
        assert result["content"] == wav

    @pytest.mark.asyncio
    async def test_unsupported_extension(self):
        content = b"fake content" * 100
        file = _make_upload_file(content, "test.xyz")

        with pytest.raises(HTTPException) as exc_info:
            await validate_audio_file(file)
        assert exc_info.value.status_code == 400
        assert "Unsupported" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_file_too_small(self):
        file = _make_upload_file(b"tiny", "test.wav")

        with pytest.raises(HTTPException) as exc_info:
            await validate_audio_file(file)
        assert exc_info.value.status_code == 400
        assert "too small" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_no_filename(self):
        file = _make_upload_file(b"content", "")

        # Empty filename should fail
        # UploadFile may handle this differently — just check it doesn't crash
        with pytest.raises(HTTPException):
            await validate_audio_file(file)


class TestImageFileValidation:

    @pytest.mark.asyncio
    async def test_valid_png_file(self):
        # Minimal valid PNG
        png_header = b"\x89PNG\r\n\x1a\n"
        content = png_header + b"\x00" * 2000  # Pad to reasonable size
        file = _make_upload_file(content, "qr_code.png")
        result = await validate_image_file(file)

        assert result["extension"] == ".png"
        assert result["size_bytes"] > 0

    @pytest.mark.asyncio
    async def test_unsupported_image_format(self):
        file = _make_upload_file(b"content" * 100, "image.bmp")

        with pytest.raises(HTTPException) as exc_info:
            await validate_image_file(file)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_image_too_small(self):
        file = _make_upload_file(b"x", "tiny.png")

        with pytest.raises(HTTPException) as exc_info:
            await validate_image_file(file)
        assert exc_info.value.status_code == 400