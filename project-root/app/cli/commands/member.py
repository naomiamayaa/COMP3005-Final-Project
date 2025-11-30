from app.users import update_user, delete_user
from app.health_metrics import add_health_metric, get_health_metrics, delete_health_metric
from app.member_goals import add_member_goals, update_member_goals, get_all_user_goals, delete_member_goal
from app.member_lookup import lookup_member
from app.classes import print_upcoming_group_sessions, register_for_group_class, list_group_classes, cancel_booking, count_past_classes, print_upcoming_pt_sessions, print_available_PT_sessions, book_pt_session

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
        print("2. Manage PT sessions")
        print("3. Manage group fitness classes")
        print("4. Manage personal information")
        print("5. Manage fitness goals")
        print("6. Manage health history")
        print("7. Exit / Return to sign in menu")
        print()
        choice = input("Enter your choice (1-7): ").strip()
        print()

        if choice == "1":
            view_dashboard(db, user)

        elif choice == "2":
           manage_PT_sessions(db,user)

        elif choice == "3":
            manage_group_fitness_classes(db, user)
        
        elif choice == "4":
            manage_personal_info(db, user)

        elif choice == "5":
            manage_member_goals(db, user)

        elif choice == "6":
            manage_health_history(db, user)

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
        print("7. Delete User")
        print("8. Exit")
        
        choice = input("Enter your choice (1-8): ").strip()
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

            try: 
                delete_user(db, user.id)
            except ValueError as e:
                print("Could not delete user:", e)

        elif choice == "8":
    
            print("\nYour updated information:")
            print(f"First Name: {user.first_name}")
            print(f"Last Name: {user.last_name}")
            print(f"Email: {user.email}")
            print(f"Date of Birth: {user.date_of_birth}")
            print(f"sex: {user.sex}")

            print("Back to home.")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 8.")

def manage_member_goals(db, user):

    while True:
        print("\n choose an option:")
        print("======================")
        print("1. Add New Goals")
        print("2. update Existing Goals")
        print("3. view Current goals")
        print("4. delete goals ")
        print("5. exit")

        choice = input("Enter your choice (1-5): ").strip()

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
                    print(f"goal id: {g.id}, Body Fat: {g.body_fat_percent}, Target Weight: {g.target_weight}")

        elif choice == "4":

            print("\nExisting goals:") # print all goals so user knows which one to edit
            print("========================================")
            for g in goals:
                print(f"User id: {g.id}, body Fat: {g.body_fat_percent}, target weight: {g.target_weight}")

            try:
                goal_id = input("Enter the ID of the goal you want to update: ").strip()
                delete_member_goal(db, goal_id, user.id )

            except ValueError as e:
                print("Could not  delete goal:", e)
            
        elif choice == "5":
            print("Back to member dashboard.")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 4.")
         
def manage_health_history(db, user):

    while True:
        print("\nChoose an option:")
        print("======================")
        print("1. Add new Health Metric")
        print("2. View Health Metrics")
        print("3. delete health Metric")
        print("4. exit")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            try:
                weight = input("Enter weight (kg): ").strip()
                height = input("Enter height (cm): ").strip()
                body_fat = input("Enter body fat percentage: ").strip()

                new_metric = add_health_metric(
                    db,
                    user_id=user.id,
                    weight =weight,
                    height = height,
                    bpm=body_fat
                )
                print("\n--------------------------")
                print("\nHealth metric added successfully:")
                print(f"metric id: {new_metric.id}")
                print(f"Weight: {new_metric.weight} kg")
                print(f"Weight: {new_metric.height} cm")

                print(f"body Fat: {new_metric.bpm}%")
                print(f"timestamp: {new_metric.date_recorded}")

            except ValueError as e:
                print("Could not add health metric:", e)

        elif choice == "2":
            print("\nCurrent Health Metrics: ")

            metrics = get_health_metrics(db, user_id=user.id)

            if not metrics:
                print("No health metrics found.")
            
            else:

                print("\nCurrent Health Metrics: ")
                for m in metrics:
                    print("\n--------------------------")
                    print(f"metric id: {m.id}")
                    print(f"Weight: {m.weight} kg")
                    print(f"Weight: {m.height} cm")
                    print(f"body Fat: {m.bpm}%")
                    print(f"timestamp: {m.date_recorded}")

        elif choice == "3":

            metrics = get_health_metrics(db, user_id=user.id)
            
            print("\nCurrent Health Metrics: ")
            for m in metrics:
                    print("\n--------------------------")
                    print(f"metric id: {m.id}")
                    print(f"Weight: {m.weight} kg")
                    print(f"Weight: {m.height} cm")
                    print(f"body Fat: {m.bpm}%")
                    print(f"timestamp: {m.date_recorded}")

            metric_id = input("Enter metric id to delete: ").strip() #str

            try:
                metric_id = int(metric_id)
            except ValueError:
                print("Metric id must be a number.")
                continue

            try:
                delete_health_metric(db, int(metric_id), user.id)
                print(f"Metric with id {metric_id} deleted successfully.")
            except ValueError as e:
                print("Could not delete metric:", e)
    
        elif choice == "4":
            print("\nBack to home!")
            break
        else:
            print("enter a number between 1 and 4.")

