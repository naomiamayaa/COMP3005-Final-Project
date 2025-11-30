from datetime import datetime, date, time, timedelta
from sqlalchemy import and_, or_

from models.models import Users, UserRole, Sex
import hashlib

# user registration: #Add new user
# add_new_user(...) – insert into User.
# all func return boolean 1 if successful, else raise ValueError with message.

def add_user(session, email_input, first_name, last_name, date_of_birth, role_input, sex_input, password):

    # unique user check
    existing_user = session.query(Users).filter_by(email=email_input).first() 
    if existing_user:
        raise ValueError("User already exists! Provide a different email.")
    
    if first_name == "" or last_name == "":
        raise ValueError("First or last name empty. Cannot proceed.")
    
    if password == "":
        raise ValueError("Empty password. Cannot proceed.")
        
    # role enum validity check
    try:
        # Convert to lowercase to match your enum values
        role_enum = UserRole(role_input.lower())   
    except ValueError:
        # if role_input not in enum valid list, raise error
        valid = [r.value for r in UserRole]
        raise ValueError(f"Invalid role '{role_input}'. Must be one of: {valid}")

    # sex enum validity check
    try:
        # Convert to lowercase to match your enum values
        sex_enum = Sex(sex_input.lower())   
    except ValueError:
        # if role_input not in enum valid list, raise error
        valid = [s.value for s in Sex]
        raise ValueError(f"Invalid sex '{sex_input}'. Must be one of: {valid}")
    
    # validate date entry
    try:
        dob = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        print("Valid date:", dob)
    except ValueError:
        raise ValueError("Invalid date format. Please use YYYY-MM-DD.")

    # create new user
    new_user = Users(

        email = email_input,
    
        first_name = first_name.capitalize(),
        last_name = last_name.capitalize(),
        date_of_birth = date_of_birth,
        sex = sex_enum,
        role = role_enum, #converted input
        password_hash = hashlib.sha256(password.encode()).hexdigest()
    )

    session.add(new_user)
    session.commit()
    print(f"User {role_enum},  {first_name.lower()},  {last_name.lower()}, was added successfully.")
    # for later use, to check if adding was successful.
    return new_user

# ----------------------edit user details-----------------------------

# update generic user fields 
def update_user(session, user_id, email_input=None, first_name=None, last_name=None,
                date_of_birth=None, sex=None, password=None):

      # Fetch the user
    user = session.query(Users).filter_by(id=user_id).first()
    if not user:
        raise ValueError(f"No user found with id={user_id}.")

    # Update email
    if email_input is not None:
        used_email = session.query(Users).filter_by(email=email_input).first()
        if used_email and used_email.id != user_id:
            raise ValueError("Email already exists for another user.")
        user.email = email_input

    # Update names
    if first_name is not None:
        if first_name.strip() == "":
            raise ValueError("First name cannot be empty.")
        user.first_name = first_name.strip().capitalize()
    
    if last_name is not None:
        if last_name.strip() == "":
            raise ValueError("Last name cannot be empty.")
        user.last_name = last_name.strip().capitalize()

    # Update date of birth
    if date_of_birth is not None:
        try:
            dob = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
            user.date_of_birth = dob
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD.")

    # Update password
    if password is not None:
        if password.strip() == "":
            raise ValueError("Password cannot be empty.")
        import hashlib
        user.password_hash = hashlib.sha256(password.encode()).hexdigest()

    # Update sex
    if sex is not None:
        try:
            user.sex = Sex(sex.lower())
        except ValueError:
            valid = [s.value for s in Sex]
            raise ValueError(f"Invalid sex '{sex}'. Must be one of: {valid}")

    # Commit changes
    session.commit()
    print(f"User {user_id} updated successfully.")
    return user

# ----------------------get/delete user details-----------------------------

def get_user_by_email(session, email):
    user = session.query(Users).filter_by(email=email).first()
    if not user:
        raise ValueError(f"No user found with email={email}.")
    return user

def get_user_by_id(session, user_id):
    user = session.query(Users).filter_by(id=user_id).first()
    if not user:
        raise ValueError(f"No user found with id={user_id}.")
    return user

def get_all_users(session):
    users = session.query(Users).all()
    return users

def delete_user(session, user_id):
    user = session.query(Users).filter_by(id=user_id).first()
    if not user:
        raise ValueError(f"No user found with id={user_id}.")
    
    session.delete(user)
    session.commit()
    print(f"User with id={user_id} has been deleted.")    
    return 1

# get the role of a user by email, else value error
def get_user_role_by_email(session, email):

    user = session.query(Users).filter_by(email=email).first()
    if not user:
        raise ValueError(f"No user found with email={email}.")
    return user.role
    
# authenticate user: returns user object if authenticated, else None
def authentication(session, email: str, password: str):

    user = get_user_by_email(session, email)
    if user and user.password_hash == hashlib.sha256(password.encode()).hexdigest():
        print("User authenticated:", user.email)
        return user

    print("Could not authenticate user:", email)
    raise ValueError("Authentication failed. Check email and password.")