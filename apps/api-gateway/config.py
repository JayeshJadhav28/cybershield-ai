"""
CyberShield AI — Application Configuration
Loads from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


def _resolve_model_dir() -> str:
    """Resolve the models/ directory relative to project root."""
    # apps/api-gateway/config.py -> project root is ../../
    this_file = Path(__file__).resolve()
    project_root = this_file.parent.parent.parent
    candidate = project_root / "models"
    if candidate.is_dir():
        return str(candidate)
    # Docker / fallback
    return os.getenv("MODEL_DIR", "./models")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Allow extra env vars without error
    )

    # ── App Info ──
    APP_NAME: str = "CyberShield AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── Database ──
    DATABASE_URL: str = "postgresql://cybershield:cybershield_pass@localhost:5432/cybershield_db"

    # ── Authentication ──
    JWT_SECRET: str = "change-this-in-production-min-32-chars-long"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    OTP_EXPIRE_MINUTES: int = 5

        # ── Email (OTP Delivery) ──
    SMTP_HOST: str = "smtp.resend.com"
    SMTP_PORT: int = 465
    SMTP_USER: str = "resend"
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "onboarding@resend.dev"
    EMAIL_ENABLED: bool = False  # auto-set based on SMTP_HOST

    # ── Groq AI (free at console.groq.com) ──
    GROQ_API_KEY: str = ""                          # main key for chat
    GROQ_CHAT_MODEL: str = "llama-3.3-70b-versatile"  # best quality, 30 RPM
    GROQ_QUIZ_MODEL: str = "llama-3.1-8b-instant"   # faster, 14.4K RPD
    GROQ_QUIZ_API_KEY: str = ""                      # optional separate key for quiz (more quota)
    CHATBOT_ENABLED: bool = True

    # ── CORS ──
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [item.strip() for item in v.split(",")]
        return v

    # ── File Uploads ──
    UPLOAD_DIR: str = "/tmp/cybershield_uploads"
    MAX_AUDIO_SIZE_MB: int = 10
    MAX_VIDEO_SIZE_MB: int = 50
    MAX_IMAGE_SIZE_MB: int = 5
    MAX_AUDIO_DURATION_S: int = 30
    MAX_VIDEO_DURATION_S: int = 60

    # ── ML Models ──
    MODEL_DIR: str = _resolve_model_dir()
    AUDIO_MODEL_H5: str = "audio_deepfake_cnn.h5"
    AUDIO_MODEL_PT: str = "audio_deepfake_cnn.pt"
    VIDEO_MODEL_H5: str = "video_deepfake_detector.h5"
    VIDEO_MODEL_PT: str = "video_deepfake_detector.pt"
    PHISHING_CLASSIFIER_PKL: str = "phishing_classifier.pkl"
    PHISHING_VECTORIZER_PKL: str = "phishing_tfidf_vectorizer.pkl"

    # ── Hybrid Scoring Weights ──
    AI_WEIGHT: float = 0.75
    RULE_WEIGHT: float = 0.25

    # ── Scoring ──
    SAFE_THRESHOLD: int = 30
    DANGEROUS_THRESHOLD: int = 70

    # ── Audio Preprocessing ──
    AUDIO_SAMPLE_RATE: int = 16000
    AUDIO_DURATION_S: float = 4.0
    AUDIO_N_MELS: int = 128
    AUDIO_HOP_LENGTH: int = 512
    AUDIO_SPEC_SHAPE: tuple = (128, 128)

    # ── Video Preprocessing ──
    VIDEO_FRAME_RATE: int = 1  # extract 1 FPS
    VIDEO_FACE_SIZE: tuple = (128, 128)
    VIDEO_MAX_FRAMES: int = 60

        # ── Image Preprocessing ──
    IMAGE_FACE_SIZE: tuple = (128, 128)
    MAX_IMAGE_SIZE_MB: int = 5
    IMAGE_FORMATS: list = [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"]

    def audio_model_path(self, ext: str = "h5") -> Path:
        name = self.AUDIO_MODEL_H5 if ext == "h5" else self.AUDIO_MODEL_PT
        return Path(self.MODEL_DIR) / name

    def video_model_path(self, ext: str = "h5") -> Path:
        name = self.VIDEO_MODEL_H5 if ext == "h5" else self.VIDEO_MODEL_PT
        return Path(self.MODEL_DIR) / name

    def phishing_classifier_path(self) -> Path:
        return Path(self.MODEL_DIR) / self.PHISHING_CLASSIFIER_PKL

    def phishing_vectorizer_path(self) -> Path:
        return Path(self.MODEL_DIR) / self.PHISHING_VECTORIZER_PKL

    # ── Rate Limiting ──
    RATE_LIMIT_REQUESTS: int = 60
    RATE_LIMIT_PERIOD: int = 60  # seconds

    # ── Email (Optional) ──
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    FROM_EMAIL: str = "noreply@cybershield.ai"

    @property
    def upload_max_bytes(self) -> dict:
        return {
            "audio": self.MAX_AUDIO_SIZE_MB * 1024 * 1024,
            "video": self.MAX_VIDEO_SIZE_MB * 1024 * 1024,
            "image": self.MAX_IMAGE_SIZE_MB * 1024 * 1024,
        }


settings = Settings()