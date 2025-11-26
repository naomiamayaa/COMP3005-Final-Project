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

from app.database import Base
from app import scheduling
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

def create_non_member_user(db):

    non_member = add_user(
        db,
        email_input="test5@example.com",
        password="hashed",
        first_name="Health",
        sex_input="other",
        last_name="User",
        date_of_birth="2003-07-07",
        role_input="admin", 
    )
    return non_member

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

def test_add_member_goals(db):

    member = create_member_user(db)
    member_id = member.id
    goals = add_member_goals(db, user_id=member_id, body_fat_percent=15.0, target_weight=40.0 )
    assert goals.member_id == member.id
    assert goals.body_fat_percent == 15.0
    assert goals.target_weight == 40.0

# create a non-member user and try to add member goals for them
def test_add_member_goals_non_member(db):

    non_member = create_non_member_user(db)
    non_member_id = non_member.id

    with pytest.raises(ValueError) as errorinfo:
        add_member_goals(db, user_id=non_member_id, body_fat_percent=15.0, target_weight=40.0 )
    assert f"No user found with id={non_member_id} that is a member." in str(errorinfo.value)

def test_add_invalid_bfp(db):

    member = create_member_user(db)
    member_id = member.id

    with pytest.raises(ValueError) as errorinfo:
        add_member_goals(db, user_id=member_id, body_fat_percent= -5.0, target_weight=50.0)
    assert "body_fat_percent must be between 0 and 100." in str(errorinfo.value) 

def test_add_invalid_target_weight(db):
    member = create_member_user(db)
    member_id = member.id

    with pytest.raises(ValueError) as errorinfo:
        add_member_goals(db, user_id=member_id, body_fat_percent= 20.0, target_weight=-10.0)
    assert "target_weight must be a positive number." in str(errorinfo.value) 

def test_non_float_inputs(db):

    member = create_member_user(db)
    member_id = member.id

    with pytest.raises(ValueError) as errorinfo:
        add_member_goals(db, user_id=member_id, body_fat_percent= "fifteen", target_weight="forty")
    assert "Weight (kg) must be a numeric float, ex: 70.5 & body_fat_percent must be a numeric float between 0 - 100." in str(errorinfo.value)


#------------------ update member goals tests -----------------

def test_update_member_goals(db):

    member = create_member_user(db)
    member_id = member.id
    goals = add_member_goals(db, user_id=member_id, body_fat_percent=15.0, target_weight=40.0 )

    updated_goals = update_member_goals(db, id=goals.id, user_id=member_id, body_fat_percent=18.0, target_weight=42.0 )

    assert updated_goals.body_fat_percent == 18.0
    assert updated_goals.target_weight == 42.0

def test_update_member_goals_not_found(db):

    member = create_member_user(db)
    member_id = member.id

    with pytest.raises(ValueError) as errorinfo:
        update_member_goals(db, id=101, user_id=member_id, body_fat_percent=18.0, target_weight=42.0 )
    assert f"No goal found with id=101 for member id={member_id}."in str(errorinfo.value)

#returns all goals for a member
def test_get_member_goals(db):

    member = create_member_user(db)
    member_id = member.id
    g1 = add_member_goals(db, user_id=member_id, body_fat_percent=15.0, target_weight=40.0 )
    g2 = add_member_goals(db, user_id=member_id, body_fat_percent=18.0, target_weight=42.0 )

    fetched_goals = get_member_goals(db, user_id=member_id)

    assert fetched_goals is not []

    ids = [g.id for g in fetched_goals]
    assert g1.id in ids
    assert g2.id in ids

def test_get_member_goals_not_found(db):

    member = create_member_user(db)
    member_id = member.id

    goals = get_member_goals(db, user_id=member_id)
    assert f"No goals found for member id={member_id}. Return empty list" 
    assert len(goals) == 0

def test_get_all_member_goals(db):

    member1 = create_member_user(db)
    member1_id = member1.id
    add_member_goals(db, user_id=member1_id, body_fat_percent=15.0, target_weight=40.0 )

    member2 =add_user(
        db,
        email_input="test231@example.com",
        password="hashed",
        first_name="Health",
        sex_input="other",
        last_name="User",
        date_of_birth="2003-03-07",
        role_input="member", 
    )

    member2_id = member2.id
    add_member_goals(db, user_id=member2_id, body_fat_percent=20.0, target_weight=60.0 )   

    all_goals= get_all_member_goals(db)
    assert len(all_goals) == 2


# ------------------ delete member goals tests -----------------

def test_delete_member_goal(db):

    member = create_member_user(db)
    member_id = member.id
    goals = add_member_goals(db, user_id=member_id, body_fat_percent=15.0, target_weight=40.0 )
    goal_id = goals.id

    success = delete_member_goal(db, id=goal_id, user_id=member_id)
    assert success == 1
    assert db.query(MemberGoals).filter_by(id=goal_id).first() is None