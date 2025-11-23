# tests/test_scheduling.py
import datetime as dt
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
    Trainers,
    HealthMetrics,
    MemberGoals,
    Classes,
    ClassRegistrations,
    TrainerAvailability,
    RoomAvailability,
    Rooms,
    UserRole,
    ClassType,
    RoomType,
)

# ----------------------
# TEST DB SETUP
# ----------------------

engine = create_engine("sqlite:///:memory:", future=True)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    scheduling.SessionLocal = TestingSessionLocal
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


# -------------------------------------------------------
# DASHBOARD TESTS
# -------------------------------------------------------

def test_dashboard_empty_user(db):
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

    result = scheduling.get_user_dashboard(user.id)

    assert result["user"].id == user.id
    assert result["latest_health"] is None
    assert result["goals"] == []
    assert result["past_class_count"] == 0
    assert result["upcoming_sessions"] == []


def test_dashboard_latest_health_and_goals(db):
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

    g1 = MemberGoals(member_id=member.id, current_weight=70.0, target_weight=65.0)
    g2 = MemberGoals(member_id=member.id, current_weight=69.0, target_weight=64.0)
    db.add_all([g1, g2])
    db.commit()

    result = scheduling.get_user_dashboard(member.id)

    assert result["latest_health"].date_recorded == dt.date(2024, 2, 1)
    assert len(result["goals"]) == 2


def test_dashboard_past_class_count_and_upcoming_sessions(db):
    now = dt.datetime.now()

    trainer = Users(
        email="trainer@example.com",
        password_hash="hashed",
        first_name="Train",
        last_name="Er",
        role=UserRole.TRAINER,
    )
    db.add(trainer)

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

    past_attended = Classes(
        trainer_id=trainer.id,
        description="Past attended",
        class_type=ClassType.GROUP,
        start_datetime=now - dt.timedelta(days=2),
        end_datetime=now - dt.timedelta(days=2, hours=-1),
    )
    past_not_attended = Classes(
        trainer_id=trainer.id,
        description="Past not attended",
        class_type=ClassType.GROUP,
        start_datetime=now - dt.timedelta(days=3),
        end_datetime=now - dt.timedelta(days=3, hours=-1),
    )
    future_class = Classes(
        trainer_id=trainer.id,
        description="Future",
        class_type=ClassType.GROUP,
        start_datetime=now + dt.timedelta(days=2),
        end_datetime=now + dt.timedelta(days=2, hours=1),
    )

    db.add_all([past_attended, past_not_attended, future_class])
    db.commit()

    db.add_all([
        ClassRegistrations(member_id=member.id, class_id=past_attended.id, attended=True),
        ClassRegistrations(member_id=member.id, class_id=past_not_attended.id, attended=False),
        ClassRegistrations(member_id=member.id, class_id=future_class.id, attended=False),
    ])
    db.commit()

    result = scheduling.get_user_dashboard(member.id)

    assert result["past_class_count"] == 1
    assert len(result["upcoming_sessions"]) == 1
    assert result["upcoming_sessions"][0].id == future_class.id


# -------------------------------------------------------
# TESTS FOR add_availability
# -------------------------------------------------------

def test_add_availability_creates_block(db):
    trainer = Trainers(
        email="t1@example.com",
        password_hash="hashed",
        first_name="T",
        last_name="One",
        role=UserRole.TRAINER,
    )
    db.add(trainer)
    db.commit()
    db.refresh(trainer)

    block = scheduling.add_availability(
        trainer_id=trainer.id,
        start_date=dt.date(2024, 1, 1),
        end_date=dt.date(2024, 1, 1),
        start_time=dt.time(9, 0),
        end_time=dt.time(11, 0),
    )

    assert block.id is not None
    assert block.trainer_id == trainer.id


