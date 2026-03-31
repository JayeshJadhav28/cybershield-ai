"""
/analyze/*  routes  —  Email · URL · QR · Audio · Video · Image

Each endpoint:
  1. validates input
  2. calls the appropriate analyser  →  ai_score + rule_score
  3. passes result into ScoringEngine  →  75% AI / 25% rules
  4. persists to DB (if authenticated)
  5. returns JSON response
"""
from __future__ import annotations

import hashlib
import logging
import os
import time
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from dependencies import get_current_user_optional
from schemas.analysis import (
    AnalysisResponse,
    EmailAnalysisRequest,
    URLAnalysisRequest,
)
from services.scoring_engine import (
    ModalityResult,
    ScoringEngine,
    ScoringInput,
)
from services.explainability import ExplainabilityService

logger = logging.getLogger(__name__)
router = APIRouter()

# Instantiate services once
scoring_engine = ScoringEngine()
explainer = ExplainabilityService()


# ── Module-level Helpers (available to all endpoints) ──────────────────
def _save_temp(upload: UploadFile, suffix: str = "") -> str:
    """Write UploadFile to disk, return temp path."""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    ext = suffix or os.path.splitext(upload.filename or "")[1]
    path = os.path.join(settings.UPLOAD_DIR, f"{uuid.uuid4()}{ext}")
    content = upload.file.read()
    with open(path, "wb") as f:
        f.write(content)
    return path


def _persist(db: Session, user, analysis_type: str, input_hash: str,
             score_out, explanation: dict, processing_ms: int,
             model_scores: dict, raw_metadata: dict, is_demo: bool = False):
    """Save analysis + detail rows to DB."""
    try:
        from models.analysis import Analysis, AnalysisDetail
        analysis = Analysis(
            id=uuid.uuid4(),
            user_id=user.id if user else None,
            type=analysis_type,
            input_hash=input_hash,
            risk_score=score_out.risk_score,
            risk_label=score_out.risk_label,
            explanation_summary=score_out.explanation_summary,
            model_scores=model_scores,
            processing_time_ms=processing_ms,
            is_demo=is_demo,
        )
        db.add(analysis)
        detail = AnalysisDetail(
            analysis_id=analysis.id,
            raw_metadata=raw_metadata,
            highlighted_elements=explanation.get("highlights", {}),
            contributing_factors=score_out.contributing_factors,
        )
        db.add(detail)
        db.commit()
        return str(analysis.id)
    except Exception as e:
        logger.warning("DB persist failed: %s", e)
        db.rollback()
        return str(uuid.uuid4())


