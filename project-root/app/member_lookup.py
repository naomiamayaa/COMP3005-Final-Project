# lookup_member(...)  (F9) Search by name (case-insensitive) 
# and view current goal and last metric. No editing rights. (trainer’s POV)

from models.models import ClassType, Users, UserRole, MemberGoals, HealthMetrics, Classes, ClassRegistrations
from sqlalchemy import desc

# checks if the trainer is allowed to lookup the member (the trainer must the the member's personal trainer)
# aka have a PT scheduled session with the member.
def allow_lookup_member(session, trainer_id, member_id):

    # select classes where trainer_id matches and session_type is PT
    scheduled_session = session.query(Classes).filter(
        Classes.trainer_id == trainer_id,
        Classes.class_type == ClassType.PT  # only PT sessions
        ).all()
    if not scheduled_session:
        print("trainer has no PT sessions.")
        return False  # no PT sessions found for the trainer
    
    # from the resulting table, check if any of the sessions include the member_id
    for session_instance in scheduled_session:
        registration = session.query(ClassRegistrations).filter(
            ClassRegistrations.class_id == session_instance.id,
            ClassRegistrations.member_id == member_id, 
            ClassRegistrations.attended == False # must have an upcoming class
        ).first()
        if registration:
            return True  # trainer is allowed to lookup the member
    print("No upcoming PT sessions with the member found.")
    return False  # no scheduled PT sessions with the member found

# member id previously validated in route handler
# member may or may not have goals/metrics yet.
# call the member's current goal and last metric
def lookup_member(session, member_id):
    
    member = session.query(Users).filter( Users.id==member_id, Users.role==UserRole.MEMBER ).first()
    if not member:
        raise ValueError(f"No user found with id={member_id} that is a member.")
    
    current_goal = session.query(MemberGoals).filter(MemberGoals.member_id == member_id).order_by(desc(MemberGoals.id)).first()
    last_metric = session.query(HealthMetrics).filter(HealthMetrics.member_id == member_id).order_by(desc(HealthMetrics.id)).first()

    return current_goal, last_metric