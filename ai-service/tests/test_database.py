import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.user import User, RoleEnum
from app.models.verification import VerificationRecord, VerificationStatusEnum, SignalTypeEnum
from app.models.epr import EprComplianceStatusEnum
from app.repositories.user_repository import UserRepository
from app.repositories.verification_repository import VerificationRepository
from app.repositories.greencoin_repository import GreenCoinRepository
from app.repositories.epr_repository import EprRepository
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.audit_repository import AuditRepository


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_user_creation_and_lookup(db_session):
    user_repo = UserRepository(db_session)
    user = user_repo.create_user(
        email="citizen@greenloop.ai",
        full_name="Jane Doe",
        password_hash="hashed_secret",
        role=RoleEnum.CITIZEN
    )
    assert user.id is not None
    assert user.email == "citizen@greenloop.ai"
    assert user.role == RoleEnum.CITIZEN

    found = user_repo.get_by_email("citizen@greenloop.ai")
    assert found is not None
    assert found.id == user.id


def test_atomic_verification_greencoins_epr_save(db_session):
    user_repo = UserRepository(db_repo := db_session)
    user = user_repo.create_user("tester@greenloop.ai", "Tester", "pwd")
    
    v_repo = VerificationRepository(db_session)
    record = v_repo.save_complete_verification(
        verification_id="VER-TEST-12345",
        user_id=user.id,
        file_name="plastic_bottle.jpg",
        file_size_bytes=102400.0,
        waste_category="Plastic",
        detected_label="Bottle",
        detection_confidence=0.92,
        ocr_text="Bisleri Pure Water",
        brand_name="Bisleri",
        barcode_value="8901234567890",
        authenticity_score=85.0,
        detection_score=90.0,
        brand_score=95.0,
        composite_score=89.5,
        status=VerificationStatusEnum.VERIFIED,
        signals=[
            {
                "signal_type": SignalTypeEnum.YOLO_DETECTION,
                "confidence": 0.92,
                "payload": {"label": "Bottle", "confidence": 0.92}
            }
        ],
        reward_coins=55,
        reward_tier="PLATINUM",
        reward_basis="Score 89.5% + EPR Brand Bonus",
        epr_evidence_id="EPR-20261005-A1B2C3D4",
        epr_credits=0.088,
        epr_material="PET",
        epr_weight=0.08,
        epr_tier="TIER_1_HIGH",
        epr_status=EprComplianceStatusEnum.COMPLIANT,
        epr_standard="CPCB EPR Guidelines",
        epr_summary="0.08 kg × 1.2 × 0.895 = 0.088 Credits"
    )

    assert record.id == "VER-TEST-12345"
    assert record.status == VerificationStatusEnum.VERIFIED
    assert record.greencoin_transaction is not None
    assert record.greencoin_transaction.amount == 55
    assert record.epr_record is not None
    assert record.epr_record.evidence_id == "EPR-20261005-A1B2C3D4"

    # Test GreenCoin ledger balance
    coin_repo = GreenCoinRepository(db_session)
    balance = coin_repo.get_user_balance(user.id)
    assert balance == 55

    # Test Analytics Aggregation
    analytics_repo = AnalyticsRepository(db_session)
    summary = analytics_repo.get_dashboard_summary()
    assert summary["has_data"] is True
    assert summary["total_verifications"] == 1
    assert summary["verified_count"] == 1
    assert summary["total_greencoins_issued"] == 55
    assert summary["total_epr_credits"] == 0.088
    assert "Plastic" in summary["category_distribution"]


def test_audit_logging(db_session):
    audit_repo = AuditRepository(db_session)
    log = audit_repo.log_event(
        action="VERIFICATION_PROCESSED",
        endpoint="/api/v1/verification/verify",
        method="POST",
        status_code=200,
        request_id="req-999"
    )
    assert log.id is not None
    logs, total = audit_repo.list_logs()
    assert total == 1
    assert logs[0].action == "VERIFICATION_PROCESSED"
