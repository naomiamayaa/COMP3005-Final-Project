from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from models.models import (
    Classes,
    ClassRegistrations,
    ClassType,
    Rooms,
    Trainers,
    Members,
    RoomAvailability,
    TrainerAvailability,  # needed for create_class
)

# importing functions for availability checks
from app.scheduling import get_trainer_schedule, get_available_rooms  

def book_pt_session(db: Session, member_id: int, class_id: int):
    """
    Book a personal training (PT) session for a member.
    Caller must manage the db session.
    """
    # Validate member
    member = db.query(Members).filter_by(id=member_id).first()
    if not member:
        raise ValueError(f"Member {member_id} does not exist.")

    # Validate class
    pt_session = db.query(Classes).filter_by(id=class_id).first()
    if not pt_session:
        raise ValueError(f"Session {class_id} does not exist.")

    # Must be a PT session
    if pt_session.class_type != ClassType.PT:
        raise ValueError("This is not a PT session.")

    # Ensure only one member can book it
    existing = db.query(ClassRegistrations).filter_by(class_id=class_id).first()
    if existing:
        raise ValueError("This PT session is already booked.")

    # Register the member
    new_registration = ClassRegistrations(
        member_id=member_id,
        class_id=class_id
    )
    db.add(new_registration)
    db.commit()
    db.refresh(new_registration)

    return new_registration


def cancel_booking(db: Session, member_id: int, class_id: int):
    """
    Cancel a member's booking for a given class.
    Caller must manage the db session.
    """
    registration = db.query(ClassRegistrations).filter_by(
        member_id=member_id,
        class_id=class_id
    ).first()

    if not registration:
        raise ValueError("This member is not registered for the class.")

    db.delete(registration)
    db.commit()

    return True


def register_for_group_class(db: Session, member_id: int, class_id: int):
    """
    Register a member for a group class.
    Caller must manage the db session.
    """
    member = db.query(Members).filter_by(id=member_id).first()
    gym_class = db.query(Classes).filter_by(id=class_id).first()

    if not member:
        raise ValueError(f"Member {member_id} does not exist.")
    if not gym_class:
        raise ValueError(f"Class {class_id} does not exist.")

    # Must be group class
    if gym_class.class_type != ClassType.GROUP:
        raise ValueError("This is not a group class.")

    # Check room capacity
    current_count = db.query(ClassRegistrations).filter_by(class_id=class_id).count()
    if current_count >= gym_class.room.capacity:
        raise ValueError("Class is full.")

    # Register member
    registration = ClassRegistrations(
        member_id=member_id,
        class_id=class_id
    )

    db.add(registration)
    db.commit()
    db.refresh(registration)

    return registration


# function called when admin wants to create a class
def create_class(
    db: Session,
    trainer_id: int,
    room_id: int,
    start_datetime,
    class_type: ClassType,
):
    """
    Create a class (PT or group), enforcing trainer/room availability and
    updating availability blocks. Caller must manage db session.
    """

    # Compute end time automatically (1-hour slot)
    end_datetime = start_datetime + timedelta(hours=1)

    # Check trainer exists
    trainer = db.query(Trainers).filter_by(id=trainer_id).first()
    if not trainer:
        raise ValueError(f"Trainer {trainer_id} does not exist.")

    # Check room exists
    room = db.query(Rooms).filter_by(id=room_id).first()
    if not room:
        raise ValueError(f"Room {room_id} does not exist.")

    # Trainer conflict check via schedule
    future_classes = get_trainer_schedule(db, trainer_id)
    for cls in future_classes:
        if cls.start_datetime < end_datetime and cls.end_datetime > start_datetime:
            raise ValueError("Trainer has another class at this time.")

    # Room availability check
    available_rooms = get_available_rooms(
        db=db,
        start_date=start_datetime.date(),
        end_date=start_datetime.date(),
        start_time=start_datetime.time(),
        end_time=end_datetime.time()
    )

    if room_id not in [r.id for r in available_rooms]:
        raise ValueError("Room is unavailable at this time.")

    # Trainer availability block that covers this class
    trainer_available = (
        db.query(TrainerAvailability)
        .filter(
            TrainerAvailability.trainer_id == trainer_id,
            TrainerAvailability.start_date <= start_datetime.date(),
            TrainerAvailability.end_date >= start_datetime.date(),
            TrainerAvailability.start_time <= start_datetime.time(),
            TrainerAvailability.end_time >= end_datetime.time()
        )
        .first()
    )
    if not trainer_available:
        raise ValueError("Trainer is unavailable at this time.")

    # CREATE THE CLASS
    new_class = Classes(
        trainer_id=trainer_id,
        room_id=room_id,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        class_type=class_type
    )
    db.add(new_class)

    # Update trainer availability (split around the booked slot if needed)
    if trainer_available:
        if trainer_available.start_time < start_datetime.time():
            trainer_before = TrainerAvailability(
                trainer_id=trainer_id,
                start_date=trainer_available.start_date,
                end_date=trainer_available.end_date,
                start_time=trainer_available.start_time,
                end_time=start_datetime.time(),
                recurring=trainer_available.recurring
            )
            db.add(trainer_before)

        if trainer_available.end_time > end_datetime.time():
            trainer_after = TrainerAvailability(
                trainer_id=trainer_id,
                start_date=trainer_available.start_date,
                end_date=trainer_available.end_date,
                start_time=end_datetime.time(),
                end_time=trainer_available.end_time,
                recurring=trainer_available.recurring
            )
            db.add(trainer_after)

        db.delete(trainer_available)

    # Update room availability similarly
    room_available = db.query(RoomAvailability).filter(
        RoomAvailability.room_id == room_id,
        RoomAvailability.start_date <= start_datetime.date(),
        RoomAvailability.end_date >= start_datetime.date(),
        RoomAvailability.start_time <= start_datetime.time(),
        RoomAvailability.end_time >= end_datetime.time()
    ).first()

    if room_available:
        if room_available.start_time < start_datetime.time():
            room_before = RoomAvailability(
                room_id=room_id,
                start_date=room_available.start_date,
                end_date=room_available.end_date,
                start_time=room_available.start_time,
                end_time=start_datetime.time(),
                recurring=room_available.recurring
            )
            db.add(room_before)
        if room_available.end_time > end_datetime.time():
            room_after = RoomAvailability(
                room_id=room_id,
                start_date=room_available.start_date,
                end_date=room_available.end_date,
                start_time=end_datetime.time(),
                end_time=room_available.end_time,
                recurring=room_available.recurring
            )
            db.add(room_after)
        db.delete(room_available)

    db.commit()
    db.refresh(new_class)

    return new_class


