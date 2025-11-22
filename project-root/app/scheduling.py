from datetime import datetime, date, time, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.database import SessionLocal

from app.models import (
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

# Show latest health stats, active goals, past class count, upcoming sessions
def get_user_dashboard(user_id: int):
    with SessionLocal() as db:

        # fetch the user for error handling
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

# Define time windows when available for sessions or classes. Prevent overlap.
def add_availability(trainer_id: int, day_of_week: str, start_time: time, end_time: time):
    if start_time >= end_time:
            raise ValueError("Start time must be earlier than end time.")

    with SessionLocal() as db:
        # validate if trainer exists, is start time < end time? 
        trainer = (
            db.query(Trainers).filter(trainer_id == Trainers.)
        )

        # look at all existing availability blocks for that trainer on that day
        # if the new block overlaps any of them reject it
        # save the new availability in the Trainer Availability table 


# See assigned PT sessions and classes.
def get_trainer_schedule(trainer_id: int):
    return None

# Assign rooms for sessions or classes. Prevent double-booking.
def get_available_rooms(date: date, start_time: time, end_time: time):
    return None