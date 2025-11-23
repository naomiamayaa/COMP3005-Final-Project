# test_scheduling.py
import datetime as dt

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# tests/test_scheduling.py
import os
import sys

# Add project-root (one level up from tests/) to sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.database import Base
from app import scheduling
from app.models import (
    Users,
    Members,
    HealthMetrics,
    MemberGoals,
    Classes,
    ClassRegistrations,
    UserRole,
    ClassType,
)


# ---- Test DB / Session setup ----

# Use an in-memory SQLite DB for tests
engine = create_engine("sqlite:///:memory:", future=True)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    """Create all tables once for the test module and monkeypatch SessionLocal."""
    Base.metadata.create_all(bind=engine)
    # monkeypatch the SessionLocal used inside scheduling.get_user_dashboard
    scheduling.SessionLocal = TestingSessionLocal
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Provide a fresh DB session for each test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

def test_dashboard_empty_user(db):
    # Arrange: create a member user
    user = Members(
        email="test1@example.com",
        password_hash="hashed",
        first_name="Test",
        last_name="User",
        role=UserRole.MEMBER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Act
    result = scheduling.get_user_dashboard(user.id)

    # Assert
    assert result["user"].id == user.id
    assert result["latest_health"] is None
    assert result["goals"] == []
    assert result["past_class_count"] == 0
    assert result["upcoming_sessions"] == []

def test_dashboard_latest_health_and_goals(db):
    # Arrange: create member
    member = Members(
        email="test2@example.com",
        password_hash="hashed",
        first_name="Health",
        last_name="User",
        role=UserRole.MEMBER,
    )
    db.add(member)
    db.commit()
    db.refresh(member)

    # Two health metrics; latest should be picked
    hm1 = HealthMetrics(
        member_id=member.id,
        date_recorded=dt.date(2024, 1, 1),
        weight=70.0,
        height=170.0,
        bpm=60,
    )
    hm2 = HealthMetrics(
        member_id=member.id,
        date_recorded=dt.date(2024, 2, 1),
        weight=69.0,
        height=170.0,
        bpm=58,
    )
    db.add_all([hm1, hm2])

    # Two goals
    g1 = MemberGoals(member_id=member.id, current_weight=70.0, target_weight=65.0)
    g2 = MemberGoals(member_id=member.id, current_weight=69.0, target_weight=64.0)
    db.add_all([g1, g2])

    db.commit()

    # Act
    result = scheduling.get_user_dashboard(member.id)

    # Assert: latest_health should be hm2
    assert result["latest_health"] is not None
    assert result["latest_health"].date_recorded == dt.date(2024, 2, 1)

    # goals contains both
    assert len(result["goals"]) == 2
    goal_weights = sorted(g.current_weight for g in result["goals"])
    assert goal_weights == [69.0, 70.0]

def test_dashboard_past_class_count_and_upcoming_sessions(db):
    now = dt.datetime.now()

    # Create trainer
    trainer = Users(
        email="trainer@example.com",
        password_hash="hashed",
        first_name="Train",
        last_name="Er",
        role=UserRole.TRAINER,
    )
    db.add(trainer)

    # Create member
    member = Members(
        email="test3@example.com",
        password_hash="hashed",
        first_name="Class",
        last_name="User",
        role=UserRole.MEMBER,
    )
    db.add(member)
    db.commit()
    db.refresh(trainer)
    db.refresh(member)

    past_class_attended = Classes(
        trainer_id=trainer.id,
        description="Past class attended",
        class_type=ClassType.GROUP,
        start_datetime=now - dt.timedelta(days=2),
        end_datetime=now - dt.timedelta(days=2, hours=-1),
    )

    past_class_not_attended = Classes(
        trainer_id=trainer.id,
        description="Past class not attended",
        class_type=ClassType.GROUP,
        start_datetime=now - dt.timedelta(days=3),
        end_datetime=now - dt.timedelta(days=3, hours=-1),
    )

    future_class = Classes(
        trainer_id=trainer.id,
        description="Future class",
        class_type=ClassType.GROUP,
        start_datetime=now + dt.timedelta(days=2),
        end_datetime=now + dt.timedelta(days=2, hours=1),
    )

    db.add_all([past_class_attended, past_class_not_attended, future_class])
    db.commit()
    db.refresh(past_class_attended)
    db.refresh(past_class_not_attended)
    db.refresh(future_class)

    # Registrations
    reg1 = ClassRegistrations(
        member_id=member.id,
        class_id=past_class_attended.id,
        attended=True,
    )
    reg2 = ClassRegistrations(
        member_id=member.id,
        class_id=past_class_not_attended.id,
        attended=False,
    )
    reg3 = ClassRegistrations(
        member_id=member.id,
        class_id=future_class.id,
        attended=False,
    )
    db.add_all([reg1, reg2, reg3])
    db.commit()

    # Act
    result = scheduling.get_user_dashboard(member.id)

    # Assert
    assert result["past_class_count"] == 1

    upcoming = result["upcoming_sessions"]
    assert len(upcoming) == 1
    assert upcoming[0].id == future_class.id
