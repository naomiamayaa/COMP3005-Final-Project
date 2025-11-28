from datetime import date, datetime, time, timedelta
from sqlalchemy.orm import Session

from models.database import Base, engine
from models.models import (
    Users, Members, Trainers, Admins,
    Rooms, Classes, ClassRegistrations,
    Equipment, MaintenanceRecords,
    TrainerAvailability, RoomAvailability,
    MemberGoals, HealthMetrics,
    UserRole, ClassType, RoomType, EquipmentStatus, MaintenanceStatus, Sex
)


def seed(db: Session):
    # ===== Users =====
    member1 = Members(
        email="member1@example.com",
        password_hash="hashedpassword",
        first_name="Alice",
        last_name="Smith",
        date_of_birth=date(1990, 5, 15),
        role=UserRole.MEMBER,
        sex=Sex.FEMALE,
    )

    member2 = Members(
        email="member2@example.com",
        password_hash="hashedpassword",
        first_name="Bob",
        last_name="Johnson",
        date_of_birth=date(1985, 8, 22),
        role=UserRole.MEMBER,
        sex=Sex.MALE,
    )

    trainer1 = Trainers(
        email="trainer1@example.com",
        password_hash="hashedpassword",
        first_name="Charlie",
        last_name="Brown",
        role=UserRole.TRAINER,
        sex=Sex.MALE,
    )

    admin1 = Admins(
        email="admin1@example.com",
        password_hash="hashedpassword",
        first_name="Dana",
        last_name="White",
        role=UserRole.ADMIN,
        sex=Sex.OTHER,
    )

    db.add_all([member1, member2, trainer1, admin1])
    db.commit()

    # ===== Rooms =====
    room1 = Rooms(room_number="101", capacity=10, room_type=RoomType.STUDIO)
    room2 = Rooms(room_number="102", capacity=5, room_type=RoomType.TRAINING_ROOM)

    db.add_all([room1, room2])
    db.commit()

    # ===== Trainer Availability =====
    availability1 = TrainerAvailability(
        trainer_id=trainer1.id,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=7),
        start_time=time(9, 0),
        end_time=time(17, 0),
        recurring=True,
    )
    db.add(availability1)
    db.commit()

    # ===== Classes =====
    class1 = Classes(
        room_id=room1.id,
        trainer_id=trainer1.id,
        start_datetime=datetime.now() + timedelta(days=1, hours=1),
        end_datetime=datetime.now() + timedelta(days=1, hours=2),
        class_type=ClassType.GROUP,
        description="Morning Yoga",
    )

    class2 = Classes(
        room_id=room2.id,
        trainer_id=trainer1.id,
        start_datetime=datetime.now() + timedelta(days=2, hours=10),
        end_datetime=datetime.now() + timedelta(days=2, hours=11),
        class_type=ClassType.PT,
        description="Personal Training Session",
    )

    db.add_all([class1, class2])
    db.commit()

    # ===== Class Registrations =====
    reg1 = ClassRegistrations(member_id=member1.id, class_id=class1.id, attended=False)
    reg2 = ClassRegistrations(member_id=member2.id, class_id=class1.id, attended=False)

    db.add_all([reg1, reg2])
    db.commit()

    # ===== Member Goals =====
    goal1 = MemberGoals(
        member_id=member1.id,
        body_fat_percent=25.0,
        target_weight=65.0,
    )
    goal2 = MemberGoals(
        member_id=member2.id,
        body_fat_percent=30.0,
        target_weight=75.0,
    )

    db.add_all([goal1, goal2])
    db.commit()


    # ===== Health Metrics =====
    metric1 = HealthMetrics(
        member_id=member1.id,
        date_recorded=date.today(),
        weight=70,
        height=165,
        bpm=70,
    )
    metric2 = HealthMetrics(
        member_id=member2.id,
        date_recorded=date.today(),
        weight=80,
        height=175,
        bpm=72,
    )

    db.add_all([metric1, metric2])
    db.commit()

    # ===== Equipment =====
    eq1 = Equipment(room_id=room1.id, name="Treadmill", status=EquipmentStatus.GOOD)
    eq2 = Equipment(
        room_id=room2.id, name="Dumbbells", status=EquipmentStatus.NEEDS_MAINTENANCE
    )

    db.add_all([eq1, eq2])
    db.commit()

    # ===== Maintenance Records =====
    maint1 = MaintenanceRecords(
        equipment_id=eq2.id,
        report_date=date.today(),
        status=MaintenanceStatus.REPORTED,
        description="Broken handle on dumbbell",
        assigned_to=admin1.id,
    )

    db.add(maint1)
    db.commit()

    print("Database seeded successfully!")


if __name__ == "__main__":
    # Optional: allow direct `python -m app.populate_tables` usage with real engine
    from models.database import SessionLocal

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed(db)