def view_dashboard(db,user):

    # show latest health stat (view only)
    # show latest goal (view only) -> call member lookup
    # past class count
    # upcoming pt sessions

    print("================================")
    print("    <   Member Dashboard   >    ")
    print("================================")

    try:
        current_goal, last_metric = lookup_member(db, user.id)

    except ValueError as e:
        print(e)
        return

    print("------------------------------")
    print("\n latest Health Metric")
    print("------------------------------")

    if last_metric:
        print(f"Recorded on:   {last_metric.date_recorded}")
        print(f"Weight:        {last_metric.weight} kg")
        print(f"Height:        {last_metric.height} cm")    
        print(f"Body Fat:      {last_metric.bpm}%")

    else:
        print("No health metrics recorded yet.")

    print("------------------------------")
    print("\n      current Fitness Goal")
    print("------------------------------")

    if current_goal:

        print(f"target weight:     {current_goal.target_weight}")
        print(f"Target body fat %:  {current_goal.body_fat_percent}")
    else:
        print("no goals set.")

   
    if last_metric and current_goal:
        progress = current_goal.target_weight - last_metric.weight #calculating the progress

        print("------------------------------------")
        print("\n    Progress toward Weight Goal")
        print("------------------------------------")

        if progress > 0:
            print(f"you are {progress:.1f} kg above your target weight !!!")
        elif progress < 0:
            print(f"You are {abs(progress):.1f} kg below your target weight !!!")
        else:
            print("you have reached your target weight !!!")
    else: 
        print("\nprogress cant be calculated because no metrics or goals exist.")

    # participation in past group classes

    print("------------------------------------")
    print("\n   Past Group Classes attended:   ")
    print("------------------------------------")

    id = user.id
    past_classes = count_past_classes(db, id)
    print(f"{user.first_name} has attended {past_classes} group classes! Keep it up!")

    # upcoming personal training sessions
    print("------------------------------------")
    print("\n   Upcoming PT sessions::   ")
    print("------------------------------------")
    print_upcoming_pt_sessions(db, id)

def manage_PT_sessions(db, user):

    while True:
        print("\nPlease choose an option:")
        print()
        print("1. schedule a new PT session")
        print("2. cancel a PT session.")
        print("3. Exit")
        choice = input("Enter your choice (1-3): ").strip()

        if choice =="1":
            schedule_PT_Session(db, user)

        elif choice =="2":
            cancel_PT_session(db, user)

        elif choice =="3":
            break

#  Allows a member to schedule a PT session.
def schedule_PT_Session(db, user):
  
    try:
        available_sessions = print_available_PT_sessions(db)

        if available_sessions is None:
            #print("no available PT sessions at the moment. sorry!")
            return
        
        session_id = int(input("Enter the ID of the PT session you want to book: ").strip())
        # Validate session ID
        selected_session = next((s for s in available_sessions if s.id == session_id), None)
        if not selected_session:
            print("invalid session id, or the session is already booked.")
            return
        
        member_id = user.id
        registration = book_pt_session(db, member_id, session_id)
        print(f"Successfully booked PT session! Session id for reference: {session_id}")
        return registration

    except ValueError as e:
        print("Error booking session:", e)
        
def cancel_PT_session(db, user):

    member_id = user.id

    print("------------------------------------")
    print("\n   Upcoming PT sessions:   ")
    print("------------------------------------")
    print_upcoming_pt_sessions(db, member_id)

    choice = input("Enter the class id you wish to delete: ").strip()
    choice = int(choice)
    try:
        bool = cancel_booking(db, member_id, choice)

    except ValueError as e:
        print("error canceling session:", e)

    if bool:
        print(f"successful deletion of PT session class id = {choice}")

def manage_group_fitness_classes(db, user):

    while True:
        print("\nPlease choose an option:")
        print()
        print("1. register for a group class")
        print("2. de-register from a group class.")
        print("3. Exit")
        choice = input("Enter your choice (1-3): ").strip()

        if choice =="1":
            member_registers_group_class(db, user)

        elif choice =="2":
            member_deregisters_group_class(db, user)

        elif choice =="3":
            break

def member_registers_group_class(db, user):

    # <display of all g classes here> 
    print("------------------------------------")
    print("\n      All Group Sessions:         ")
    print("------------------------------------")
    all_gClasses = list_group_classes(db)

    for c in all_gClasses:
        class_id = c["class_id"]

        start = c["start_datetime"]
        end = c["end_datetime"]

        day = start.strftime("%Y-%m-%d")
        start_time = start.strftime("%H:%M")
        end_time = end.strftime("%H:%M")

        print(f"Class id: {class_id}")
        # print(f"Trainer:  {trainer_name}")
        print(f"Date:     {day}")
        print(f"Time:     from {start_time} to {end_time}")
        
    choice = input ("select the class id you want to <register> for: ")
    choice = int(choice)
    member_id = user.id

    try:
        registration = register_for_group_class(db, member_id, choice)
        if registration:
            print(f"successful registration for class id = {registration.class_id}")

    except ValueError as e:
        print("error registering for group class:", e)


def member_deregisters_group_class(db, user):

    member_id = user.id 

     # <display of all g classes that the user is registrated in here>  
    print("------------------------------------")
    print("\nUpcoming Registered Group Sessions:")
    print("------------------------------------")
    print_upcoming_group_sessions(db, member_id)

    choice = input ("select the class id you want to <deregister> from: ")
    choice = int(choice)

    try:
        success = cancel_booking(db, member_id, choice)
        if success:
            print(f" deregistration for class id = {choice} successful")

    except ValueError as e:
        print("error deregistering for group class:", e)

