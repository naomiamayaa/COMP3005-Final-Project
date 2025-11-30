from datetime import datetime, date, time, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
#added
from sqlalchemy import select


# from models.database import SessionLocal

from models.models import (
    Members,
    Trainers,
    Admins,
    Users,
    TrainerAvailability,
    RoomAvailability,
    Rooms,
    Classes,
    ClassRegistrations,
    MemberGoals,
    HealthMetrics
)

# =========================================================
# 1. Show latest health stats, active goals, past class count, upcoming sessions
# =========================================================

def get_user_dashboard(db: Session, user_id: int):
    """
    Build a dashboard summary for a member.

    NOTE: db session must be created and managed by the caller.
    """

    # fetch the user for error handling / display
    user = db.query(Users).filter(Users.id == user_id).first()

    # get the latest health stats
    latest_health = (
        db.query(HealthMetrics)
        .filter(HealthMetrics.member_id == user_id)
        .order_by(HealthMetrics.date_recorded.desc())
        .first()
    )

    # get the goals for that user
    goals = (
        db.query(MemberGoals)
        .filter(MemberGoals.member_id == user_id)
        .all()
    )

    now = datetime.now()

    # get the class count of past attended classes
    past_class_count = (
        db.query(ClassRegistrations)
        .join(Classes, Classes.id == ClassRegistrations.class_id)
        .filter(
            ClassRegistrations.member_id == user_id,
            ClassRegistrations.attended == True,
            Classes.end_datetime < now,
        )
        .count()
    )

    # get the upcoming sessions
    upcoming_sessions = (
        db.query(Classes)
        .join(ClassRegistrations, Classes.id == ClassRegistrations.class_id)
        .filter(
            ClassRegistrations.member_id == user_id,
            Classes.start_datetime >= now,
        )
        .order_by(Classes.start_datetime.asc())
        .all()
    )

    return {
        "user": user,
        "latest_health": latest_health,
        "goals": goals,
        "past_class_count": past_class_count,
        "upcoming_sessions": upcoming_sessions,
    }


# =========================================================
# 2. Define time windows when trainer is available. Prevent overlap.
# =========================================================

def add_availability(
    db: Session,
    trainer_id: int,
    start_date: date,
    end_date: date,
    start_time: time,
    end_time: time,
):
    """
    Add a trainer availability block. Caller must manage the db session.
    """

    if start_time >= end_time:
        raise ValueError("Start time must be earlier than end time.")

    if start_date > end_date:
        raise ValueError("Start date must be on or before end date.")

    # check trainer exists
    trainer = (
        db.query(Trainers)
        .filter(Trainers.id == trainer_id)
        .one_or_none()
    )
    if trainer is None:
        raise ValueError(f"Trainer with id {trainer_id} does not exist.")

    # look at all existing availability blocks for that trainer that overlap this window
    conflict = (
        db.query(TrainerAvailability)
        .filter(TrainerAvailability.trainer_id == trainer_id)
        .filter(TrainerAvailability.start_date <= end_date)
        .filter(TrainerAvailability.end_date >= start_date)
        .filter(TrainerAvailability.start_time <= end_time)
        .filter(TrainerAvailability.end_time >= start_time)
        .first()
    )

    # if the new block overlaps any of them reject it
    if conflict is not None:
        raise ValueError(
            "New availability overlaps an existing availability block "
            f"(id={conflict.id})."
        )

    # save the new availability in the Trainer Availability table
    new_block = TrainerAvailability(
        trainer_id=trainer_id,
        start_date=start_date,
        end_date=end_date,
        start_time=start_time,
        end_time=end_time,
    )

    db.add(new_block)
    db.commit()
    db.refresh(new_block)

    return new_block

#added room availability function
def add_room_availability(
    db: Session,
    room_id: int,
    start_date: date,
    end_date: date,
    start_time: time,
    end_time: time,
):
    """
    Add an availability block for a room. Prevents overlap with existing blocks.
    Caller must manage the db session.
    """

    if start_time >= end_time:
        raise ValueError("Start time must be earlier than end time.")

    if start_date > end_date:
        raise ValueError("Start date must be on or before end date.")

    # check room exists
    room = db.query(Rooms).filter(Rooms.id == room_id).one_or_none()
    if room is None:
        raise ValueError(f"Room with id {room_id} does not exist.")

    # check for overlapping availability
    conflict = (
        db.query(RoomAvailability)
        .filter(RoomAvailability.room_id == room_id)
        .filter(RoomAvailability.start_date <= end_date)
        .filter(RoomAvailability.end_date >= start_date)
        .filter(RoomAvailability.start_time <= end_time)
        .filter(RoomAvailability.end_time >= start_time)
        .first()
    )

    if conflict is not None:
        raise ValueError(
            "New availability overlaps an existing availability block "
            f"(id={conflict.id})."
        )

    # create the new availability block
    new_block = RoomAvailability(
        room_id=room_id,
        start_date=start_date,
        end_date=end_date,
        start_time=start_time,
        end_time=end_time,
    )

    db.add(new_block)
    db.commit()
    db.refresh(new_block)

    return new_block


# =========================================================
# 3. See assigned PT sessions and classes (trainer schedule).
# =========================================================

def get_trainer_schedule(db: Session, trainer_id: int):
    """
    Return upcoming classes/sessions for a trainer.

    Caller must manage db session.
    """

    # check trainer exists
    trainer = (
        db.query(Trainers)
        .filter(Trainers.id == trainer_id)
        .one_or_none()
    )
    if trainer is None:
        raise ValueError(f"Trainer with id {trainer_id} does not exist.")

    now = datetime.now()

    trainers_classes = (
        db.query(Classes)
        .filter(Classes.trainer_id == trainer_id)
        .filter(Classes.end_datetime >= now)  # drop past classes
        .order_by(Classes.start_datetime.asc())
        .all()
    )

    return trainers_classes


# =========================================================
# 4. Assign rooms for sessions or classes. Prevent double-booking.
# =========================================================

def get_available_rooms(
    db: Session,
    start_date: date,
    end_date: date,
    start_time: time,
    end_time: time,
):
    """
    Return all rooms that are AVAILABLE in the given window
    (i.e., they have an availability block that fully covers that window).
    Caller must manage db session.
    """

    if start_time >= end_time:
        raise ValueError("Start time must be earlier than end time.")

    if start_date > end_date:
        raise ValueError("Start date must be on or before end date.")

    # Rooms that have at least one availability block covering the whole window
    available_rooms = (
        db.query(Rooms)
        .join(RoomAvailability, Rooms.id == RoomAvailability.room_id)
        .filter(RoomAvailability.start_date <= start_date)
        .filter(RoomAvailability.end_date >= end_date)
        .filter(RoomAvailability.start_time <= start_time)
        .filter(RoomAvailability.end_time >= end_time)
        .all()
    )

    return available_rooms