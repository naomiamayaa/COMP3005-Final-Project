import datetime
import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Enum,
    Float,
    Time,
    ForeignKey,
    Boolean,
    DateTime,
)
from sqlalchemy.orm import relationship
from .database import Base


# ===== Enums =====

class UserRole(enum.Enum):
    MEMBER = "member"
    TRAINER = "trainer"
    ADMIN = "admin"


class ClassType(enum.Enum):
    PT = "personal training session"
    GROUP = "group class"


class RoomType(enum.Enum):
    STUDIO = "studio"
    TRAINING_ROOM = "training room"


class MaintenanceStatus(enum.Enum):
    REPORTED = "reported"
    IN_PROGRESS = "in progress"
    FIXED = "completed"


class EquipmentStatus(enum.Enum):
    GOOD = "good condition"
    NEEDS_MAINTENANCE = "needs maintenance"
    OUT_OF_ORDER = "out of order"


class InstructorAssignment(enum.Enum):
    WEEKLY = "recurring"
    ONE_TIME = "single session"


class Sex(enum.Enum):
    FEMALE = "woman"
    MALE = "man"
    OTHER = "other"


# ===== Base Users table (single-table inheritance) =====

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=True)

    role = Column(Enum(UserRole, name="user_role_enum"), nullable=False)
    sex = Column(Enum(Sex, name="user_sex_enum"), nullable=True)

    __mapper_args__ = {
        "polymorphic_on": role,      # only polymorphic_on here
        # no polymorphic_identity on the base; subclasses define it
    }


# ===== Subclasses =====

class Members(Users):
    __mapper_args__ = {
        "polymorphic_identity": UserRole.MEMBER,
    }

    goals = relationship(
        "MemberGoals",
        back_populates="member",
        cascade="all, delete-orphan",
    )

    health_metrics = relationship(
        "HealthMetrics",
        back_populates="member",
        cascade="all, delete-orphan",
    )


class Trainers(Users):
    __mapper_args__ = {
        "polymorphic_identity": UserRole.TRAINER,
    }

    availability = relationship(
        "TrainerAvailability",
        back_populates="trainer",
        cascade="all, delete-orphan",
    )


class Admins(Users):
    __mapper_args__ = {
        "polymorphic_identity": UserRole.ADMIN,
    }


# ===== Member-related tables =====

class MemberGoals(Base):
    __tablename__ = "member_goals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    body_fat_percent = Column(Float, nullable=True)
    target_weight = Column(Float, nullable=True)

    member = relationship("Members", back_populates="goals")


class HealthMetrics(Base):
    __tablename__ = "health_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date_recorded = Column(DateTime(timezone=False), default=datetime.datetime.now, nullable=False)
    weight = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    bpm = Column(Integer, nullable=True)

    member = relationship("Members", back_populates="health_metrics")


# ===== Classes table =====

class Classes(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    trainer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    description = Column(String(1000), nullable=True)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)

    class_type = Column(
        Enum(ClassType, name="class_type_enum"),
        nullable=False,
    )

    trainer = relationship("Trainers", foreign_keys=[trainer_id])
    room = relationship("Rooms", backref="classes")

class ClassRegistrations(Base):
    __tablename__ = "class_registrations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    attended = Column(Boolean, default=False)  # or "status" enum

    member = relationship("Members", backref="class_registrations")
    gym_class = relationship("Classes", backref="registrations")

# ===== Rooms table =====

class Rooms(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_number = Column(String(50), unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)

    room_type = Column(
        Enum(RoomType, name="room_type_enum"),
        nullable=False,
    )

    # optional, but nice:
    availabilities = relationship(
        "RoomAvailability",
        back_populates="room",
        cascade="all, delete-orphan",
    )

    equipment = relationship(
        "Equipment",
        back_populates="room",
        cascade="all, delete-orphan",
    )


# ===== Availability tables =====

class TrainerAvailability(Base):
    __tablename__ = "trainer_availability"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trainer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    recurring = Column(Boolean, default=False)

    trainer = relationship("Trainers", back_populates="availability")


class RoomAvailability(Base):
    __tablename__ = "room_availability"

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    recurring = Column(Boolean, default=False)

    room = relationship("Rooms", back_populates="availabilities")


# ===== Equipment and Maintenance tables =====

class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    name = Column(String(255), nullable=False)

    status = Column(
        Enum(EquipmentStatus, name="equipment_status_enum"),
        nullable=False,
        default=EquipmentStatus.GOOD,
    )

    room = relationship("Rooms", back_populates="equipment")

    maintenance_records = relationship(
        "MaintenanceRecords",
        back_populates="equipment",
        cascade="all, delete-orphan",
    )


class MaintenanceRecords(Base):
    __tablename__ = "maintenance_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    report_date = Column(Date, nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)

    status = Column(
        Enum(MaintenanceStatus, name="maintenance_status_enum"),
        nullable=False,
        default=MaintenanceStatus.REPORTED,
    )

    description = Column(String(1000), nullable=True)

    equipment = relationship("Equipment", back_populates="maintenance_records")
