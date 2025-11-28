
from models.models import Users, UserRole, MemberGoals

# if the user is a member, allow create/edit/delete of MemberGoal.

def add_member_goals(session, user_id,  body_fat_percent, target_weight):

    # filter the user_id for Role=Member
    member_exists = session.query(Users).filter( Users.id==user_id, Users.role==UserRole.MEMBER ).first()

    if not member_exists:
        raise ValueError(f"No user found with id={user_id} that is a member.")
    
    if body_fat_percent is None or target_weight is None:
        raise ValueError("Body fat percent and target weight must be provided.")
    
    try:
        body_fat_percent = float(body_fat_percent)
        target_weight = float(target_weight)
    except ValueError:
        raise ValueError("Weight (kg) must be a numeric float, ex: 70.5 & body_fat_percent must be a numeric float between 0 - 100.")
    
    if not (0 <= body_fat_percent <= 100):
        raise ValueError("body_fat_percent must be between 0 and 100.")
    
    if target_weight <= 0:
        raise ValueError("target_weight must be a positive number.")


    new_goal = MemberGoals(
        member_id = user_id,
        body_fat_percent = body_fat_percent,
        target_weight = target_weight
    )
  
    session.add(new_goal)
    session.commit()
    print(f"Member goals for user id {user_id} added successfully.")
    return new_goal

def update_member_goals(session, id, user_id, body_fat_percent, target_weight):

    # filter the user_id for Role=Member
    member_exists = session.query(Users).filter( Users.id==user_id, Users.role==UserRole.MEMBER ).first()
    if not member_exists:
        raise ValueError(f"No user found with id={user_id} that is a member.")

    # find the goal and check if that goal belongs to the provided user_id
    goal_exists = session.query(MemberGoals).filter( MemberGoals.id==id, MemberGoals.member_id==user_id ).first()
    if not goal_exists:
        raise ValueError(f"No goal found with id={id} for member id={user_id}.")
    
    try:
        body_fat_percent = float(body_fat_percent)
        target_weight = float(target_weight)
    except ValueError:
        raise ValueError("Weight (kg) must be a numeric float, ex: 70.5 & body_fat_percent must be a numeric float between 0 - 100.")

    if body_fat_percent is None or target_weight is None:
        raise ValueError("Body fat percent and target weight must be provided.")
    
    if not (0 <= body_fat_percent <= 100):
        raise ValueError("body_fat_percent must be between 0 and 100.")
    
    if target_weight <= 0:
        raise ValueError("target_weight must be a positive number.")


    goal_exists.body_fat_percent = body_fat_percent
    goal_exists.target_weight = target_weight

    session.commit()
    print(f"Member goals for user id {user_id} updated successfully.")
    return goal_exists

def get_member_goals(session, user_id):
    # filter the user_id for Role=Member
    member_exists = session.query(Users).filter( Users.id==user_id, Users.role==UserRole.MEMBER ).first()
    if not member_exists:
        raise ValueError(f"No user found with id={user_id} that is a member.")
    
    goals = session.query(MemberGoals).filter( MemberGoals.member_id==user_id ).all()
    if not goals:
        print(f"No goals found for member id={user_id}. Return empty list")
        return []

    return goals

def get_all_member_goals(session):
    goals = session.query(MemberGoals).all()

    if not goals:
        print("No member goals found in the database. Empty List returned.")
        return []
    return goals

def delete_member_goal(session, id, user_id):
        
    # filter the user_id for Role=Member
    member = session.query(Users).filter( Users.id==user_id, Users.role==UserRole.MEMBER ).first()

    if not member:
        raise ValueError(f"No user found with id={user_id} that is a member.")
    
    # find the goal and check if that goal belongs to the provided user_id
    goal = session.query(MemberGoals).filter( MemberGoals.id==id, MemberGoals.member_id==user_id ).first()
    if not goal:
        raise ValueError(f"No goal found with id={id} for member id={user_id}.")
    
    session.delete(goal)
    session.commit()
    print(f"Member goals for user id {user_id} deleted successfully.")
    return 1

def delete_all_member_goals(session, user_id):

    # filter the user_id for Role=Member
    member = session.query(Users).filter( Users.id==user_id, Users.role==UserRole.MEMBER ).first()

    if not member:
        raise ValueError(f"No user found with id={user_id} that is a member.")
    
    goals = session.query(MemberGoals).filter( MemberGoals.member_id==user_id ).all()
    if not goals:
        print(f"No goals found for member id={user_id}. Nothing to delete.")
        return 0

    for goal in goals:
        session.delete(goal)
    
    session.commit()
    print(f"All member goals for user id {user_id} deleted successfully.")
    return 1