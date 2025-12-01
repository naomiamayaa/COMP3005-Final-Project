from datetime import date, datetime
from sqlalchemy.orm import Session

from app.maintenance import list_maintenance_log, create_or_update_maintenance
from app.classes import (
    create_class,
    update_class,
    list_classes,
    get_available_trainers_and_rooms,
)
from app.scheduling import add_room_availability
from models.models import MaintenanceStatus, ClassType, Equipment, Rooms


# ============================================================
#                        ADMIN DASHBOARD
# ============================================================

def admin_dashboard(session: Session, user):
    """Main admin menu."""
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


# ============================================================
#                  EQUIPMENT & MAINTENANCE
# ============================================================

def list_equipment_with_rooms(session: Session):
    """Print all equipment and their rooms."""
    equipments = session.query(Equipment).join(Rooms).all()

    if not equipments:
        print("No equipment found.")
        return []

    print("\n--- Equipment List ---")
    result = []

    for eq in equipments:
        room_number = eq.room.room_number if eq.room else "Unknown"
        status = eq.status.value if eq.status else "Unknown"

        print(f"ID: {eq.id} | Name: {eq.name} | Room: {room_number} | Status: {status}")

        result.append({
            "equipment_id": eq.id,
            "name": eq.name,
            "room_number": room_number,
            "status": status
        })

    return result


def equipment_management_menu(session: Session):
    """Equipment and maintenance menu."""
    while True:
        print("\n--- Equipment Management ---")
        print("1. View Maintenance Log")
        print("2. Create Maintenance Record")
        print("3. Back")

        choice = input("Choose: ").strip()

        # --------------------------
        # 1. VIEW MAINTENANCE LOG
        # --------------------------
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

        # --------------------------
        # 2. CREATE MAINTENANCE RECORD
        # --------------------------
        elif choice == "2":
            try:
                list_equipment_with_rooms(session)

                equipment_id = int(input("Enter Equipment ID: "))
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

            except ValueError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")

        elif choice == "3":
            return
        else:
            print("Invalid choice.")


# ============================================================
#                    CLASS SCHEDULING MENU
# ============================================================

def class_scheduling_menu(session: Session):
    """Admin menu for class creation, updates, and room availability."""
    while True:
        print("\n--- Class Scheduling ---")
        print("1. Create Class")
        print("2. Update Class")
        print("3. View All Classes")
        print("4. Add Room Availability")
        print("5. Back")

        choice = input("Choose: ").strip()

        # --------------------------
        # 1. CREATE CLASS
        # --------------------------
        if choice == "1":
            try:
                start_str = input("Enter class start datetime (YYYY-MM-DD HH:MM): ")
                start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M")

                available_trainers, available_rooms = get_available_trainers_and_rooms(
                    session, start_dt
                )

                if not available_trainers:
                    print("No trainers available at this time.")
                    continue
                print("\nAvailable Trainers:")
                for t in available_trainers:
                    print(f"{t.id}: {t.first_name} {t.last_name}")

                if not available_rooms:
                    print("No rooms available at this time.")
                    continue
                print("\nAvailable Rooms:")
                for r in available_rooms:
                    print(f"{r.id}: Room {r.room_number} (Capacity {r.capacity})")

                trainer_id = int(input("Select Trainer ID: "))
                room_id = int(input("Select Room ID: "))

                class_type_str = input("Class type (PT/GROUP): ").upper()
                if class_type_str not in ["PT", "GROUP"]:
                    print("Invalid class type.")
                    continue

                class_type = ClassType.PT if class_type_str == "PT" else ClassType.GROUP

                new_cls = create_class(
                    db=session,
                    trainer_id=trainer_id,
                    room_id=room_id,
                    start_datetime=start_dt,
                    class_type=class_type
                )

                print(f"Created class {new_cls.id}.")

            except ValueError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")

        # --------------------------
        # 2. UPDATE CLASS
        # --------------------------
        elif choice == "2":
            try:
                class_id = int(input("Class ID: "))
                trainer_id = int(input("New Trainer ID: "))
                room_id = int(input("New Room ID: "))
                start_str = input("New Start datetime (YYYY-MM-DD HH:MM): ")
                end_str = input("New End datetime (YYYY-MM-DD HH:MM): ")

                try:
                    start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
                    end_dt = datetime.strptime(end_str, "%Y-%m-%d %H:%M")
                except ValueError:
                    print("Invalid datetime format.")
                    continue

                class_type_str = input("Class type (PT/GROUP): ").upper()
                if class_type_str not in ["PT", "GROUP"]:
                    print("Invalid class type.")
                    continue

                class_type = ClassType.PT if class_type_str == "PT" else ClassType.GROUP

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

            except ValueError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")

        # --------------------------
        # 3. VIEW CLASSES
        # --------------------------
        elif choice == "3":
            try:
                classes = list_classes(session)
                print("\n--- All Classes ---")
                for c in classes:
                    print(
                        f"{c['class_id']}: {c['class_type']} | Trainer: {c['trainer_name']} | "
                        f"Room: {c['room_number']} | {c['start_datetime']} → {c['end_datetime']}"
                    )
            except Exception as e:
                print(f"Error fetching classes: {e}")

        # --------------------------
        # 4. ADD ROOM AVAILABILITY
        # --------------------------
        elif choice == "4":
            add_room_availability_menu(session)

        elif choice == "5":
            return
        else:
            print("Invalid choice.")


# ============================================================
#               ADD ROOM AVAILABILITY (ADMIN)
# ============================================================

def add_room_availability_menu(session: Session):
    """Menu UI for creating room availability."""

    print("\n--- Add Room Availability ---")

    rooms = session.query(Rooms).all()
    if not rooms:
        print("No rooms found.")
        return

    print("\nAvailable Rooms:")
    for r in rooms:
        print(f"{r.id}: Room {r.room_number} (Capacity {r.capacity})")

    try:
        room_id = int(input("Enter Room ID: "))

        start_date_str = input("Start date (YYYY-MM-DD): ")
        end_date_str = input("End date (YYYY-MM-DD): ")
        start_time_str = input("Start time (HH:MM): ")
        end_time_str = input("End time (HH:MM): ")

        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        end_time = datetime.strptime(end_time_str, "%H:%M").time()

        new_block = add_room_availability(
            db=session,
            room_id=room_id,
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time
        )

        print(f"Room availability created successfully! ID = {new_block.id}")

    except ValueError as e:
        print(f"Invalid input: {e}")
    except Exception as e:
        print(f"Error: {e}")
