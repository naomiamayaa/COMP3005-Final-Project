"""
Main application for Health and Fitness Club Management System
COMP3005 Final Project

This is a command-line interface for the fitness club management system.
"""

import sys
from datetime import datetime, date
from tabulate import tabulate
from database import DatabaseConnection, DatabaseManager
from member_operations import MemberOperations
from trainer_operations import TrainerOperations
from admin_operations import AdminOperations


class FitnessClubApp:
    """Main application class"""
    
    def __init__(self):
        """Initialize the application"""
        try:
            self.db_connection = DatabaseConnection()
            self.db_manager = DatabaseManager(self.db_connection)
            self.member_ops = MemberOperations(self.db_manager)
            self.trainer_ops = TrainerOperations(self.db_manager)
            self.admin_ops = AdminOperations(self.db_manager)
            print("\n" + "="*60)
            print("Health and Fitness Club Management System")
            print("="*60)
        except Exception as e:
            print(f"Error initializing application: {e}")
            sys.exit(1)
    
    def display_menu(self):
        """Display main menu"""
        print("\n" + "="*60)
        print("MAIN MENU")
        print("="*60)
        print("1. Member Operations")
        print("2. Trainer Operations")
        print("3. Admin Operations")
        print("4. Reports and Analytics")
        print("0. Exit")
        print("="*60)
    
    def member_menu(self):
        """Member operations menu"""
        while True:
            print("\n" + "-"*60)
            print("MEMBER OPERATIONS")
            print("-"*60)
            print("1. View all members")
            print("2. Add new member")
            print("3. View member details")
            print("4. Update member profile")
            print("5. Register for class")
            print("6. View member schedule")
            print("7. View billing history")
            print("0. Back to main menu")
            print("-"*60)
            
            choice = input("\nEnter your choice: ")
            
            if choice == '1':
                self.view_all_members()
            elif choice == '2':
                self.add_new_member()
            elif choice == '3':
                self.view_member_details()
            elif choice == '4':
                self.update_member_profile()
            elif choice == '5':
                self.register_for_class()
            elif choice == '6':
                self.view_member_schedule()
            elif choice == '7':
                self.view_member_billing()
            elif choice == '0':
                break
            else:
                print("Invalid choice. Please try again.")
    
    def trainer_menu(self):
        """Trainer operations menu"""
        while True:
            print("\n" + "-"*60)
            print("TRAINER OPERATIONS")
            print("-"*60)
            print("1. View all trainers")
            print("2. Add new trainer")
            print("3. View trainer schedule")
            print("4. Schedule class")
            print("5. Schedule personal training session")
            print("6. View personal training sessions")
            print("0. Back to main menu")
            print("-"*60)
            
            choice = input("\nEnter your choice: ")
            
            if choice == '1':
                self.view_all_trainers()
            elif choice == '2':
                self.add_new_trainer()
            elif choice == '3':
                self.view_trainer_schedule()
            elif choice == '4':
                self.schedule_class()
            elif choice == '5':
                self.schedule_personal_session()
            elif choice == '6':
                self.view_personal_sessions()
            elif choice == '0':
                break
            else:
                print("Invalid choice. Please try again.")
    
    def admin_menu(self):
        """Admin operations menu"""
        while True:
            print("\n" + "-"*60)
            print("ADMIN OPERATIONS")
            print("-"*60)
            print("1. Room Management")
            print("2. Equipment Management")
            print("3. Class Management")
            print("4. Billing Management")
            print("0. Back to main menu")
            print("-"*60)
            
            choice = input("\nEnter your choice: ")
            
            if choice == '1':
                self.room_management()
            elif choice == '2':
                self.equipment_management()
            elif choice == '3':
                self.class_management()
            elif choice == '4':
                self.billing_management()
            elif choice == '0':
                break
            else:
                print("Invalid choice. Please try again.")
    
    def reports_menu(self):
        """Reports and analytics menu"""
        while True:
            print("\n" + "-"*60)
            print("REPORTS AND ANALYTICS")
            print("-"*60)
            print("1. Room Utilization")
            print("2. Popular Classes")
            print("3. Trainer Workload")
            print("4. Membership Statistics")
            print("5. Class Attendance Stats")
            print("0. Back to main menu")
            print("-"*60)
            
            choice = input("\nEnter your choice: ")
            
            if choice == '1':
                self.room_utilization_report()
            elif choice == '2':
                self.popular_classes_report()
            elif choice == '3':
                self.trainer_workload_report()
            elif choice == '4':
                self.membership_stats_report()
            elif choice == '5':
                self.class_attendance_report()
            elif choice == '0':
                break
            else:
                print("Invalid choice. Please try again.")
    
    # Member Operations Implementation
    def view_all_members(self):
        """View all members"""
        try:
            members = self.member_ops.get_all_members()
            if members:
                headers = ['ID', 'First Name', 'Last Name', 'Email', 'Phone', 
                          'Membership Type', 'Start Date']
                data = [[m['member_id'], m['first_name'], m['last_name'], 
                        m['email'], m['phone'], m['membership_type'], 
                        m['membership_start_date']] for m in members]
                print("\n" + tabulate(data, headers=headers, tablefmt='grid'))
            else:
                print("No members found.")
        except Exception as e:
            print(f"Error: {e}")
    
    def add_new_member(self):
        """Add a new member"""
        try:
            print("\nAdd New Member")
            first_name = input("First Name: ")
            last_name = input("Last Name: ")
            email = input("Email: ")
            phone = input("Phone: ")
            dob = input("Date of Birth (YYYY-MM-DD): ")
            membership_type = input("Membership Type (Basic/Premium/VIP): ")
            start_date = input("Membership Start Date (YYYY-MM-DD): ")
            fitness_goals = input("Fitness Goals: ")
            
            member_id = self.member_ops.add_member(
                first_name, last_name, email, phone, dob,
                membership_type, start_date, fitness_goals
            )
            print(f"\nMember added successfully! Member ID: {member_id}")
        except Exception as e:
            print(f"Error: {e}")
    
    def view_member_details(self):
        """View member details"""
        try:
            member_id = int(input("\nEnter Member ID: "))
            member = self.member_ops.get_member_by_id(member_id)
            if member:
                print("\nMember Details:")
                for key, value in member.items():
                    print(f"{key}: {value}")
            else:
                print("Member not found.")
        except Exception as e:
            print(f"Error: {e}")
    
    def update_member_profile(self):
        """Update member profile"""
        try:
            member_id = int(input("\nEnter Member ID: "))
            print("Enter new values (press Enter to skip):")
            email = input("Email: ")
            phone = input("Phone: ")
            fitness_goals = input("Fitness Goals: ")
            
            updates = {}
            if email: updates['email'] = email
            if phone: updates['phone'] = phone
            if fitness_goals: updates['fitness_goals'] = fitness_goals
            
            if updates:
                self.member_ops.update_member_profile(member_id, **updates)
            else:
                print("No updates provided.")
        except Exception as e:
            print(f"Error: {e}")
    
    def register_for_class(self):
        """Register member for a class"""
        try:
            # Show upcoming classes
            classes = self.admin_ops.get_upcoming_classes()
            if classes:
                headers = ['Class ID', 'Class Name', 'Date', 'Time', 'Trainer', 
                          'Room', 'Available Spots']
                data = [[c['class_id'], c['class_name'], c['class_date'], 
                        f"{c['start_time']}-{c['end_time']}", c['trainer_name'],
                        c['room_name'], c['available_spots']] for c in classes]
                print("\n" + tabulate(data, headers=headers, tablefmt='grid'))
            
            member_id = int(input("\nEnter Member ID: "))
            class_id = int(input("Enter Class ID: "))
            self.member_ops.register_for_class(member_id, class_id)
        except Exception as e:
            print(f"Error: {e}")
    
    def view_member_schedule(self):
        """View member schedule"""
        try:
            member_id = int(input("\nEnter Member ID: "))
            schedule = self.member_ops.get_member_schedule(member_id)
            if schedule:
                headers = ['Class Name', 'Date', 'Start Time', 'End Time', 
                          'Room', 'Status']
                data = [[s['class_name'], s['class_date'], s['start_time'], 
                        s['end_time'], s['room_name'], s['status']] for s in schedule]
                print("\n" + tabulate(data, headers=headers, tablefmt='grid'))
            else:
                print("No scheduled classes found.")
        except Exception as e:
            print(f"Error: {e}")
    
    def view_member_billing(self):
        """View member billing history"""
        try:
            member_id = int(input("\nEnter Member ID: "))
            billing = self.member_ops.get_member_billing_history(member_id)
            if billing:
                headers = ['Billing ID', 'Date', 'Amount', 'Description', 
                          'Status', 'Payment Date']
                data = [[b['billing_id'], b['billing_date'], f"${b['amount']}", 
                        b['description'], b['payment_status'], 
                        b['payment_date']] for b in billing]
                print("\n" + tabulate(data, headers=headers, tablefmt='grid'))
            else:
                print("No billing records found.")
        except Exception as e:
            print(f"Error: {e}")
    
    # Trainer Operations Implementation
    def view_all_trainers(self):
        """View all trainers"""
        try:
            trainers = self.trainer_ops.get_all_trainers()
            if trainers:
                headers = ['ID', 'First Name', 'Last Name', 'Email', 
                          'Specialization', 'Hourly Rate']
                data = [[t['trainer_id'], t['first_name'], t['last_name'], 
                        t['email'], t['specialization'], 
                        f"${t['hourly_rate']}"] for t in trainers]
                print("\n" + tabulate(data, headers=headers, tablefmt='grid'))
            else:
                print("No trainers found.")
        except Exception as e:
            print(f"Error: {e}")
    
    def add_new_trainer(self):
        """Add a new trainer"""
        try:
            print("\nAdd New Trainer")
            first_name = input("First Name: ")
            last_name = input("Last Name: ")
            email = input("Email: ")
            phone = input("Phone: ")
            dob = input("Date of Birth (YYYY-MM-DD): ")
            specialization = input("Specialization: ")
            certification = input("Certification: ")
            hourly_rate = float(input("Hourly Rate: "))
            
            trainer_id = self.trainer_ops.add_trainer(
                first_name, last_name, email, phone, dob,
                specialization, certification, hourly_rate
            )
            print(f"\nTrainer added successfully! Trainer ID: {trainer_id}")
        except Exception as e:
            print(f"Error: {e}")
    
    def view_trainer_schedule(self):
        """View trainer schedule"""
        try:
            trainer_id = int(input("\nEnter Trainer ID: "))
            schedule = self.trainer_ops.get_trainer_schedule(trainer_id)
            if schedule:
                headers = ['Class Name', 'Date', 'Start Time', 'End Time', 
                          'Room', 'Participants']
                data = [[s['class_name'], s['class_date'], s['start_time'], 
                        s['end_time'], s['room_name'], 
                        s['current_participants']] for s in schedule]
                print("\n" + tabulate(data, headers=headers, tablefmt='grid'))
            else:
                print("No scheduled classes found.")
        except Exception as e:
            print(f"Error: {e}")
    
    def schedule_class(self):
        """Schedule a new class"""
        try:
            print("\nSchedule New Class")
            class_name = input("Class Name: ")
            description = input("Description: ")
            trainer_id = int(input("Trainer ID: "))
            room_id = int(input("Room ID: "))
            class_date = input("Date (YYYY-MM-DD): ")
            start_time = input("Start Time (HH:MM): ")
            end_time = input("End Time (HH:MM): ")
            max_participants = int(input("Max Participants: "))
            
            class_id = self.trainer_ops.add_class(
                class_name, description, trainer_id, room_id,
                class_date, start_time, end_time, max_participants
            )
            print(f"\nClass scheduled successfully! Class ID: {class_id}")
        except Exception as e:
            print(f"Error: {e}")
    
    def schedule_personal_session(self):
        """Schedule a personal training session"""
        try:
            print("\nSchedule Personal Training Session")
            member_id = int(input("Member ID: "))
            trainer_id = int(input("Trainer ID: "))
            session_date = input("Date (YYYY-MM-DD): ")
            start_time = input("Start Time (HH:MM): ")
            end_time = input("End Time (HH:MM): ")
            notes = input("Notes: ")
            
            session_id = self.trainer_ops.schedule_personal_session(
                member_id, trainer_id, session_date, start_time, end_time, notes
            )
            print(f"\nSession scheduled successfully! Session ID: {session_id}")
        except Exception as e:
            print(f"Error: {e}")
    
    def view_personal_sessions(self):
        """View personal training sessions"""
        try:
            trainer_id = int(input("\nEnter Trainer ID: "))
            sessions = self.trainer_ops.get_trainer_personal_sessions(trainer_id)
            if sessions:
                headers = ['Session ID', 'Member', 'Date', 'Time', 'Status']
                data = [[s['session_id'], s['member_name'], s['session_date'], 
                        f"{s['start_time']}-{s['end_time']}", 
                        s['status']] for s in sessions]
                print("\n" + tabulate(data, headers=headers, tablefmt='grid'))
            else:
                print("No sessions found.")
        except Exception as e:
            print(f"Error: {e}")
    
    # Admin Operations Implementation
    def room_management(self):
        """Room management submenu"""
        try:
            rooms = self.admin_ops.get_all_rooms()
            if rooms:
                headers = ['ID', 'Room Name', 'Capacity', 'Status']
                data = [[r['room_id'], r['room_name'], r['capacity'], 
                        r['status']] for r in rooms]
                print("\n" + tabulate(data, headers=headers, tablefmt='grid'))
        except Exception as e:
            print(f"Error: {e}")
    
    def equipment_management(self):
        """Equipment management submenu"""
        try:
            equipment = self.admin_ops.get_all_equipment()
            if equipment:
                headers = ['ID', 'Name', 'Type', 'Status', 'Next Maintenance']
                data = [[e['equipment_id'], e['equipment_name'], 
                        e['equipment_type'], e['status'], 
                        e['next_maintenance_date']] for e in equipment]
                print("\n" + tabulate(data, headers=headers, tablefmt='grid'))
        except Exception as e:
            print(f"Error: {e}")
    
    def class_management(self):
        """Class management submenu"""
        try:
            classes = self.admin_ops.get_upcoming_classes()
            if classes:
                headers = ['ID', 'Class Name', 'Date', 'Time', 'Trainer', 
                          'Participants']
                data = [[c['class_id'], c['class_name'], c['class_date'], 
                        f"{c['start_time']}-{c['end_time']}", c['trainer_name'],
                        f"{c['current_participants']}/{c['max_participants']}"
                        ] for c in classes]
                print("\n" + tabulate(data, headers=headers, tablefmt='grid'))
        except Exception as e:
            print(f"Error: {e}")
    
    def billing_management(self):
        """Billing management submenu"""
        try:
            billing = self.admin_ops.get_member_billing_summary()
            if billing:
                headers = ['Member ID', 'Member Name', 'Total Bills', 
                          'Total Paid', 'Pending', 'Overdue']
                data = [[b['member_id'], b['member_name'], b['total_bills'],
                        f"${b['total_paid']}", f"${b['total_pending']}", 
                        f"${b['total_overdue']}" ] for b in billing]
                print("\n" + tabulate(data, headers=headers, tablefmt='grid'))
        except Exception as e:
            print(f"Error: {e}")
    
    # Reports Implementation
    def room_utilization_report(self):
        """Room utilization report"""
        try:
            report = self.admin_ops.get_room_utilization()
            if report:
                headers = ['Room ID', 'Room Name', 'Capacity', 
                          'Classes Scheduled', 'Status']
                data = [[r['room_id'], r['room_name'], r['capacity'],
                        r['classes_scheduled'], r['status']] for r in report]
                print("\n" + tabulate(data, headers=headers, tablefmt='grid'))
        except Exception as e:
            print(f"Error: {e}")
    
    def popular_classes_report(self):
        """Popular classes report"""
        try:
            report = self.admin_ops.get_popular_classes()
            if report:
                headers = ['Class Name', 'Total Registrations', 'Avg Participants']
                data = [[r['class_name'], r['total_registrations'],
                        round(r['avg_participants'], 2)] for r in report]
                print("\n" + tabulate(data, headers=headers, tablefmt='grid'))
        except Exception as e:
            print(f"Error: {e}")
    
    def trainer_workload_report(self):
        """Trainer workload report"""
        try:
            report = self.admin_ops.get_trainer_workload()
            if report:
                headers = ['Trainer ID', 'Trainer Name', 'Total Classes', 
                          'Total Sessions']
                data = [[r['trainer_id'], r['trainer_name'], r['total_classes'],
                        r['total_sessions']] for r in report]
                print("\n" + tabulate(data, headers=headers, tablefmt='grid'))
        except Exception as e:
            print(f"Error: {e}")
    
    def membership_stats_report(self):
        """Membership statistics report"""
        try:
            report = self.admin_ops.get_membership_statistics()
            if report:
                headers = ['Membership Type', 'Member Count']
                data = [[r['membership_type'], r['member_count']] for r in report]
                print("\n" + tabulate(data, headers=headers, tablefmt='grid'))
        except Exception as e:
            print(f"Error: {e}")
    
    def class_attendance_report(self):
        """Class attendance report"""
        try:
            report = self.admin_ops.get_class_attendance_stats()
            if report:
                headers = ['Class ID', 'Class Name', 'Date', 'Max Participants',
                          'Registered', 'Attended', 'Attendance Rate']
                data = [[r['class_id'], r['class_name'], r['class_date'],
                        r['max_participants'], r['registered_count'],
                        r['attended_count'], 
                        f"{r['attendance_rate']}%" if r['attendance_rate'] else 'N/A'
                        ] for r in report]
                print("\n" + tabulate(data, headers=headers, tablefmt='grid'))
        except Exception as e:
            print(f"Error: {e}")
    
    def run(self):
        """Run the main application loop"""
        while True:
            self.display_menu()
            choice = input("\nEnter your choice: ")
            
            if choice == '1':
                self.member_menu()
            elif choice == '2':
                self.trainer_menu()
            elif choice == '3':
                self.admin_menu()
            elif choice == '4':
                self.reports_menu()
            elif choice == '0':
                print("\nThank you for using the Fitness Club Management System!")
                self.db_connection.close_all_connections()
                break
            else:
                print("Invalid choice. Please try again.")


def main():
    """Main entry point"""
    try:
        app = FitnessClubApp()
        app.run()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
