"""initial_schema

Revision ID: 001
Revises: 
Create Date: 2024-01-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── ENUM Types ──
    user_role = postgresql.ENUM('user', 'admin', 'org_admin', name='user_role', create_type=False)
    user_role.create(op.get_bind(), checkfirst=True)

    org_type = postgresql.ENUM('bank', 'college', 'govt', 'other', name='org_type', create_type=False)
    org_type.create(op.get_bind(), checkfirst=True)

    membership_role = postgresql.ENUM('member', 'coordinator', 'admin', name='membership_role', create_type=False)
    membership_role.create(op.get_bind(), checkfirst=True)

    analysis_type = postgresql.ENUM('email', 'url', 'qr', 'audio', 'video', name='analysis_type', create_type=False)
    analysis_type.create(op.get_bind(), checkfirst=True)

    risk_label = postgresql.ENUM('safe', 'suspicious', 'dangerous', name='risk_label', create_type=False)
    risk_label.create(op.get_bind(), checkfirst=True)

    quiz_category = postgresql.ENUM('deepfake', 'phishing', 'upi_qr', 'kyc_otp', 'general', name='quiz_category', create_type=False)
    quiz_category.create(op.get_bind(), checkfirst=True)

    actor_type = postgresql.ENUM('user', 'system', name='actor_type', create_type=False)
    actor_type.create(op.get_bind(), checkfirst=True)

    audit_target_type = postgresql.ENUM('analysis', 'quiz', 'config', 'user', name='audit_target_type', create_type=False)
    audit_target_type.create(op.get_bind(), checkfirst=True)

    # ── Users ──
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('display_name', sa.String(100), nullable=True),
        sa.Column('role', user_role, nullable=False, server_default='user'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # ── Organizations ──
    op.create_table(
        'organizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', org_type, nullable=False, server_default='other'),
        sa.Column('contact_email', sa.String(255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ── Org Memberships ──
    op.create_table(
        'org_memberships',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', membership_role, nullable=False, server_default='member'),
        sa.Column('joined_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint('org_id', 'user_id', name='uq_org_user'),
    )

    # ── Analyses ──
    op.create_table(
        'analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('type', analysis_type, nullable=False),
        sa.Column('input_hash', sa.String(64), nullable=False),
        sa.Column('risk_score', sa.SmallInteger(), nullable=False),
        sa.Column('risk_label', risk_label, nullable=False),
        sa.Column('explanation_summary', sa.Text(), nullable=False),
        sa.Column('model_scores', postgresql.JSONB(), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('is_demo', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint('risk_score >= 0 AND risk_score <= 100', name='ck_risk_score_range'),
    )
    op.create_index('ix_analyses_user_id', 'analyses', ['user_id'])
    op.create_index('ix_analyses_org_id', 'analyses', ['org_id'])
    op.create_index('ix_analyses_type', 'analyses', ['type'])
    op.create_index('ix_analyses_created_at', 'analyses', ['created_at'])
    op.create_index('ix_analyses_input_hash', 'analyses', ['input_hash'])

    # ── Analysis Details ──
    op.create_table(
        'analysis_details',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('analysis_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('analyses.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('raw_metadata', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('highlighted_elements', postgresql.JSONB(), server_default='[]'),
        sa.Column('contributing_factors', postgresql.JSONB(), server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ── Quiz Questions ──
    op.create_table(
        'quiz_questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('category', quiz_category, nullable=False),
        sa.Column('difficulty', sa.SmallInteger(), nullable=False, server_default='1'),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('options', postgresql.JSONB(), nullable=False),
        sa.Column('correct_option_index', sa.SmallInteger(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('language', sa.String(5), nullable=False, server_default='en'),
        sa.Column('tags', postgresql.JSONB(), server_default='[]'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint('difficulty >= 1 AND difficulty <= 3', name='ck_difficulty_range'),
        sa.CheckConstraint('correct_option_index >= 0 AND correct_option_index <= 3', name='ck_correct_option_range'),
    )
    op.create_index('ix_quiz_questions_category', 'quiz_questions', ['category'])
    op.create_index('ix_quiz_questions_language', 'quiz_questions', ['language'])

    # ── Quiz Sessions ──
    op.create_table(
        'quiz_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('category', quiz_category, nullable=False),
        sa.Column('total_questions', sa.SmallInteger(), nullable=False, server_default='10'),
        sa.Column('correct_count', sa.SmallInteger(), server_default='0'),
        sa.Column('score_pct', sa.SmallInteger(), server_default='0'),
        sa.Column('badge_earned', sa.String(20), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint('score_pct >= 0 AND score_pct <= 100', name='ck_score_pct_range'),
    )
    op.create_index('ix_quiz_sessions_user_id', 'quiz_sessions', ['user_id'])

    # ── Quiz Answers ──
    op.create_table(
        'quiz_answers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('quiz_session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('quiz_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('quiz_questions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('selected_option_index', sa.SmallInteger(), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('answered_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint('quiz_session_id', 'question_id', name='uq_session_question'),
        sa.CheckConstraint('selected_option_index >= 0 AND selected_option_index <= 3', name='ck_selected_option_range'),
    )

    # ── Scenarios ──
    op.create_table(
        'scenarios',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', quiz_category, nullable=False),
        sa.Column('scenario_type', sa.String(20), nullable=False, server_default='chat'),
        sa.Column('steps', postgresql.JSONB(), nullable=False),
        sa.Column('language', sa.String(5), nullable=False, server_default='en'),
        sa.Column('estimated_time_minutes', sa.SmallInteger(), server_default='5'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ── Scoring Configs ──
    op.create_table(
        'scoring_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=True),
        sa.Column('audio_weight', sa.Numeric(3, 2), nullable=False, server_default='0.35'),
        sa.Column('video_weight', sa.Numeric(3, 2), nullable=False, server_default='0.35'),
        sa.Column('phish_weight', sa.Numeric(3, 2), nullable=False, server_default='0.30'),
        sa.Column('safe_threshold', sa.SmallInteger(), nullable=False, server_default='30'),
        sa.Column('dangerous_threshold', sa.SmallInteger(), nullable=False, server_default='70'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint('safe_threshold >= 0 AND safe_threshold <= 100', name='ck_safe_threshold_range'),
        sa.CheckConstraint('dangerous_threshold >= 0 AND dangerous_threshold <= 100', name='ck_dangerous_threshold_range'),
        sa.CheckConstraint('safe_threshold < dangerous_threshold', name='ck_threshold_order'),
    )

    # ── OTP Tokens ──
    op.create_table(
        'otp_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('otp_hash', sa.String(255), nullable=False),
        sa.Column('purpose', sa.String(20), nullable=False, server_default='login'),
        sa.Column('attempts', sa.SmallInteger(), nullable=False, server_default='0'),
        sa.Column('max_attempts', sa.SmallInteger(), nullable=False, server_default='3'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_otp_tokens_email', 'otp_tokens', ['email'])
    op.create_index('ix_otp_tokens_expires', 'otp_tokens', ['expires_at'])

    # ── Refresh Tokens ──
    op.create_table(
        'refresh_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token_hash', sa.String(255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_refresh_tokens_user', 'refresh_tokens', ['user_id'])

    # ── Audit Logs ──
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('actor_type', actor_type, nullable=False),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('target_type', audit_target_type, nullable=False),
        sa.Column('target_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), server_default='{}'),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_audit_logs_created', 'audit_logs', ['created_at'])

    # ── Insert Global Default Scoring Config ──
    op.execute("""
        INSERT INTO scoring_configs (id, org_id, audio_weight, video_weight, phish_weight, safe_threshold, dangerous_threshold, is_active, created_at)
        VALUES (gen_random_uuid(), NULL, 0.35, 0.35, 0.30, 30, 70, true, NOW())
    """)


def downgrade() -> None:
    # Drop tables in reverse dependency order
    op.drop_table('audit_logs')
    op.drop_table('refresh_tokens')
    op.drop_table('otp_tokens')
    op.drop_table('scoring_configs')
    op.drop_table('scenarios')
    op.drop_table('quiz_answers')
    op.drop_table('quiz_sessions')
    op.drop_table('quiz_questions')
    op.drop_table('analysis_details')
    op.drop_table('analyses')
    op.drop_table('org_memberships')
    op.drop_table('organizations')
    op.drop_table('users')

    # Drop ENUM types
    for enum_name in [
        'audit_target_type', 'actor_type', 'quiz_category',
        'risk_label', 'analysis_type', 'membership_role',
        'org_type', 'user_role'
    ]:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")