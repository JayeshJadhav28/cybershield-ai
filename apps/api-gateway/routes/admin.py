"""
Admin routes — org metrics, scoring config, content management.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from dependencies import get_current_user_required, require_admin

from models.analysis import Analysis
from models.user import User
from models.quiz import QuizSession
from models.config import ScoringConfig
from models.organization import OrgMembership

from schemas.admin import (
    OrgMetricsResponse,
    AnalysisByType,
    RiskDistribution,
    QuizMetrics,
    ScoringConfigUpdate,
    ScoringConfigResponse,
)

from services.quiz_service import quiz_service

router = APIRouter()


# ═══════════════════════════════════════════
# ORG METRICS
# ═══════════════════════════════════════════

@router.get(
    "/metrics",
    response_model=OrgMetricsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get organization metrics",
    description="Returns aggregated analytics for the user's organization. Requires admin role.",
)
async def get_org_metrics(
    current_user=Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    # Find user's org
    org_id = None
    if current_user.org_memberships:
        org_id = current_user.org_memberships[0].org_id

    # Total users (in org or global for admins)
    if org_id:
        total_users = (
            db.query(OrgMembership)
            .filter(OrgMembership.org_id == org_id)
            .count()
        )
    elif current_user.role == "admin":
        total_users = db.query(User).filter(User.is_active == True).count()
    else:
        total_users = 1

    # Analysis metrics
    analysis_query = db.query(Analysis)
    if org_id:
        analysis_query = analysis_query.filter(Analysis.org_id == org_id)
    elif current_user.role != "admin":
        analysis_query = analysis_query.filter(Analysis.user_id == current_user.id)

    total_analyses = analysis_query.count()

    # By type
    type_counts = (
        analysis_query
        .with_entities(Analysis.type, func.count(Analysis.id))
        .group_by(Analysis.type)
        .all()
    )
    analyses_by_type = AnalysisByType()
    for atype, count in type_counts:
        if hasattr(analyses_by_type, atype):
            setattr(analyses_by_type, atype, count)

    # Risk distribution
    risk_counts = (
        analysis_query
        .with_entities(Analysis.risk_label, func.count(Analysis.id))
        .group_by(Analysis.risk_label)
        .all()
    )
    risk_dist = RiskDistribution()
    for label, count in risk_counts:
        if hasattr(risk_dist, label):
            setattr(risk_dist, label, count)

    # Quiz metrics
    if org_id:
        quiz_metrics_data = quiz_service.get_org_quiz_metrics(db, org_id)
    else:
        quiz_metrics_data = {
            "total_sessions": db.query(QuizSession).filter(
                QuizSession.user_id == current_user.id,
                QuizSession.completed_at.isnot(None),
            ).count(),
            "average_score": 0,
            "weakest_category": None,
            "completion_rate": 0.0,
        }
        sessions = db.query(QuizSession).filter(
            QuizSession.user_id == current_user.id,
            QuizSession.completed_at.isnot(None),
        ).all()
        if sessions:
            quiz_metrics_data["average_score"] = int(
                sum(s.score_pct for s in sessions) / len(sessions)
            )

    quiz_metrics = QuizMetrics(
        total_sessions=quiz_metrics_data.get("total_sessions", 0),
        average_score=quiz_metrics_data.get("average_score", 0),
        weakest_category=quiz_metrics_data.get("weakest_category"),
        completion_rate=quiz_metrics_data.get("completion_rate", 0.0),
    )

    return OrgMetricsResponse(
        org_id=str(org_id) if org_id else None,
        period="last_30_days",
        total_users=total_users,
        total_analyses=total_analyses,
        analyses_by_type=analyses_by_type,
        risk_distribution=risk_dist,
        quiz_metrics=quiz_metrics,
    )


# ═══════════════════════════════════════════
# SCORING CONFIG
# ═══════════════════════════════════════════

@router.get(
    "/scoring-config",
    response_model=ScoringConfigResponse,
    status_code=status.HTTP_200_OK,
    summary="Get scoring configuration",
    description="Returns current scoring engine configuration.",
)
async def get_scoring_config(
    current_user=Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    org_id = None
    if current_user.org_memberships:
        org_id = current_user.org_memberships[0].org_id

    config = None
    if org_id:
        config = (
            db.query(ScoringConfig)
            .filter(ScoringConfig.org_id == org_id, ScoringConfig.is_active == True)
            .first()
        )

    if not config:
        config = (
            db.query(ScoringConfig)
            .filter(ScoringConfig.org_id.is_(None), ScoringConfig.is_active == True)
            .first()
        )

    if not config:
        raise HTTPException(status_code=404, detail="No scoring config found")

    return ScoringConfigResponse(
        id=str(config.id),
        org_id=str(config.org_id) if config.org_id else None,
        audio_weight=float(config.audio_weight),
        video_weight=float(config.video_weight),
        phish_weight=float(config.phish_weight),
        safe_threshold=config.safe_threshold,
        dangerous_threshold=config.dangerous_threshold,
    )


@router.patch(
    "/scoring-config",
    response_model=ScoringConfigResponse,
    status_code=status.HTTP_200_OK,
    summary="Update scoring configuration",
    description="Update scoring weights and thresholds. Requires admin role.",
)
async def update_scoring_config(
    update: ScoringConfigUpdate,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    org_id = None
    if current_user.org_memberships:
        org_id = current_user.org_memberships[0].org_id

    config = None
    if org_id:
        config = (
            db.query(ScoringConfig)
            .filter(ScoringConfig.org_id == org_id, ScoringConfig.is_active == True)
            .first()
        )

    if not config:
        config = (
            db.query(ScoringConfig)
            .filter(ScoringConfig.org_id.is_(None), ScoringConfig.is_active == True)
            .first()
        )

    if not config:
        raise HTTPException(status_code=404, detail="No scoring config found")

    if update.audio_weight is not None:
        config.audio_weight = update.audio_weight
    if update.video_weight is not None:
        config.video_weight = update.video_weight
    if update.phish_weight is not None:
        config.phish_weight = update.phish_weight
    if update.safe_threshold is not None:
        config.safe_threshold = update.safe_threshold
    if update.dangerous_threshold is not None:
        config.dangerous_threshold = update.dangerous_threshold

    # Validate thresholds
    if config.safe_threshold >= config.dangerous_threshold:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="safe_threshold must be less than dangerous_threshold",
        )

    db.commit()
    db.refresh(config)

    return ScoringConfigResponse(
        id=str(config.id),
        org_id=str(config.org_id) if config.org_id else None,
        audio_weight=float(config.audio_weight),
        video_weight=float(config.video_weight),
        phish_weight=float(config.phish_weight),
        safe_threshold=config.safe_threshold,
        dangerous_threshold=config.dangerous_threshold,
    )