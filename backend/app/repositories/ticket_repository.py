from typing import Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.ticket import Ticket


def get_by_idempotency_key(db: Session, user_id: str, key: str) -> Optional[Ticket]:
    statement = (
        select(Ticket)
        .options(selectinload(Ticket.moods))
        .where(Ticket.user_id == user_id, Ticket.idempotency_key == key)
    )
    return db.scalar(statement)


def ticket_number_exists(db: Session, ticket_no: str) -> bool:
    return db.scalar(select(Ticket.id).where(Ticket.ticket_no == ticket_no).limit(1)) is not None


def get_user_ticket(db: Session, user_id: str, ticket_id: str) -> Optional[Ticket]:
    statement = (
        select(Ticket)
        .options(selectinload(Ticket.moods))
        .where(Ticket.id == ticket_id, Ticket.user_id == user_id)
    )
    return db.scalar(statement)


def list_user_tickets(
    db: Session,
    user_id: str,
    province_code: Optional[str],
    ticket_type: Optional[str],
    page: int,
    page_size: int,
) -> Tuple[List[Ticket], int]:
    filters = [Ticket.user_id == user_id]
    if province_code:
        filters.append(Ticket.province_code == province_code)
    if ticket_type:
        filters.append(Ticket.ticket_type == ticket_type)

    total = db.scalar(select(func.count(Ticket.id)).where(*filters)) or 0
    statement = (
        select(Ticket)
        .options(selectinload(Ticket.moods))
        .where(*filters)
        .order_by(Ticket.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return list(db.scalars(statement).all()), total


def province_ticket_stats(db: Session, user_id: str, province_code: str) -> Dict[str, object]:
    types = list(
        db.scalars(
            select(Ticket.ticket_type)
            .where(Ticket.user_id == user_id, Ticket.province_code == province_code)
            .distinct()
        ).all()
    )
    total = db.scalar(
        select(func.count(Ticket.id)).where(
            Ticket.user_id == user_id,
            Ticket.province_code == province_code,
        )
    ) or 0
    ordered_types = [item for item in ("gold", "silver", "paper") if item in types]
    if len(ordered_types) == 3:
        status = "complete"
    elif ordered_types:
        status = "partial"
    else:
        status = "unlit"
    return {
        "lighting_status": status,
        "collected_types": ordered_types,
        "collected_type_count": len(ordered_types),
        "ticket_count": total,
    }


def user_ticket_summary(db: Session, user_id: str) -> Dict[str, int]:
    ticket_count = db.scalar(select(func.count(Ticket.id)).where(Ticket.user_id == user_id)) or 0
    lit_province_count = db.scalar(
        select(func.count(func.distinct(Ticket.province_code))).where(Ticket.user_id == user_id)
    ) or 0
    return {"lit_province_count": lit_province_count, "ticket_count": ticket_count}

