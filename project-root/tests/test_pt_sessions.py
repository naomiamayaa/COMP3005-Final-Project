"""
Extended Test Script — now with full table reset + automatic seeding before tests.
Uses the updated classes.py API (db passed explicitly) and an in-memory SQLite DB.
"""

from datetime import datetime, timedelta
import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, date, time


# -------------------------------------------------------------------
# Ensure project root is on sys.path so `import app...` works
# -------------------------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from models.database import Base
from models.models import (
    Members,
    Trainers,
    Rooms,
    Users,
    MemberGoals,
    HealthMetrics,
    ClassRegistrations,
    Classes,
    TrainerAvailability,
    RoomAvailability,
    Equipment,
    MaintenanceRecords,
    ClassType,
)
from app.classes import (
    create_class,
    list_classes,
    register_for_group_class,
    book_pt_session,
    cancel_booking,
    update_class,
)
from app.populate_tables import seed

# -------------------------------------------------------------------
# Test DB setup: in-memory SQLite, just like test_scheduling.py
# -------------------------------------------------------------------
engine = create_engine("sqlite:///:memory:", future=True)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Override SessionLocal for this script
SessionLocal = TestingSessionLocal

# Create all tables in the SQLite DB
Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------
# Utility
# ---------------------------------------------------------

def print_header(title):
    print("\n" + "=" * 60)
    print(">>> " + title)
    print("=" * 60 + "\n")


# ---------------------------------------------------------
# CLEAR ALL TABLES
# ---------------------------------------------------------

def clear_all_tables():
    print_header("RESETTING DATABASE TABLES")

    with SessionLocal() as db:
        # Child tables first
        db.query(ClassRegistrations).delete()
        db.query(RoomAvailability).delete()
        db.query(TrainerAvailability).delete()
        db.query(MaintenanceRecords).delete()
        db.query(Equipment).delete()
        db.query(Classes).delete()
        db.query(MemberGoals).delete()
        db.query(HealthMetrics).delete()

        # Rooms
        db.query(Rooms).delete()

        # Users last
        db.query(Users).delete()

        db.commit()

    print("✔ All tables cleared.\n")


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def pick_existing_ids():
    """Fetch one trainer, one room, and one member from DB."""
    with SessionLocal() as db:
        trainer = db.query(Trainers).first()
        room = db.query(Rooms).first()
        member = db.query(Members).first()

        if not trainer or not room or not member:
            raise ValueError("DB must have at least 1 trainer, 1 room, and 1 member.")

        return trainer.id, room.id, member.id


def pick_second_member():
    """Get a second member (for PT double-book test)."""
    with SessionLocal() as db:
        members = db.query(Members).order_by(Members.id.asc()).all()
        if len(members) < 2:
            raise ValueError("DB must have at least 2 members for this test.")
        return members[1].id  # second member


# ---------------------------------------------------------
# Group Class Tests
# ---------------------------------------------------------

def test_class_creation():
    print_header("TEST: CREATE GROUP CLASS")

    trainer_id, room_id, member_id = pick_existing_ids()

    # Schedule for tomorrow at 10:00, which is safely within 09:00–17:00
    start_date = date.today() + timedelta(days=1)
    start = datetime.combine(start_date, time(10, 0))

    with SessionLocal() as db:
        new_class = create_class(
            db=db,
            trainer_id=trainer_id,
            room_id=room_id,
            start_datetime=start,
            class_type=ClassType.GROUP,
        )
        new_class.description = "YOGA"
        db.commit()
        class_id = new_class.id   # 👈 grab primitive before session closes

    print(f"✔ Group class created (ID {class_id})")
    return class_id, member_id



def test_registration(class_id, member_id):
    print_header("TEST: REGISTER MEMBER FOR GROUP CLASS")

    with SessionLocal() as db:
        reg = register_for_group_class(
            db=db,
            member_id=member_id,
            class_id=class_id,
        )

    print(f"✔ Member registered (Registration ID {reg.id})")


