# app/cli/trainer_pov.py

from datetime import datetime

from sqlalchemy import or_

from models.database import SessionLocal
from models.models import Users, UserRole

# ---- domain functions you already implemented elsewhere ----
from app.scheduling import add_availability, get_trainer_schedule
# TODO: adjust this import to wherever you defined these:
from app.member_lookup import allow_lookup_member, lookup_member


# ========== small helpers for parsing input ==========

def _prompt_date(label: str):
    """Prompt for a date in YYYY-MM-DD format."""
    while True:
        raw = input(f"{label} (YYYY-MM-DD): ").strip()
        try:
            return datetime.strptime(raw, "%Y-%m-%d").date()
        except ValueError:
            print("  ❌ Invalid date format. Please use YYYY-MM-DD.")


def _prompt_time(label: str):
    """Prompt for a time in HH:MM (24h) format."""
    while True:
        raw = input(f"{label} (HH:MM, 24h): ").strip()
        try:
            return datetime.strptime(raw, "%H:%M").time()
        except ValueError:
            print("  ❌ Invalid time format. Please use HH:MM (24h clock).")


def _print_trainer_schedule(classes):
    if not classes:
        print("\nYou have no upcoming classes or PT sessions.")
        return

    print("\nYour upcoming classes / PT sessions:")
    print("-" * 72)
    for cls in classes:
        start_str = cls.start_datetime.strftime("%Y-%m-%d %H:%M")
        end_str = cls.end_datetime.strftime("%H:%M")
        class_type = getattr(cls.class_type, "value", str(cls.class_type))
        room_id = getattr(cls, "room_id", "N/A")

        print(
            f"ID {cls.id:3d} | {class_type:<5} | {start_str}–{end_str} | Room {room_id}"
        )
    print("-" * 72)


# ========== handlers for each menu option ==========

def _handle_set_availability(user):
    """
    CLI wrapper for add_availability(...) for the logged-in trainer.
    """
    print("\n=== Set Availability ===")
    print("You are defining when you are available to take sessions/classes.")
    print("Overlapping blocks are not allowed.\n")

    start_date = _prompt_date("Start date")
    end_date = _prompt_date("End date")
    start_time = _prompt_time("Start time")
    end_time = _prompt_time("End time")

    with SessionLocal() as db:
        try:
            block = add_availability(
                db=db,
                trainer_id=user.id,
                start_date=start_date,
                end_date=end_date,
                start_time=start_time,
                end_time=end_time,
            )
        except ValueError as e:
            print(f"\n❌ Could not save availability: {e}")
            return

        print("\n✅ Availability saved:")
        print(
            f"  Dates: {block.start_date} to {block.end_date}\n"
            f"  Time:  {block.start_time.strftime('%H:%M')}–"
            f"{block.end_time.strftime('%H:%M')}"
        )


def _handle_schedule_view(user):
    """
    CLI wrapper for get_trainer_schedule(...).
    """
    print("\n=== Trainer Schedule ===")

    with SessionLocal() as db:
        try:
            classes = get_trainer_schedule(db, trainer_id=user.id)
        except ValueError as e:
            print(f"❌ Error loading schedule: {e}")
            return

        _print_trainer_schedule(classes)


def _handle_member_lookup(user):
    """
    Member Lookup:
      - Search by name (case insensitive)
      - Trainer is only allowed if they have an upcoming PT session with that member
      - Show current goal and last metric (read-only)
    """
    print("\n=== Member Lookup ===")
    name_query = input("Enter member first or last name (partial is OK): ").strip()

    if not name_query:
        print("❌ Name cannot be empty.")
        return

    with SessionLocal() as db:
        # 1) Find candidate members by name
        pattern = f"%{name_query}%"
        matches = (
            db.query(Users)
            .filter(Users.role == UserRole.MEMBER)
            .filter(
                or_(
                    Users.first_name.ilike(pattern),
                    Users.last_name.ilike(pattern),
                )
            )
            .order_by(Users.last_name.asc(), Users.first_name.asc())
            .all()
        )

        if not matches:
            print("No members found with that name.")
            return

        print("\nMatching members:")
        for m in matches:
            print(f"  {m.id}: {m.first_name} {m.last_name} ({m.email})")

        # 2) Choose a specific member by ID
        chosen_id = None
        while True:
            raw = input(
                "\nEnter the member ID to view details (or 'c' to cancel): "
            ).strip()
            if raw.lower() == "c":
                return
            if not raw.isdigit():
                print("  Please enter a numeric member ID.")
                continue

            candidate_id = int(raw)
            if any(m.id == candidate_id for m in matches):
                chosen_id = candidate_id
                break
            else:
                print("  That ID is not in the list above.")

        # 3) Check whether trainer is allowed to look them up
        try:
            allowed = allow_lookup_member(
                session=db,
                trainer_id=user.id,
                member_id=chosen_id,
            )
        except Exception as e:
            print(f"❌ Could not verify lookup permission: {e}")
            return

        if not allowed:
            print(
                "\n❌ You can only view details for members you have an upcoming "
                "PT session with."
            )
            return

        # 4) Fetch current goal & last metric
        try:
            current_goal, last_metric = lookup_member(db, member_id=chosen_id)
        except ValueError as e:
            print(f"❌ Error looking up member: {e}")
            return

        selected = next(m for m in matches if m.id == chosen_id)

        print("\n--- Member Summary ---")
        print(f"Name:  {selected.first_name} {selected.last_name}")
        print(f"Email: {selected.email}")

        # Current goal
        if current_goal:
            print("\nCurrent Goal:")
            print(f"  Target body fat % : {current_goal.body_fat_percent}")
            print(f"  Target weight (kg): {current_goal.target_weight}")
        else:
            print("\nCurrent Goal: none set yet.")

        # Last health metric
        if last_metric:
            print("\nLast Recorded Health Metric:")
            print(f"  Date recorded : {last_metric.date_recorded}")
            print(f"  Weight (kg)   : {last_metric.weight_kg}")
            print(f"  Body fat %    : {last_metric.body_fat_percent}")
        else:
            print("\nLast Recorded Health Metric: none recorded yet.")


# ========== main menu ==========

def trainer_pov(user):
    """
    Trainer Point-of-View CLI menu.
    `user` is the logged-in trainer ORM object (Users row with role=TRAINER).
    """
    print(f"\nWelcome, {user.first_name} {user.last_name} (Trainer)")

    while True:
        print("\nTrainer Dashboard")
        print("1. Set Availability")
        print("2. Schedule View")
        print("3. Member Lookup")
        print("4. Sign Out")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            _handle_set_availability(user)

        elif choice == "2":
            _handle_schedule_view(user)

        elif choice == "3":
            _handle_member_lookup(user)

        elif choice == "4":
            print("Signing out...")
            break

        else:
            print("Invalid choice. Please enter a number between 1–4.")
