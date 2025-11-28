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

from models.database import Base
from app import scheduling
from models.models import (
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


#------------------ Helper Functions -----------------

# helper function to create a new user for  tests
def new_shiny_user(db):
    user = add_user(
        db,
        email_input="test5@example.com",
        password="hashed",
        first_name="Health",
        sex_input="other",
        last_name="User",
        date_of_birth="2003-07-07",
        role_input="admin", 
    )
    return user

#------------------ add user tests -----------------

def test_add_user_success(db):
    # Act & Assert: add user successfully
    # Arrange: create user
    db_result = db.query(Users).filter_by(email="test2@example.com").first()
    assert db_result is None

    add_user(
        db,
        email_input="test2@example.com",
        password="hashed",
        first_name="heAlTh",
        sex_input="woman",
        last_name="User",
        date_of_birth="2003-07-07",
        role_input="member", 
    )

    db_result = db.query(Users).filter_by(email="test2@example.com").first()
    assert db_result is not None
    assert db_result.first_name == "Health"

def test_add_user_duplicate_email(db):
    # Arrange: create initial user
    add_user(
        db,
        email_input="test2@example.com",
        password="hashed",
        first_name="Health",
        sex_input="woman",
        last_name="User",
        date_of_birth="2003-07-07",
        role_input="member", 
    )
    db_result = db.query(Users).filter_by(email="test2@example.com").first()
    assert db_result is not None
    
    with pytest.raises(ValueError) as excinfo:
        add_user(
            db,
            email_input="test2@example.com",
            password="hashed",
            first_name="Health",
            sex_input="woman",
            last_name="User",
            date_of_birth="2003-07-07",
            role_input="member", 
        )
    
    assert "User already exists! Provide a different email." in str(excinfo.value)

def test_add_user_invalid_role(db):
    with pytest.raises(ValueError) as excinfo:
        add_user(
            db,
            email_input="test3@example.com",
            password="hashed",
            first_name="Health",
            sex_input="man",    
            last_name="User",
            date_of_birth="2003-07-07",
            role_input="invalid_role",
        )
    assert "Invalid role 'invalid_role'." in str(excinfo.value)


def test_add_user_incorrect_date_format(db):
    with pytest.raises(ValueError) as excinfo:
        add_user(
            db,
            email_input="test3@example.com",
            password="hashed",
            first_name="Health",
            sex_input="man",    
            last_name="User",
            date_of_birth="2065-17-90",
            role_input="trainer",
        )
    assert "Invalid date format. Please use YYYY-MM-DD." in str(excinfo.value)


# ----------------- update user tests -----------------

def test_update_user(db):
    # Arrange: create initial user
    add_user(
        db,
        email_input="test4@example.com",
        password="hashed",
        first_name="Health",
        sex_input="other",
        last_name="User",
        date_of_birth="2003-07-07",
        role_input="member", 
    )

    update_user(
        db,
        user_id=1,
        email_input="updated@example.com",
        first_name="Updated",
        last_name="User",
        date_of_birth="2000-01-01",
        sex="other",
        password="newhashedpassword"
    )

    db_result = db.query(Users).filter_by(email="updated@example.com").first()
    assert db_result is not None

    db_result = db.query(Users).filter_by(email="test4@example.com").first()
    assert db_result is None



# ----------------- delete user tests -----------------

def test_delete_user(db):
    # Arrange: create initial user
    user = new_shiny_user(db)

    user_id = user.id
    delete_user(db, user_id=user_id)

    db_result = db.query(Users).filter_by(id=user_id).first()
    assert db_result is None

def test_delete_user_not_found(db):

    with pytest.raises(ValueError) as errorinfo:
        delete_user(db, user_id=101)
    assert "No user found" in str(errorinfo.value)


# ----------------- get user by id tests -----------------

def test_get_user_by_id(db):

    user = new_shiny_user(db)

    fetched_user = get_user_by_id(db, user.id)
    assert fetched_user is not None
    assert fetched_user.id == user.id
    assert fetched_user.email == user.email
    assert fetched_user.first_name == user.first_name

def test_get_user_by_id_not_found(db):

    with pytest.raises(ValueError) as errorinfo:
        fetched_user = get_user_by_id(db, user_id=101)
    assert "No user found" in str(errorinfo.value)

# ----------------- get all users tests -----------------

def test_get_all_users(db):

    user1 = new_shiny_user(db)
    user2 = add_user(
        db,
        email_input="test70@example.com",
        password="non",
        first_name="tyra",
        sex_input="woman",
        last_name="bingus",
        date_of_birth="2003-07-04",
        role_input="admin", 
    )

    all_users = get_all_users(db)
    assert len(all_users) == 2
    assert all_users[0].email == user1.email    
    assert all_users[1].email == user2.email

def test_get_all_users_empty(db):

    all_users = get_all_users(db)
    assert len(all_users) == 0