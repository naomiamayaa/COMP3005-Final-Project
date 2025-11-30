from app.users import update_user, get_user_by_email
from app.health_metrics import add_health_metric, get_health_metrics
from app.member_goals import get_member_goals, add_member_goals, update_member_goals, get_all_user_goals
from models.models import MemberGoals    

    # 1) View dashboard
    # 2) Schedule PT sessions - wait for charita?
    # 3) Register for group fitness classes
    # 4) Manage personal information
    # 5) Manage fitness goals
    # 6) Manage Health history

def member_POV(db, user):

    print()
    print()
    print()
    print("===================================")
    print("       <   Member Home   >         ")
    print("===================================")

    while True:
        print("\nPlease choose an option:")
        print()
        print("1. View dashboard")
        print("2. Schedule PT sessions")
        print("3. Register for group fitness classes")
        print("4. Manage personal information")
        print("5. Manage fitness goals")
        print("6. Manage health history")
        print("7. Exit / Return to sign in menu")
        print()
        choice = input("Enter your choice (1-3): ").strip()
        print()

        #if choice == "1":
        
        #elif choice == "2":
        #elif choice == "3":
        if choice == "4":
            manage_personal_info(db, user)

        elif choice == "5":
            manage_member_goals(db, user)

        #elif choice == "6":


           


        elif choice == "7":
            print()
            print("===================================")
            print(" Thank you for choosing NewFitness!")
            print("===================================")
            print()

            break

        else:
            print("Invalid choice. Please enter a number between 1 and 7.")

def manage_personal_info(db, user):
    while True: 
        
        print("\nPlease choose an option:")
        print("1. Change Password")
        print("2. Change First Name")
        print("3. Change Last Name")
        print("4. Change Email")
        print("5. Change Date of Birth")
        print("6. Change Sex")
        print("7. Exit")
        
        choice = input("Enter your choice (1-7): ").strip()
        print()

        if choice == "1":
            try:
                pw = input("Enter new password: ").strip()
                update_user(db, user.id, password=pw)
                print("Password updated successfully.")
            except ValueError as e:
                print("Could not update password:", e)

        elif choice == "2":
            try:
                first = input("Enter new first name: ").strip()
                update_user(db, user.id, first_name=first)
                print("First name updated successfully.")
            except ValueError as e:
                print("Could not update first name:", e)

        elif choice == "3":
            try:
                last = input("Enter new last name: ").strip()
                update_user(db, user.id, last_name=last)
                print("Last name updated successfully.")
            except ValueError as e:
                print("Could not update last name:", e)

        elif choice == "4":
            try:
                email = input("Enter new email: ").strip()
                update_user(db, user.id, email_input=email)
                print("Email updated successfully.")
            except ValueError as e:
                print("Could not update email:", e)

        elif choice == "5":
            try:
                dob = input("Enter new date of birth (YYYY-MM-DD): ").strip()
                update_user(db, user.id, date_of_birth=dob)
                print("Date of birth updated successfully.")
            except ValueError as e:
                print("Could not update date of birth:", e)

        elif choice == "6":
            try:
                sex = input("Enter new sex (male/female/other): ").strip().lower()
                update_user(db, user.id, sex=sex)
                print("Sex updated successfully.")
            except ValueError as e:
                print("Could not update sex:", e)

        elif choice == "7":
    
            print("\nYour updated information:")
            print(f"First Name: {user.first_name}")
            print(f"Last Name: {user.last_name}")
            print(f"Email: {user.email}")
            print(f"Date of Birth: {user.date_of_birth}")
            print(f"sex: {user.sex}")

            print("Back to home.")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 7.")


def manage_member_goals(db, user):

    while True:
        print("\n choose an option:")
        print("1. Add New Goals")
        print("2. update Existing Goals")
        print("3. view Current goals")
        print("4. exit")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            try:
                body_fat = input("Enter body fat percentage (0-100): ").strip()
                target_weight = input("Enter target weight (kg): ").strip()
                add_member_goals(db, user.id, body_fat, target_weight)
            except ValueError as e:
                print("Could not add goals:", e)

        elif choice == "2":
            try:
                goals = get_all_user_goals(db, user.id)
                if goals==[]:
                    print("No existing goals found. Please add goals first.")
                    continue

                print("\nExisting goals:") # print all goals so user knows which one to edit
                print("========================================")
                for g in goals:
                    print(f"User id: {g.id}, body Fat: {g.body_fat_percent}, target weight: {g.target_weight}")

                goal_id = input("Enter the ID of the goal you want to update: ").strip()
                body_fat = input("Enter new body fat percentage (0-100): ").strip()
                target_weight = input("Enter new target weight (kg): ").strip()

                update_member_goals(db, int(goal_id), user.id, body_fat, target_weight)

            except ValueError as e:
                print("Could not update goal:", e)

        elif choice == "3":
            goals = get_all_user_goals(db, user.id)
            if not goals:
                print("No goals found.")
            else:
                print("\nYour current goals:")
                for g in goals:
                    print(f"ID: {g.id}, Body Fat: {g.body_fat_percent}, Target Weight: {g.target_weight}")

        elif choice == "4":
            print("Back to member dashboard.")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 4.")
         

   