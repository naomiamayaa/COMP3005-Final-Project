# app/models.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Enum,
    Float,
    Time,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from .database import Base
import enum

# Enums 
class UserRole(enum.Enum):
    MEMBER = "member"
    TRAINER = "trainer"
    ADMIN = "admin"

class classType(enum.Enum):
    PT = "personal training session"
    GROUP = "group class"

class roomType(enum.Enum):
    STUDIO = "studio"
    TRAINING_ROOM = "Training Room"

class maintenanceStatus(enum.Enum):
    REPORTED = "reported"
    IN_PROGRESS = "in progress"
    FIXED = "completed"

class instructorAssignment(enum.Enum):
    WEEKLY = "recurring"
    ONE_TIME = "single session"