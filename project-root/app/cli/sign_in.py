from app.users import add_user, authentication
# remember to create sessions inside fuctions to prevent session leaks

# sign in: returns user object if authenticated, else None
def user_sign_in(db):
    
        # ask for user credentials
    print("Please sign in to continue.")
    user_email = input("Email: ").strip()
    user_password = input("Password: ").strip()

    # validate credentials 
    try:
        user = authentication(db, user_email, user_password)
        print(f"Welcome back, {user.first_name}!")
        return user

    except ValueError as e:
        print("Error during authentication:", e)
        choice = input("Try again? (y/n): ").strip().lower()
        if choice != "y":
            return None
   
                
def sign_up(db):
    
    print("create a new account by providing the following details:")

    first_name = input("First Name: ").strip()
    last_name = input("Last Name: ").strip()
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    date_of_birth = input("Date of Birth (YYYY-MM-DD): ").strip()
    sex = input("Sex (man/woman/other): ").strip()
    role = input("Role (admin/trainer/member): ").strip().lower()

    try:
        user = add_user(db, email, first_name, last_name, date_of_birth, role, sex, password)
        return user

    except ValueError as e:
        print("Error during sign up:", e)
        return None
    
  
    
