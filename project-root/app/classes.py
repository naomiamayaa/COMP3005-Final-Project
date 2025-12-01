from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from models.models import (
    Users,
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
    
    # if the member is already registered in the group class selected (to avoid duplicates):
    alr_registered = db.query(ClassRegistrations).filter_by(class_id=class_id, member_id=member_id).first()
    if alr_registered:
        raise ValueError(f"Member is already registered for class id = {class_id}.")

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


# function called when admin wants to create a class, altered
def create_class(db: Session, trainer_id: int, room_id: int, start_datetime, class_type: ClassType):
    """
    Create a class after trainer and room have been selected from available options,
    and update trainer/room availability blocks.
    """
    end_datetime = start_datetime + timedelta(hours=1)

    # Verify trainer exists
    trainer = db.query(Trainers).filter_by(id=trainer_id).first()
    if not trainer:
        raise ValueError(f"Trainer {trainer_id} does not exist.")

    # Verify room exists
    room = db.query(Rooms).filter_by(id=room_id).first()
    if not room:
        raise ValueError(f"Room {room_id} does not exist.")

    # Check for conflicts again (safety)
    future_classes = get_trainer_schedule(db, trainer_id)
    for cls in future_classes:
        if cls.start_datetime < end_datetime and cls.end_datetime > start_datetime:
            raise ValueError("Trainer has another class at this time.")

    # CREATE THE CLASS
    new_class = Classes(
        trainer_id=trainer_id,
        room_id=room_id,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        class_type=class_type
    )
    db.add(new_class)

    # -------------------
    # Update Trainer Availability
    # -------------------
    trainer_block = db.query(TrainerAvailability).filter(
        TrainerAvailability.trainer_id == trainer_id,
        TrainerAvailability.start_date <= start_datetime.date(),
        TrainerAvailability.end_date >= start_datetime.date(),
        TrainerAvailability.start_time <= start_datetime.time(),
        TrainerAvailability.end_time >= end_datetime.time()
    ).first()

    if trainer_block:
        # Split before
        if trainer_block.start_time < start_datetime.time():
            trainer_before = TrainerAvailability(
                trainer_id=trainer_id,
                start_date=trainer_block.start_date,
                end_date=trainer_block.end_date,
                start_time=trainer_block.start_time,
                end_time=start_datetime.time(),
                recurring=trainer_block.recurring
            )
            db.add(trainer_before)
        # Split after
        if trainer_block.end_time > end_datetime.time():
            trainer_after = TrainerAvailability(
                trainer_id=trainer_id,
                start_date=trainer_block.start_date,
                end_date=trainer_block.end_date,
                start_time=end_datetime.time(),
                end_time=trainer_block.end_time,
                recurring=trainer_block.recurring
            )
            db.add(trainer_after)
        # Remove used block
        db.delete(trainer_block)

    # -------------------
    # Update Room Availability
    # -------------------
    room_block = db.query(RoomAvailability).filter(
        RoomAvailability.room_id == room_id,
        RoomAvailability.start_date <= start_datetime.date(),
        RoomAvailability.end_date >= start_datetime.date(),
        RoomAvailability.start_time <= start_datetime.time(),
        RoomAvailability.end_time >= end_datetime.time()
    ).first()

    if room_block:
        # Split before
        if room_block.start_time < start_datetime.time():
            room_before = RoomAvailability(
                room_id=room_id,
                start_date=room_block.start_date,
                end_date=room_block.end_date,
                start_time=room_block.start_time,
                end_time=start_datetime.time(),
                recurring=room_block.recurring
            )
            db.add(room_before)
        # Split after
        if room_block.end_time > end_datetime.time():
            room_after = RoomAvailability(
                room_id=room_id,
                start_date=room_block.start_date,
                end_date=room_block.end_date,
                start_time=end_datetime.time(),
                end_time=room_block.end_time,
                recurring=room_block.recurring
            )
            db.add(room_after)
        # Remove used block
        db.delete(room_block)

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
    List all classes (PT + group) with attendees, trainer name, and room number.
    """
    classes = (
        db.query(Classes)
        .options(
            joinedload(Classes.trainer),         # Trainer relationship
            joinedload(Classes.room),            # Room relationship
            joinedload(Classes.registrations)    # Registrations relationship
        )
        .order_by(Classes.start_datetime.asc())
        .all()
    )

    result = []
    for cls in classes:
        # Prepare attendees list
        attendees = [
            {"member_id": reg.member_id, "attended": reg.attended}
            for reg in cls.registrations
        ]

        # Trainer name
        trainer_name = f"{cls.trainer.first_name} {cls.trainer.last_name}" if cls.trainer else "Unknown"

        # Room number
        room_number = cls.room.room_number if cls.room else "Unknown"

        result.append({
            "class_id": cls.id,
            "class_type": cls.class_type.value,
            "start_datetime": cls.start_datetime,
            "end_datetime": cls.end_datetime,
            "trainer_name": trainer_name,
            "room_number": room_number,
            "attendees": attendees
        })

    return result


# count past group classes attended by a specific member id, returns int
def count_past_classes(db, member_id: int):
    
    now = datetime.now()
    return (
        db.query(ClassRegistrations)
        .join(Classes)
        .filter(
            ClassRegistrations.member_id == member_id,
            ClassRegistrations.attended == True,
            Classes.class_type == ClassType.GROUP,
            Classes.end_datetime < now
        )
        .count()
    )

def print_upcoming_pt_sessions(db, member_id: int):

    now = datetime.now()

    # query PT sessions booked by this member that are in the future
    sessions = (
        db.query(Classes)
        .join(ClassRegistrations, ClassRegistrations.class_id == Classes.id)
        .join(Users, Classes.trainer_id == Users.id)  # get trainer info
        .filter(
            Classes.class_type == ClassType.PT,
            ClassRegistrations.member_id == member_id,
            Classes.start_datetime > now
        )
        .order_by(Classes.start_datetime.asc())
        .all()
    )

    if not sessions:
        print("No upcoming PT sessions booked.")
        return

    print("Upcoming PT Sessions:")
    for session in sessions:
        trainer_name = f"{session.trainer.first_name} {session.trainer.last_name}"
        print(f" class id: {session.id} - {session.start_datetime.strftime('%Y-%m-%d %H:%M')} with {trainer_name}")


def print_upcoming_group_sessions(db, member_id: int):

    now = datetime.now()

    # query g sessions booked by this member that are in the future
    sessions = (
        db.query(Classes)
        .join(ClassRegistrations, ClassRegistrations.class_id == Classes.id)
        .join(Users, Classes.trainer_id == Users.id)  # get trainer info
        .filter(
            Classes.class_type == ClassType.GROUP,
            ClassRegistrations.member_id == member_id,
            Classes.start_datetime > now
        )
        .order_by(Classes.start_datetime.asc())
        .all()
    )

    if not sessions:
        print("No upcoming group sessions booked.")
        return

    print("Upcoming Group Sessions:")
    for session in sessions:
        trainer_name = f"{session.trainer.first_name} {session.trainer.last_name}"
        print(f" class id: {session.id} - {session.start_datetime.strftime('%Y-%m-%d %H:%M')} with {trainer_name}")


# Displays available PT sessions that are not booked yet.
def print_available_PT_sessions(db):
    
    now = datetime.now()

    # Query available PT sessions

    print("------------------------------------")
    print(" upcoming PT classes open for registration:   ")
    print("------------------------------------")

    available_sessions = (
        db.query(Classes).filter(

            Classes.class_type == ClassType.PT,
            Classes.start_datetime > now  # future sessions only

        )
        .outerjoin(ClassRegistrations, Classes.id == ClassRegistrations.class_id)
        .filter(ClassRegistrations.id == None)  # not booked
        .order_by(Classes.start_datetime.asc())
        .all()
    )

    if not available_sessions:
        print("no available PT sessions at the moment, sorry.")
        return None

    print("Available PT sessions:")
    for session in available_sessions:
        trainer_name = f"{session.trainer.first_name} {session.trainer.last_name}"
        print(f" class id: {session.id} start time: {session.start_datetime.strftime('%Y-%m-%d %H:%M')} with {trainer_name}")

    return available_sessions



# count past group classes attended by a specific member id, returns int
def count_past_classes(db, member_id: int):
    
    now = datetime.now()
    return (
        db.query(ClassRegistrations)
        .join(Classes)
        .filter(
            ClassRegistrations.member_id == member_id,
            ClassRegistrations.attended == True,
            Classes.class_type == ClassType.GROUP,
            Classes.end_datetime < now
        )
        .count()
    )

def print_upcoming_pt_sessions(db, member_id: int):

    now = datetime.now()

    # query PT sessions booked by this member that are in the future
    sessions = (
        db.query(Classes)
        .join(ClassRegistrations, ClassRegistrations.class_id == Classes.id)
        .join(Users, Classes.trainer_id == Users.id)  # get trainer info
        .filter(
            Classes.class_type == ClassType.PT,
            ClassRegistrations.member_id == member_id,
            Classes.start_datetime > now
        )
        .order_by(Classes.start_datetime.asc())
        .all()
    )

    if not sessions:
        print("No upcoming PT sessions booked.")
        return

    print("Upcoming PT Sessions:")
    for session in sessions:
        trainer_name = f"{session.trainer.first_name} {session.trainer.last_name}"
        print(f" class id: {session.id} - {session.start_datetime.strftime('%Y-%m-%d %H:%M')} with {trainer_name}")


def print_upcoming_group_sessions(db, member_id: int):

    now = datetime.now()

    # query g sessions booked by this member that are in the future
    sessions = (
        db.query(Classes)
        .join(ClassRegistrations, ClassRegistrations.class_id == Classes.id)
        .join(Users, Classes.trainer_id == Users.id)  # get trainer info
        .filter(
            Classes.class_type == ClassType.GROUP,
            ClassRegistrations.member_id == member_id,
            Classes.start_datetime > now
        )
        .order_by(Classes.start_datetime.asc())
        .all()
    )

    if not sessions:
        print("No upcoming group sessions booked.")
        return

    print("Upcoming Group Sessions:")
    for session in sessions:
        trainer_name = f"{session.trainer.first_name} {session.trainer.last_name}"
        print(f" class id: {session.id} - {session.start_datetime.strftime('%Y-%m-%d %H:%M')} with {trainer_name}")


# Displays available PT sessions that are not booked yet.
def print_available_PT_sessions(db):
    
    now = datetime.now()

    # Query available PT sessions

    print("------------------------------------")
    print(" upcoming PT classes open for registration:   ")
    print("------------------------------------")

    available_sessions = (
        db.query(Classes).filter(

            Classes.class_type == ClassType.PT,
            Classes.start_datetime > now  # future sessions only

        )
        .outerjoin(ClassRegistrations, Classes.id == ClassRegistrations.class_id)
        .filter(ClassRegistrations.id == None)  # not booked
        .order_by(Classes.start_datetime.asc())
        .all()
    )

    if not available_sessions:
        print("no available PT sessions at the moment, sorry.")
        return None

    print("Available PT sessions:")
    for session in available_sessions:
        trainer_name = f"{session.trainer.first_name} {session.trainer.last_name}"
        print(f" class id: {session.id} start time: {session.start_datetime.strftime('%Y-%m-%d %H:%M')} with {trainer_name}")

    return available_sessions


#added functions
def show_trainer_availability(session):
    """List all trainers with their available time blocks"""
    trainers = session.query(Trainers).all()
    for t in trainers:
        print(f"\nTrainer {t.id}: {t.first_name} {t.last_name}")
        blocks = session.query(TrainerAvailability).filter_by(trainer_id=t.id).all()
        if not blocks:
            print("  No availability blocks.")
        else:
            for b in blocks:
                print(f"  {b.start_date} {b.start_time} - {b.end_date} {b.end_time}")

def show_room_availability(session):
    """List all rooms with their available time blocks"""
    rooms = session.query(Rooms).all()
    for r in rooms:
        print(f"\nRoom {r.id}: {r.room_number} (Capacity {r.capacity})")
        blocks = session.query(RoomAvailability).filter_by(room_id=r.id).all()
        if not blocks:
            print("  No availability blocks.")
        else:
            for b in blocks:
                print(f"  {b.start_date} {b.start_time} - {b.end_date} {b.end_time}")



def get_available_trainers_and_rooms(db: Session, start_datetime, duration_hours=1):
    """
    Return available trainers and rooms for a given datetime and duration.
    """
    end_datetime = start_datetime + timedelta(hours=duration_hours)

    # Available trainers: check trainer availability and conflicts
    all_trainers = db.query(Trainers).all()
    available_trainers = []

    for trainer in all_trainers:
        # Check if trainer has an availability block that covers this time
        avail_block = db.query(TrainerAvailability).filter(
            TrainerAvailability.trainer_id == trainer.id,
            TrainerAvailability.start_date <= start_datetime.date(),
            TrainerAvailability.end_date >= start_datetime.date(),
            TrainerAvailability.start_time <= start_datetime.time(),
            TrainerAvailability.end_time >= end_datetime.time()
        ).first()

        if not avail_block:
            continue  # trainer unavailable

        # Check if trainer has any conflicting classes
        future_classes = get_trainer_schedule(db, trainer.id)
        conflict = False
        for cls in future_classes:
            if cls.start_datetime < end_datetime and cls.end_datetime > start_datetime:
                conflict = True
                break
        if not conflict:
            available_trainers.append(trainer)

    # Available rooms: use the existing get_available_rooms function
    available_rooms = get_available_rooms(
        db=db,
        start_date=start_datetime.date(),
        end_date=start_datetime.date(),
        start_time=start_datetime.time(),
        end_time=end_datetime.time()
    )

    return available_trainers, available_rooms