def test_add_availability_rejects_overlap(db):
    trainer = Trainers(
        email="t2@example.com",
        password_hash="hashed",
        first_name="T",
        last_name="Two",
        role=UserRole.TRAINER,
    )
    db.add(trainer)
    db.commit()
    db.refresh(trainer)

    existing = TrainerAvailability(
        trainer_id=trainer.id,
        start_date=dt.date(2024, 1, 1),
        end_date=dt.date(2024, 1, 1),
        start_time=dt.time(9, 0),
        end_time=dt.time(11, 0),
    )
    db.add(existing)
    db.commit()

    with pytest.raises(ValueError):
        scheduling.add_availability(
            trainer_id=trainer.id,
            start_date=dt.date(2024, 1, 1),
            end_date=dt.date(2024, 1, 1),
            start_time=dt.time(10, 0),
            end_time=dt.time(12, 0),
        )


def test_add_availability_unknown_trainer_raises(db):
    with pytest.raises(ValueError):
        scheduling.add_availability(
            trainer_id=9999,
            start_date=dt.date(2024, 1, 1),
            end_date=dt.date(2024, 1, 1),
            start_time=dt.time(9, 0),
            end_time=dt.time(11, 0),
        )


# -------------------------------------------------------
# TESTS FOR get_trainer_schedule
# -------------------------------------------------------

def test_get_trainer_schedule_future_only(db):
    now = dt.datetime.now()

    trainer = Trainers(
        email="future@example.com",
        password_hash="hashed",
        first_name="Future",
        last_name="Test",
        role=UserRole.TRAINER,
    )
    db.add(trainer)
    db.commit()
    db.refresh(trainer)

    past = Classes(
        trainer_id=trainer.id,
        description="Past",
        class_type=ClassType.PT,
        start_datetime=now - dt.timedelta(days=1),
        end_datetime=now - dt.timedelta(days=1, hours=-1),
    )
    future1 = Classes(
        trainer_id=trainer.id,
        description="Future1",
        class_type=ClassType.PT,
        start_datetime=now + dt.timedelta(days=1),
        end_datetime=now + dt.timedelta(days=1, hours=1),
    )
    future2 = Classes(
        trainer_id=trainer.id,
        description="Future2",
        class_type=ClassType.PT,
        start_datetime=now + dt.timedelta(days=3),
        end_datetime=now + dt.timedelta(days=3, hours=1),
    )
    db.add_all([past, future1, future2])
    db.commit()

    result = scheduling.get_trainer_schedule(trainer.id)
    desc = [c.description for c in result]

    assert desc == ["Future1", "Future2"]


def test_get_trainer_schedule_unknown_trainer():
    with pytest.raises(ValueError):
        scheduling.get_trainer_schedule(trainer_id=9999)


# -------------------------------------------------------
# TESTS FOR get_available_rooms
# -------------------------------------------------------

def test_get_available_rooms_excludes_conflicted(db):
    room1 = Rooms(
        room_number="R1",
        capacity=20,
        room_type=RoomType.STUDIO,
    )
    room2 = Rooms(
        room_number="R2",
        capacity=15,
        room_type=RoomType.TRAINING_ROOM,
    )
    db.add_all([room1, room2])
    db.commit()
    db.refresh(room1)
    db.refresh(room2)

    booking = RoomAvailability(
        room_id=room1.id,
        start_date=dt.date(2024, 1, 1),
        end_date=dt.date(2024, 1, 1),
        start_time=dt.time(10, 0),
        end_time=dt.time(12, 0),
    )
    db.add(booking)
    db.commit()

    available = scheduling.get_available_rooms(
        start_date=dt.date(2024, 1, 1),
        end_date=dt.date(2024, 1, 1),
        start_time=dt.time(11, 0),
        end_time=dt.time(11, 30),
    )

    ids = {r.id for r in available}
    assert room2.id in ids
    assert room1.id not in ids

def test_get_available_rooms_no_conflicts_returns_all(db):
    room1 = Rooms(
        room_number="Y1",
        capacity=30,
        room_type=RoomType.STUDIO,
    )
    room2 = Rooms(
        room_number="W1",
        capacity=25,
        room_type=RoomType.TRAINING_ROOM,
    )
    db.add_all([room1, room2])
    db.commit()
    db.refresh(room1)
    db.refresh(room2)

    available = scheduling.get_available_rooms(
        start_date=dt.date(2024, 2, 1),
        end_date=dt.date(2024, 2, 1),
        start_time=dt.time(9, 0),
        end_time=dt.time(10, 0),
    )

    ids = {r.id for r in available}
    assert room1.id in ids
    assert room2.id in ids