# admin function to update class details
def update_class(
    db: Session,
    class_id: int,
    trainer_id: int,
    room_id: int,
    start_datetime: datetime,
    end_datetime: datetime,
    class_type: ClassType
):
    """
    Update class details (trainer, room, times, type).
    Caller must manage db session.
    """
    cls = db.query(Classes).filter_by(id=class_id).first()
    if not cls:
        raise ValueError(f"Class {class_id} not found.")

    # TRAINER CHECK
    trainer_conflict = db.query(Classes).filter(
        Classes.trainer_id == trainer_id,
        Classes.id != class_id,
        Classes.start_datetime < end_datetime,
        Classes.end_datetime > start_datetime
    ).first()
    if trainer_conflict:
        raise ValueError("Trainer has another class at this time.")

    # ROOM CHECK
    room_conflict = db.query(Classes).filter(
        Classes.room_id == room_id,
        Classes.id != class_id,
        Classes.start_datetime < end_datetime,
        Classes.end_datetime > start_datetime
    ).first()
    if room_conflict:
        raise ValueError("Room has another class at this time.")

    # APPLY UPDATES
    cls.trainer_id = trainer_id
    cls.room_id = room_id
    cls.start_datetime = start_datetime
    cls.end_datetime = end_datetime
    cls.class_type = class_type

    db.commit()
    db.refresh(cls)

    return cls


def list_group_classes(db: Session):
    """
    List all group classes with their attendees.
    Caller must manage db session.
    """
    classes = (
        db.query(Classes)
        .filter(Classes.class_type == ClassType.GROUP)
        .order_by(Classes.start_datetime.asc())
        .all()
    )

    result = []
    for cls in classes:
        attendees = [
            {"member_id": reg.member_id, "attended": reg.attended}
            for reg in cls.registrations
        ]
        result.append({
            "class_id": cls.id,
            "trainer_id": cls.trainer_id,
            "room_id": cls.room_id,
            "start_datetime": cls.start_datetime,
            "end_datetime": cls.end_datetime,
            "class_type": cls.class_type.value,
            "attendees": attendees
        })
    return result


def list_pt_sessions(db: Session):
    """
    List all PT sessions with who booked them (if any).
    Caller must manage db session.
    """
    sessions = (
        db.query(Classes)
        .filter(Classes.class_type == ClassType.PT)
        .order_by(Classes.start_datetime.asc())
        .all()
    )

    result = []
    for session in sessions:
        # PT sessions can only have 0 or 1 member
        attendee = session.registrations[0].member_id if session.registrations else None
        result.append({
            "session_id": session.id,
            "trainer_id": session.trainer_id,
            "room_id": session.room_id,
            "start_datetime": session.start_datetime,
            "end_datetime": session.end_datetime,
            "class_type": session.class_type.value,
            "booked_by_member_id": attendee
        })
    return result


def list_classes(db: Session):
    """
    List all classes (PT + group) with attendees.
    Caller must manage db session.
    """
    classes = (
        db.query(Classes)
        .order_by(Classes.start_datetime.asc())
        .all()
    )

    result = []
    for cls in classes:
        attendees = [
            {"member_id": reg.member_id, "attended": reg.attended}
            for reg in cls.registrations
        ]

        result.append({
            "class_id": cls.id,
            "trainer_id": cls.trainer_id,
            "room_id": cls.room_id,
            "start_datetime": cls.start_datetime,
            "end_datetime": cls.end_datetime,
            "class_type": cls.class_type.value,
            "attendees": attendees
        })

    return result
