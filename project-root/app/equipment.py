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
