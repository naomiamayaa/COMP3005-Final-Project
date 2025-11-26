from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv

import os
import sys
import pytest

# Add project-root (one level up from tests/) to sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.users import add_user, update_user, delete_user, get_user_by_id, get_all_users
from app.member_goals import add_member_goals, update_member_goals, get_member_goals, get_all_member_goals, delete_member_goal, delete_all_member_goals           
from app.health_metrics import add_health_metric, get_health_metrics, delete_health_metric
from app.member_lookup import allow_lookup_member, lookup_member
from app.models import Rooms, RoomType



from app.database import Base
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

load_dotenv()
DATABASE_URL = (
    f"postgresql+psycopg://{os.getenv('PGUSER')}:{os.getenv('PGPASSWORD')}"
    f"@{os.getenv('PGHOST')}:{os.getenv('PGPORT')}/{os.getenv('PGDATABASE')}"
)

engine = create_engine(DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

#------------------ Fixtures -----------------

@pytest.fixture
def db():
    """Provide a fresh DB session for each test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture(autouse=True)
def setup_test_db():
    """Create all tables before each test and drop them after."""
    Base.metadata.create_all(bind=engine)

    yield
    Base.metadata.drop_all(bind=engine)

def create_admin_user(db):
    admin = add_user(
        db,
        email_input="test52@example.com",
        password="hashed",
        first_name="Health",
        sex_input="other",
        last_name="User",
        date_of_birth="2003-07-07",
        role_input="admin", 
    )
    return admin

def create_member_user(db):
    member = add_user(
        db,
        email_input="test5@example.com",
        password="hashed",
        first_name="Health",
        sex_input="other",
        last_name="User",
        date_of_birth="2003-07-07",
        role_input="member", 
    )
    return member

def create_trainer_user(db):
    trainer = add_user(

        db,
        email_input="test15@example.com",
        password="hashed",
        first_name="Health",
        sex_input="other",
        last_name="User",
        date_of_birth="2003-07-07",
        role_input="trainer", 
    )
    return trainer

def create_class(db, trainer_id, room_id):

    new_class = Classes(

        room_id = room_id,
        trainer_id = trainer_id,
        class_type = ClassType.PT,
        description = "Test Class",
        start_datetime = datetime(2024, 10, 1, 10, 0),
        end_datetime = datetime(2024, 10, 1, 11, 0)
    )
    db.add(new_class)
    db.commit()
    return new_class

def create_room(db):

    new_room = Rooms(

        room_type = RoomType.STUDIO,
        room_number = "101A",
        capacity = 20
    )
    db.add(new_room)
    db.commit()
    return new_room

def create_ClassRegistration(db, class_id, member_id, attended=False):

    class_registration = ClassRegistrations(
        
        member_id = member_id,
        class_id = class_id,
        attended = attended
    )
    db.add(class_registration)
    db.commit()
    return class_registration

def test_member_lookup(db):
    
    trainer = create_trainer_user(db)
    member = create_member_user(db)

    # create a health metric and member goal for the member
    metric = add_health_metric(db, user_id=member.id, weight=70.0, height=175.0, bpm=60)
    goal = add_member_goals(db, user_id=member.id, body_fat_percent=15.0, target_weight=40.0 )
    
    # create a room
    new_room = create_room(db)
    # create a class with the trainer and register the member to it
    new_class = create_class(db, trainer.id, new_room.id)
    registration = create_ClassRegistration(db, new_class.id, member.id, attended=False)

    # trainer looks up the member
    allowed = allow_lookup_member(db, trainer.id, member.id)
    assert allowed == True

    current_goal, last_metric = lookup_member(db, member.id)
    assert current_goal is goal
    assert last_metric is metric

    # create a non trainer user and try to lookup member
    non_trainer = create_admin_user(db)
    allowed = allow_lookup_member(db, non_trainer.id, member.id)
    assert allowed == False


def test_member_lookup_no_upcoming_session(db):

    trainer = create_trainer_user(db)
    member = create_member_user(db)

    # create a room
    new_room = create_room(db)
    # create a class with the trainer and register the member to it
    new_class = create_class(db, trainer.id, new_room.id)
    registration = create_ClassRegistration(db, new_class.id, member.id, attended=True)  # attended=True means no upcoming session

    assert allow_lookup_member(db, trainer.id, member.id) == False

def test_member_lookup_no_pt_sessions(db):

    trainer = create_trainer_user(db)
    member = create_member_user(db)

    # trainer has no PT sessions at all
    assert allow_lookup_member(db, trainer.id, member.id) == False