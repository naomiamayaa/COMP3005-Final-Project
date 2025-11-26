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
from app.health_metrics import add_health_metric, get_health_metrics, delete_health_metric          

from app.database import Base
from app import scheduling
from app.models import (
    Users,
    Members,
    HealthMetrics,
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


def test_add_health_metrics(db):

    member = create_member_user(db) 
    member_id = member.id
    metrics = add_health_metric(db, user_id=member_id, weight=70.0, height=175.0, bpm=60)

    assert metrics.member_id == member.id
    assert metrics.weight == 70.0
    assert metrics.height == 175.0
    assert metrics.bpm == 60
    assert metrics.date_recorded is not None

def test_add_health_metrics_non_member(db):

    non_member = create_non_member_user(db)
    non_member_id = non_member.id

    with pytest.raises(ValueError) as errorinfo:
        add_health_metric(db, user_id=non_member_id, weight=70.0, height=175.0, bpm=60)
    
    assert f"No user found with id={non_member_id} that is a member." in str(errorinfo.value)

def test_add_invalid_health_metrics(db):

    member = create_member_user(db)
    member_id = member.id

    with pytest.raises(ValueError) as errorinfo:
        add_health_metric(db, user_id=member_id, weight=-70.0, height=175.0, bpm=60)
    assert "Weight (kg), height (cm), and bpm (beats per minute) must be positive numbers." in str(errorinfo.value)

    with pytest.raises(ValueError) as errorinfo:
        add_health_metric(db, user_id=member_id, weight=70.0, height="one million", bpm=60)
    assert "Weight and height must be numeric (float), bpm (beats per minute) must be an integer." in str(errorinfo.value)


# ------------------ Display Health Metrics Tests -----------------

def test_get_health_metrics(db):

    member = create_member_user(db)
    member_id = member.id

    # add some health metrics
    add_health_metric(db, user_id=member_id, weight=70.0, height=175.0, bpm=60)
    add_health_metric(db, user_id=member_id, weight=68.0, height=154.5, bpm=58)

    metrics = get_health_metrics(db, user_id=member_id)
    assert len(metrics) == 2
    assert metrics[0].weight == 70.0
    assert metrics[1].weight == 68.0

    assert metrics[0].height == 175.0
    assert metrics[1].height == 154.5

    assert metrics[0].bpm == 60
    assert metrics[1].bpm == 58

def test_display_health_metrics_non_member(db):

    non_member = create_non_member_user(db)
    non_member_id = non_member.id

    get_health_metrics(db, user_id=non_member_id)
    assert f"No health metrics found for member id={non_member_id}. Return Empty list." 
    assert get_health_metrics(db, user_id=non_member_id) == []

def test_get_health_metrics_no_metrics(db):

    member = create_member_user(db)
    metrics = get_health_metrics(db, user_id=member.id)
    assert metrics == []

# ------------------ Delete Health Metric Tests -----------------

def test_delete_health_metric(db):

    member = create_member_user(db)
    member_id = member.id

    metric = add_health_metric(db, user_id=member_id, weight=70.0, height=175.0, bpm=60)
    metric_id = metric.id

    result = delete_health_metric(db, metric_id=metric_id, user_id=member_id)
    assert result == 1
    assert get_health_metrics(db, user_id=member_id) == []
  
    get_health_metrics(db, user_id=member_id)
    assert f"No health metrics found for member id={member_id}."

    # verify deletion
    metrics = get_health_metrics(db, user_id=member_id)
    assert len(metrics) == 0

def test_delete_nonexistent_health_metric(db):

    member = create_member_user(db)
    member_id = member.id

    with pytest.raises(ValueError) as errorinfo:
        delete_health_metric(db, metric_id=101, user_id=member_id)
    
    assert f"No health metric found with id=101 for member id={member_id}." in str(errorinfo.value)