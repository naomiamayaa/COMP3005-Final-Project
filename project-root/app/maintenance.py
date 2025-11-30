from datetime import date
from sqlalchemy.orm import Session

from models.models import (
    Equipment,
    MaintenanceRecords,
    MaintenanceStatus,
    Rooms,
    Users
)


def create_or_update_maintenance(
    db: Session,
    equipment_id: int,
    report_date: date,
    assigned_to: int = None,
    description: str = "",
    status: MaintenanceStatus = MaintenanceStatus.REPORTED
):
    """
    Create a new maintenance record for an equipment item.
    Caller must manage the DB session.
    """
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise ValueError(f"Equipment {equipment_id} does not exist.")

    record = MaintenanceRecords(
        equipment_id=equipment_id,
        report_date=report_date,
        assigned_to=assigned_to,
        description=description,
        status=status
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def list_maintenance_log(
    db: Session,
    status_filter: MaintenanceStatus = None
):
    """
    Return maintenance records with equipment + room + assigned-to details.
    Caller must manage the DB session.
    """

    query = (
        db.query(MaintenanceRecords)
        .join(Equipment)
        .join(Rooms)
        .outerjoin(Users, MaintenanceRecords.assigned_to == Users.id)
    )

    if status_filter:
        query = query.filter(MaintenanceRecords.status == status_filter)

    records = query.order_by(MaintenanceRecords.report_date.desc()).all()

    result = []
    for rec in records:
        result.append({
            "maintenance_id": rec.id,
            "equipment_name": rec.equipment.name,
            "room_number": rec.equipment.room.room_number,
            "status": rec.status.value,
            "report_date": rec.report_date,
            "assigned_to": rec.assigned_to,  
            "description": rec.description
        })

    return result
