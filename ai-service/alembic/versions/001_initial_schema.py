"""Initial schema migration: Create users, verifications, signals, greencoins, epr, audit, and assistant tables

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-05 16:54:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('CITIZEN', 'MUNICIPAL', 'PRODUCER', 'ADMIN', name='roleenum'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)

    # 2. Verification Records
    op.create_table(
        'verification_records',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=True),
        sa.Column('image_hash', sa.String(length=64), nullable=True),
        sa.Column('file_name', sa.String(length=255), nullable=True),
        sa.Column('file_size_bytes', sa.Float(), nullable=True),
        sa.Column('waste_category', sa.String(length=100), nullable=False),
        sa.Column('detected_label', sa.String(length=100), nullable=True),
        sa.Column('detection_confidence', sa.Float(), nullable=True),
        sa.Column('ocr_text', sa.Text(), nullable=True),
        sa.Column('brand_name', sa.String(length=150), nullable=True),
        sa.Column('barcode_value', sa.String(length=100), nullable=True),
        sa.Column('authenticity_score', sa.Float(), nullable=False),
        sa.Column('detection_score', sa.Float(), nullable=False),
        sa.Column('brand_score', sa.Float(), nullable=False),
        sa.Column('composite_score', sa.Float(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'VERIFIED', 'REJECTED', 'REVIEW_REQUIRED', 'FAILED', name='verificationstatusenum'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_verification_records_id'), 'verification_records', ['id'], unique=False)
    op.create_index(op.f('ix_verification_records_user_id'), 'verification_records', ['user_id'], unique=False)
    op.create_index(op.f('ix_verification_records_waste_category'), 'verification_records', ['waste_category'], unique=False)
    op.create_index(op.f('ix_verification_records_brand_name'), 'verification_records', ['brand_name'], unique=False)
    op.create_index(op.f('ix_verification_records_created_at'), 'verification_records', ['created_at'], unique=False)

    # 3. Verification Signals
    op.create_table(
        'verification_signals',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('verification_id', sa.String(length=36), nullable=False),
        sa.Column('signal_type', sa.Enum('YOLO_DETECTION', 'OCR_BRAND', 'BARCODE', 'AUTHENTICITY', 'SCORE_BREAKDOWN', name='signaltypeenum'), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['verification_id'], ['verification_records.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_verification_signals_verification_id'), 'verification_signals', ['verification_id'], unique=False)

    # 4. GreenCoin Transactions
    op.create_table(
        'greencoin_transactions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=True),
        sa.Column('verification_id', sa.String(length=36), nullable=True),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('transaction_type', sa.Enum('EARNED', 'REDEEMED', 'BONUS', 'ADJUSTMENT', name='transactiontypeenum'), nullable=False),
        sa.Column('reward_tier', sa.Enum('BRONZE', 'SILVER', 'GOLD', 'PLATINUM', name='rewardtierenum'), nullable=False),
        sa.Column('calculation_basis', sa.String(length=255), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['verification_id'], ['verification_records.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('verification_id')
    )
    op.create_index(op.f('ix_greencoin_transactions_user_id'), 'greencoin_transactions', ['user_id'], unique=False)

    # 5. EPR Records
    op.create_table(
        'epr_records',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('verification_id', sa.String(length=36), nullable=False),
        sa.Column('evidence_id', sa.String(length=100), nullable=False),
        sa.Column('brand_name', sa.String(length=150), nullable=True),
        sa.Column('material_type', sa.String(length=100), nullable=False),
        sa.Column('waste_category', sa.String(length=100), nullable=False),
        sa.Column('weight_kg', sa.Float(), nullable=False),
        sa.Column('epr_credits_generated', sa.Float(), nullable=False),
        sa.Column('recyclability_tier', sa.String(length=50), nullable=False),
        sa.Column('compliance_status', sa.Enum('COMPLIANT', 'PENDING_AUDIT', 'REJECTED', name='eprcompliancestatusenum'), nullable=False),
        sa.Column('regulatory_standard', sa.String(length=255), nullable=False),
        sa.Column('calculation_summary', sa.String(length=255), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['verification_id'], ['verification_records.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('verification_id'),
        sa.UniqueConstraint('evidence_id')
    )
    op.create_index(op.f('ix_epr_records_brand_name'), 'epr_records', ['brand_name'], unique=False)

    # 6. Audit Logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('endpoint', sa.String(length=255), nullable=False),
        sa.Column('method', sa.String(length=10), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('request_id', sa.String(length=100), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)

    # 7. Assistant Sessions & Messages
    op.create_table(
        'assistant_sessions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'assistant_messages',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('session_id', sa.String(length=36), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('model_name', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['assistant_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('assistant_messages')
    op.drop_table('assistant_sessions')
    op.drop_table('audit_logs')
    op.drop_table('epr_records')
    op.drop_table('greencoin_transactions')
    op.drop_table('verification_signals')
    op.drop_table('verification_records')
    op.drop_table('users')
