from datetime import datetime, date, time, timedelta
from sqlalchemy import and_, or_

from app.models import Users, UserRole, Sex
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
                date_of_birth=None, role=None, sex=None, password=None):

    # if user id not in database
    user = session.query(Users).filter_by(id=user_id).first()
    print (f"user id {user_id} found.")
    if not user:
        raise ValueError(f"No user found with id={user_id}.")   
    
    # if the to-be-updated email is already used
    used_email = session.query(Users).filter_by(email=email_input).first() 
    if used_email:
        raise ValueError("Email already exists for another user.")
    else:
        user.email = email_input

    if first_name == "" or last_name == "":
        raise ValueError("First or last name empty. Cannot proceed.")
    else:
        user.first_name = first_name.capitalize()
        user.last_name= last_name.capitalize()

    # date of birth validity
    try:
        dob = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        user.date_of_birth = dob
    except ValueError:
        raise ValueError("Invalid date format. Please use YYYY-MM-DD.")
    
    if password == "":
        raise ValueError("empty password. Cannot proceed.")
    else:
        user.password = password
        print (f"password for user {user_id} has been changed.")

    if role:
        raise ValueError("eannot change a user's role once established.")
    
    if sex:
        # sex enum validity check
        try:
            # Convert to lowercase to match your enum values
            role_enum = Sex(sex.lower())   
            sex = role_enum
            print(f"sex changed.")
        except ValueError:
            # if role_input not in enum valid list, raise error
            valid = [s.value for s in Sex]
            raise ValueError(f"Invalid sex '{sex}'. Must be one of: {valid}")

    session.commit()
    print("User details updated successfully.")
    return user

# ----------------------get/delete user details-----------------------------

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

