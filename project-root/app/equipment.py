from sqlalchemy.orm import Session
from models.models import Rooms, Equipment, EquipmentStatus

def add_equipment_to_room(
    db: Session,
    room_id: int,
    name: str,
    status: EquipmentStatus = EquipmentStatus.GOOD,
):
    """
    Add equipment to a room.
    Caller must open and manage the database session.
    """

    # Check if the room exists
    room = db.query(Rooms).filter(Rooms.id == room_id).one_or_none()
    if room is None:
        raise ValueError(f"Room with id {room_id} does not exist.")

    # Create the new equipment
    new_equipment = Equipment(
        room_id=room_id,
        name=name,
        status=status
    )

    db.add(new_equipment)
    db.commit()
    db.refresh(new_equipment)

    return new_equipment



def list_equipment_with_rooms(db: Session):
    """
    List all equipment along with their room numbers and status.
    """
    equipments = db.query(Equipment).join(Rooms).all()

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
