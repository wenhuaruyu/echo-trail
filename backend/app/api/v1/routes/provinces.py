from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, request_id
from app.core.errors import AppError
from app.core.responses import success_response
from app.db.session import get_db
from app.models.user import User
from app.repositories.province_repository import get_province, list_provinces
from app.services.province_service import serialize_province


router = APIRouter()


@router.get("")
def get_provinces(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    current_request_id: str = Depends(request_id),
):
    del user
    provinces = list_provinces(db)
    payload = {
        "items": [serialize_province(province) for province in provinces],
        "summary": {"lit_province_count": 0, "ticket_count": 0},
    }
    return success_response(payload, current_request_id)


@router.get("/{province_code}")
def get_province_detail(
    province_code: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    current_request_id: str = Depends(request_id),
):
    del user
    province = get_province(db, province_code)
    if province is None:
        raise AppError(404, "PROVINCE_NOT_FOUND", "省份不存在")
    return success_response(serialize_province(province), current_request_id)

