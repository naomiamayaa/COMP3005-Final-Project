from datetime import date, datetime
from sqlalchemy.orm import Session

# import your functions
from app.maintenance import list_maintenance_log, create_or_update_maintenance
from app.classes import (
    create_class,
    update_class,
    list_classes,
)
from models.models import MaintenanceStatus, ClassType


def admin_dashboard(session: Session):
    """Main admin menu"""
    while True:
        print("\n=== ADMIN DASHBOARD ===")
        print("1. Equipment Management")
        print("2. Class Scheduling")
        print("3. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            equipment_management_menu(session)
        elif choice == "2":
            class_scheduling_menu(session)
        elif choice == "3":
            print("Exiting Admin Dashboard.")
            break
        else:
            print("Invalid choice, try again.")


def equipment_management_menu(session: Session):
    while True:
        print("\n--- Equipment Management ---")
        print("1. View Maintenance Log")
        print("2. Create Maintenance Record")
        print("3. Back")

        choice = input("Choose: ").strip()

        if choice == "1":
            status = input("Status filter (REPORTED, IN_PROGRESS, FIXED or blank): ").upper()
            status_filter = MaintenanceStatus[status] if status in MaintenanceStatus.__members__ else None

            records = list_maintenance_log(db=session, status_filter=status_filter)
            print("\n--- Maintenance Records ---")
            for r in records:
                print(
                    f"[{r['maintenance_id']}] {r['equipment_name']} "
                    f"(Room {r['room_number']}) - {r['status']} "
                    f"on {r['report_date']} | Assigned to: {r['assigned_to']}"
                )

        elif choice == "2":
            equipment_id = int(input("Equipment ID: "))
            assigned_to = input("Assign to user id (blank for none): ")
            assigned_to = int(assigned_to) if assigned_to else None
            description = input("Issue description: ")

            rec = create_or_update_maintenance(
                db=session,
                equipment_id=equipment_id,
                report_date=date.today(),
                assigned_to=assigned_to,
                description=description
            )

            print(f"Created maintenance record {rec.id}.")

        elif choice == "3":
            return
        else:
            print("Invalid choice.")


def class_scheduling_menu(session: Session):
    while True:
        print("\n--- Class Scheduling ---")
        print("1. Create Class")
        print("2. Update Class")
        print("3. View All Classes")
        print("4. Back")

        choice = input("Choose: ").strip()

        if choice == "1":
            trainer_id = int(input("Trainer ID: "))
            room_id = int(input("Room ID: "))
            start_str = input("Start datetime (YYYY-MM-DD HH:MM): ")
            start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M")

            class_type = input("Class type (PT/GROUP): ").upper()
            class_type = ClassType.PT if class_type == "PT" else ClassType.GROUP

            new_cls = create_class(
                db=session,
                trainer_id=trainer_id,
                room_id=room_id,
                start_datetime=start_dt,
                class_type=class_type
            )
            print(f"Created class {new_cls.id}.")

        elif choice == "2":
            class_id = int(input("Class ID: "))
            trainer_id = int(input("New Trainer ID: "))
            room_id = int(input("New Room ID: "))

            start_str = input("New Start datetime (YYYY-MM-DD HH:MM): ")
            end_str = input("New End datetime (YYYY-MM-DD HH:MM): ")

            start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(end_str, "%Y-%m-%d %H:%M")

            class_type = input("Class type (PT/GROUP): ").upper()
            class_type = ClassType.PT if class_type == "PT" else ClassType.GROUP

            updated = update_class(
                db=session,
                class_id=class_id,
                trainer_id=trainer_id,
                room_id=room_id,
                start_datetime=start_dt,
                end_datetime=end_dt,
                class_type=class_type
            )

            print(f"Updated class {updated.id}.")

        elif choice == "3":
            classes = list_classes(session)
            print("\n--- All Classes ---")
            for c in classes:
                print(
                    f"{c['class_id']}: {c['class_type']} "
                    f"from {c['start_datetime']} to {c['end_datetime']}"
                )

        elif choice == "4":
            return

        else:
            print("Invalid choice.")
