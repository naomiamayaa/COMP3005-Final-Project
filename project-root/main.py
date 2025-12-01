# main.py is your command hub.
# It imports and registers the other POV command groups.

from app.cli.sign_in import user_sign_in, sign_up
from models.create_models import main as create_models
from models.models import UserRole
from app.cli.commands.member import member_POV
from app.cli.commands.trainer import trainer_pov
from models.database import SessionLocal, Base

#from app.populate_tables import seed
#added
from app.cli.commands.admin import admin_dashboard, equipment_management_menu, class_scheduling_menu 
from app.cli.commands.member import member_POV
from app.cli.commands.trainer import trainer_pov


def main():

    db = SessionLocal()

    try:
        create_models()
        

        print()
        print()
        print()
        print("===================================")
        print("       Welcome to NewFitness!      ")
        print("===================================")

        while True:
            print("\nPlease choose an option:")
            print("1. Sign In")
            print("2. Sign Up")
            print("3. Exit")

            choice = input("Enter your choice (1-3): ").strip()

            if choice == "1":
                user = user_sign_in(db)
                if user:
                    print(f"- Successfully signed in as {user.first_name} {user.last_name}.")
                    # Here you can add more functionality after sign-in
                    print("- You can now access your dashboard and manage your account.")
                    # get user role and display appropriate message
                    if user.role == UserRole.MEMBER:
                        print("- You have member privileges.")
                        member_POV(db, user)
            
                    elif user.role == UserRole.TRAINER:
                        print("- You have trainer privileges.")
                        trainer_pov(user)
            

                    elif user.role == UserRole.ADMIN:
                        print("- You have admin privileges.")
                        admin_dashboard(db, user)
                else:
                    print("Sign in failed.")

            elif choice == "2":
                user = sign_up(db)
                if user:
                    print(f"Account created successfully for {user.first_name} {user.last_name}. You can now sign in.")
                else:
                    print("Sign up failed or cancelled.")

            elif choice == "3":
                print()
                print("===================================")
                print(" Thank you for choosing NewFitness!")
                print("===================================")
                print()

                break

            else:
                print("enter a number between 1 and 3.")

    finally:
        db.close()
        
# call main
main()