def test_list_classes():
    print_header("TEST: LIST CLASSES")

    with SessionLocal() as db:
        classes = list_classes(db)

    for cls in classes:
        print(f"\nClass {cls['class_id']} — {cls['class_type']}")
        for attendee in cls["attendees"]:
            print(
                f"   Member {attendee['member_id']} — Attended? {attendee['attended']}"
            )

    print("\n✔ Listing complete.")


# ---------------------------------------------------------
# PT Session Tests (using create_class + book_pt_session + update_class + cancel_booking)
# ---------------------------------------------------------

def test_schedule_pt_session():
    print_header("TEST: SCHEDULE PT SESSION (CREATE PT CLASS + BOOK)")

    trainer_id, room_id, member_id = pick_existing_ids()

    # Two days from now at 11:00, also within 09:00–17:00
    start_date = date.today() + timedelta(days=2)
    start = datetime.combine(start_date, time(11, 0))

    with SessionLocal() as db:
        pt_class = create_class(
            db=db,
            trainer_id=trainer_id,
            room_id=room_id,
            start_datetime=start,
            class_type=ClassType.PT,
        )

        booking = book_pt_session(
            db=db,
            member_id=member_id,
            class_id=pt_class.id,
        )

        pt_class_id = pt_class.id         # 👈 extract IDs in-session
        booking_id = booking.id

    print(f"✔ PT class created (ID {pt_class_id}) and booked (Registration ID {booking_id})")
    return pt_class_id, trainer_id, room_id, member_id



def test_pt_conflict_double_booking(pt_class_id):
    """
    Try to double-book the same PT class with a second member – should fail.
    """
    print_header("TEST: DOUBLE-BOOK PT SESSION (expect failure)")

    second_member_id = pick_second_member()

    try:
        with SessionLocal() as db:
            book_pt_session(
                db=db,
                member_id=second_member_id,
                class_id=pt_class_id,
            )
        print("✘ ERROR — PT double-booking NOT detected!")
    except Exception as e:
        print("✔ PT double-booking correctly rejected:")
        print("  ", e)


def test_reschedule_pt_session(pt_class_id, trainer_id, room_id):
    """
    Use update_class to reschedule a PT session to a new time.
    """
    print_header("TEST: RESCHEDULE PT SESSION (via update_class)")

    new_start = datetime.now() + timedelta(hours=5)
    new_end = new_start + timedelta(hours=1)

    with SessionLocal() as db:
        session = update_class(
            db=db,
            class_id=pt_class_id,
            trainer_id=trainer_id,
            room_id=room_id,
            start_datetime=new_start,
            end_datetime=new_end,
            class_type=ClassType.PT,
        )

    print(f"✔ PT session rescheduled to {session.start_datetime}")


def test_cancel_pt_session(pt_class_id, member_id):
    """
    Cancel a PT booking (not deleting the class itself).
    """
    print_header("TEST: CANCEL PT SESSION BOOKING")

    with SessionLocal() as db:
        cancel_booking(
            db=db,
            member_id=member_id,
            class_id=pt_class_id,
        )

    print("✔ PT session booking cancelled")


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():
    print_header("STARTING TESTER")

    # 1. Reset DB
    clear_all_tables()

    # 2. Seed DB
    print_header("SEEDING DATABASE")
    with SessionLocal() as db:
        seed(db)

    # 3. Group Class Tests
    cls_id, member_id = test_class_creation()
    test_registration(cls_id, member_id)
    test_list_classes()

    # 4. PT Session Tests
    pt_id, trainer_id, room_id, member_id = test_schedule_pt_session()
    test_pt_conflict_double_booking(pt_id)
    test_reschedule_pt_session(pt_id, trainer_id, room_id)
    test_cancel_pt_session(pt_id, member_id)

    print_header("TESTING COMPLETE")


if __name__ == "__main__":
    main()