# ═══════════════════════════════════════════════════════════════════
# POST /analyze/email
# ═══════════════════════════════════════════════════════════════════
@router.post("/email", response_model=None)
async def analyze_email(
    request: EmailAnalysisRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    start = time.time()
    from services.email_analyzer import EmailAnalyzer

    analyzer = EmailAnalyzer()
    input_text = f"{request.subject}|{request.body}|{request.sender}|{'|'.join(request.urls or [])}"
    input_hash = hashlib.sha256(input_text.encode()).hexdigest()

    phish_result = analyzer.analyze(
        subject=request.subject,
        body=request.body,
        sender=request.sender,
        urls=request.urls or [],
    )

    modality = ModalityResult(
        ai_probability=phish_result.probability,
        rule_score=phish_result.probability,
        confidence=phish_result.confidence,
        features=phish_result.features,
        flags=phish_result.flags,
        model_available=False,
    )

    score_out = scoring_engine.compute(ScoringInput(
        phish_result=modality,
        analysis_type="email",
        contextual_flags=phish_result.flags,
    ))

    explanation = explainer.generate("email", score_out, phish_result.features)
    processing_ms = int((time.time() - start) * 1000)

    analysis_id = _persist(
        db, current_user, "email", input_hash, score_out,
        explanation, processing_ms,
        score_out.model_scores, phish_result.features,
    )

    return {
        "analysis_id": analysis_id,
        "risk_score": score_out.risk_score,
        "risk_label": score_out.risk_label,
        "processing_time_ms": processing_ms,
        "explanation": {
            "summary": score_out.explanation_summary,
            **explanation,
            "contributing_factors": score_out.contributing_factors,
            "scoring_breakdown": score_out.breakdown,
        },
        "tip": explainer.get_tip("email", score_out.risk_label),
    }


# ═══════════════════════════════════════════════════════════════════
# POST /analyze/audio
# ═══════════════════════════════════════════════════════════════════
@router.post("/audio", response_model=None)
async def analyze_audio(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    from utils.file_validation import validate_audio_file
    from services.audio_analyzer import AudioAnalyzer

    start = time.time()
    await validate_audio_file(file)

    content = await file.read()
    await file.seek(0)
    temp_path = _save_temp(file)
    try:
        input_hash = hashlib.sha256(content).hexdigest()

        analyzer = AudioAnalyzer()
        audio_result = analyzer.analyze(temp_path)

        modality = ModalityResult(
            ai_probability=audio_result.ai_probability,
            rule_score=audio_result.rule_score,
            confidence=audio_result.confidence,
            features=audio_result.features,
            flags=audio_result.flags,
            model_available=audio_result.model_available,
        )

        score_out = scoring_engine.compute(ScoringInput(
            audio_result=modality,
            analysis_type="audio",
        ))

        explanation = explainer.generate("audio", score_out, audio_result.features)
        processing_ms = int((time.time() - start) * 1000)

        analysis_id = _persist(
            db, current_user, "audio", input_hash, score_out,
            explanation, processing_ms,
            score_out.model_scores, audio_result.metadata,
        )

        return {
            "analysis_id": analysis_id,
            "risk_score": score_out.risk_score,
            "risk_label": score_out.risk_label,
            "processing_time_ms": processing_ms,
            "audio_metadata": audio_result.metadata,
            "explanation": {
                "summary": score_out.explanation_summary,
                **explanation,
                "contributing_factors": score_out.contributing_factors,
                "scoring_breakdown": score_out.breakdown,
            },
            "tip": explainer.get_tip("audio", score_out.risk_label),
        }
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


# ═══════════════════════════════════════════════════════════════════
# POST /analyze/video
# ═══════════════════════════════════════════════════════════════════
@router.post("/video", response_model=None)
async def analyze_video(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    from utils.file_validation import validate_video_file
    from services.video_analyzer import VideoAnalyzer

    start = time.time()
    await validate_video_file(file)

    content = await file.read()
    await file.seek(0)
    temp_path = _save_temp(file)
    try:
        input_hash = hashlib.sha256(content).hexdigest()

        analyzer = VideoAnalyzer()
        video_result = analyzer.analyze(temp_path)

        modality = ModalityResult(
            ai_probability=video_result.ai_probability,
            rule_score=video_result.rule_score,
            confidence=video_result.confidence,
            features=video_result.features,
            flags=video_result.flags,
            model_available=video_result.model_available,
        )

        score_out = scoring_engine.compute(ScoringInput(
            video_result=modality,
            analysis_type="video",
        ))

        explanation = explainer.generate("video", score_out, video_result.features)
        processing_ms = int((time.time() - start) * 1000)

        analysis_id = _persist(
            db, current_user, "video", input_hash, score_out,
            explanation, processing_ms,
            score_out.model_scores, video_result.metadata,
        )

        return {
            "analysis_id": analysis_id,
            "risk_score": score_out.risk_score,
            "risk_label": score_out.risk_label,
            "processing_time_ms": processing_ms,
            "video_metadata": video_result.metadata,
            "explanation": {
                "summary": score_out.explanation_summary,
                **explanation,
                "contributing_factors": score_out.contributing_factors,
                "scoring_breakdown": score_out.breakdown,
            },
            "tip": explainer.get_tip("video", score_out.risk_label),
        }
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


# ═══════════════════════════════════════════════════════════════════
# POST /analyze/image
# ═══════════════════════════════════════════════════════════════════
@router.post("/image", response_model=None)
async def analyze_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    from utils.file_validation import validate_image_file
    from services.image_analyzer import ImageAnalyzer

    start = time.time()
    await validate_image_file(file)

    content = await file.read()
    await file.seek(0)
    temp_path = _save_temp(file)
    try:
        input_hash = hashlib.sha256(content).hexdigest()

        analyzer = ImageAnalyzer()
        image_result = analyzer.analyze(temp_path)

        modality = ModalityResult(
            ai_probability=image_result.ai_probability,
            rule_score=image_result.rule_score,
            confidence=image_result.confidence,
            features=image_result.features,
            flags=image_result.flags,
            model_available=image_result.model_available,
        )

        score_out = scoring_engine.compute(ScoringInput(
            video_result=modality,
            analysis_type="image",
        ))

        explanation = explainer.generate("image", score_out, image_result.features)
        processing_ms = int((time.time() - start) * 1000)

        analysis_id = _persist(
            db, current_user, "image", input_hash, score_out,
            explanation, processing_ms,
            score_out.model_scores, image_result.metadata,
        )

        return {
            "analysis_id": analysis_id,
            "risk_score": score_out.risk_score,
            "risk_label": score_out.risk_label,
            "processing_time_ms": processing_ms,
            "image_metadata": image_result.metadata,
            "per_face_scores": image_result.per_face_scores,
            "explanation": {
                "summary": score_out.explanation_summary,
                **explanation,
                "contributing_factors": score_out.contributing_factors,
                "scoring_breakdown": score_out.breakdown,
            },
            "tip": explainer.get_tip("image", score_out.risk_label),
        }
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


# ═══════════════════════════════════════════════════════════════════
# POST /analyze/url
# ═══════════════════════════════════════════════════════════════════
@router.post("/url", response_model=None)
async def analyze_url(
    request: URLAnalysisRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    start = time.time()
    # ── FIX: import the singleton instance directly, don't re-call it ──
    from services.url_analyzer import url_analyzer

    url_result = url_analyzer.analyze(request.url)

    modality = ModalityResult(
        ai_probability=url_result.probability,
        rule_score=getattr(url_result, "rule_score", url_result.probability),
        confidence=url_result.confidence,
        features=url_result.features,
        flags=url_result.flags,
        model_available=True,
    )

    score_out = scoring_engine.compute(ScoringInput(
        phish_result=modality,
        analysis_type="url",
        contextual_flags=url_result.flags,
    ))

    explanation = explainer.generate("url", score_out, url_result.features)
    processing_ms = int((time.time() - start) * 1000)
    input_hash = hashlib.sha256(request.url.encode()).hexdigest()

    analysis_id = _persist(
        db, current_user, "url", input_hash, score_out,
        explanation, processing_ms,
        score_out.model_scores, url_result.features,
    )

    return {
        "analysis_id": analysis_id,
        "risk_score": score_out.risk_score,
        "risk_label": score_out.risk_label,
        "processing_time_ms": processing_ms,
        "explanation": {
            "summary": score_out.explanation_summary,
            **explanation,
            "contributing_factors": score_out.contributing_factors,
            "scoring_breakdown": score_out.breakdown,
        },
        "tip": explainer.get_tip("url", score_out.risk_label),
    }


# ═══════════════════════════════════════════════════════════════════
# POST /analyze/qr
# ═══════════════════════════════════════════════════════════════════
@router.post("/qr", response_model=None)
async def analyze_qr(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    start = time.time()
    # ── FIX: import the singleton instance (lowercase), class is QRAnalyzer ──
    from services.qr_analyzer import qr_analyzer

    content = await file.read()
    await file.seek(0)
    temp_path = _save_temp(file)
    try:
        qr_result = qr_analyzer.analyze(temp_path)

        modality = ModalityResult(
            ai_probability=qr_result.probability,
            rule_score=getattr(qr_result, "rule_score", qr_result.probability),
            confidence=qr_result.confidence,
            features=qr_result.features,
            flags=qr_result.flags,
            model_available=True,
        )

        score_out = scoring_engine.compute(ScoringInput(
            phish_result=modality,
            analysis_type="qr",
            contextual_flags=qr_result.flags,
        ))

        explanation = explainer.generate("qr", score_out, qr_result.features)
        processing_ms = int((time.time() - start) * 1000)
        input_hash = hashlib.sha256(content).hexdigest()

        analysis_id = _persist(
            db, current_user, "qr", input_hash, score_out,
            explanation, processing_ms,
            score_out.model_scores, qr_result.features,
        )

        return {
            "analysis_id": analysis_id,
            "decoded": qr_result.decoded,
            "risk_score": score_out.risk_score,
            "risk_label": score_out.risk_label,
            "processing_time_ms": processing_ms,
            "explanation": {
                "summary": score_out.explanation_summary,
                **explanation,
                "contributing_factors": score_out.contributing_factors,
                "scoring_breakdown": score_out.breakdown,
            },
            "tip": explainer.get_tip("qr", score_out.risk_label),
        }
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)