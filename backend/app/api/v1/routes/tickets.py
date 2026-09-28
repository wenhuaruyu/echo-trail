from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, request_id
from app.core.errors import AppError
from app.core.responses import success_response
from app.db.session import get_db
from app.models.user import User
from app.repositories.ticket_repository import get_user_ticket, list_user_tickets
from app.schemas.ticket import TicketCreate
from app.services.ticket_service import create_ticket, serialize_ticket


router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_user_ticket(
    payload: TicketCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    current_request_id: str = Depends(request_id),
):
    ticket, province_lighting, created = create_ticket(db, user, payload)
    return success_response(
        {
            "ticket": serialize_ticket(ticket),
            "province_lighting": province_lighting,
            "created": created,
        },
        current_request_id,
        "票根生成成功" if created else "已返回本次请求生成的票根",
    )


@router.get("")
def get_user_tickets(
    province_code: str = None,
    ticket_type: str = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    current_request_id: str = Depends(request_id),
):
    if ticket_type is not None and ticket_type not in {"gold", "silver", "paper"}:
        raise AppError(422, "TICKET_TYPE_INVALID", "票根类型错误")
    tickets, total = list_user_tickets(
        db,
        user.id,
        province_code,
        ticket_type,
        page,
        page_size,
    )
    return success_response(
        {
            "items": [serialize_ticket(ticket) for ticket in tickets],
            "page": page,
            "page_size": page_size,
            "total": total,
            "has_more": page * page_size < total,
        },
        current_request_id,
    )


@router.get("/{ticket_id}")
def get_ticket_detail(
    ticket_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    current_request_id: str = Depends(request_id),
):
    ticket = get_user_ticket(db, user.id, ticket_id)
    if ticket is None:
        raise AppError(404, "TICKET_NOT_FOUND", "票根不存在")
    return success_response(serialize_ticket(ticket), current_request_id)

