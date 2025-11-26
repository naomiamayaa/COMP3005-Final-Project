# Add_health_metric CRUD(...)  (F3) Log multiple metric entries; do not overwrite. 
# Must support time-stamped entries. input new health metrics (e.g., weight, heart rate).
# members can input new measurements for the existing metric types. 

# trainers can view/update member health metrics only if the specified members are clients.

from app.models import Users, UserRole, HealthMetrics
from sqlalchemy import Column, DateTime

# this function allows editing rights for both trainers and members. It does NOT check whether the trainer is assigned to the member. 
# that check should be done in the route handler if needed.
def add_health_metric(session, user_id, weight, height, bpm):

    # figure out if user_id is a member
    member_exists = session.query(Users).filter( Users.id==user_id, Users.role==UserRole.MEMBER ).first()

    if not member_exists:
        raise ValueError(f"No user found with id={user_id} that is a member.")
    
    # validate inputs
    try:
        weight = float(weight)
        height = float(height)
        bpm = int(bpm)
    except ValueError:
        raise ValueError("Weight and height must be numeric (float), bpm (beats per minute) must be an integer.")
    
    if weight <= 0 or height <= 0 or bpm <= 0:
        raise ValueError("Weight (kg), height (cm), and bpm (beats per minute) must be positive numbers.")

    new_metric = HealthMetrics(
        member_id = user_id,
        weight = weight,
        height = height,
        bpm = bpm
    )
    session.add(new_metric)
    session.commit()
    print(f"Health metrics for user id {user_id} added successfully.")
    return new_metric

def get_health_metrics(session, user_id):
    
    metrics = session.query(HealthMetrics).filter( HealthMetrics.member_id==user_id ).all()
    if not metrics:
        print(f"No health metrics found for member id={user_id}. Return Empty list")
        return []

    return metrics

def delete_health_metric(session, metric_id, user_id):

    # figure out if user_id is a member
    member_exists = session.query(Users).filter( Users.id==user_id, Users.role==UserRole.MEMBER ).first()
    if not member_exists:
        raise ValueError(f"No user found with id={user_id} that is a member.")

    # find the metric and check if that metric belongs to the provided user_id
    metric_exists = session.query(HealthMetrics).filter( HealthMetrics.id==metric_id, HealthMetrics.member_id==user_id ).first()
    if not metric_exists:
        raise ValueError(f"No health metric found with id={metric_id} for member id={user_id}.")

    session.delete(metric_exists)
    session.commit()
    print(f"Health metric id {metric_id} for member id {user_id} deleted successfully.")
    return 1