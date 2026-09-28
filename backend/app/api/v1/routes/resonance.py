from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, request_id
from app.core.responses import success_response
from app.db.session import get_db
from app.models.user import User
from app.services.statistics_service import get_resonance


router = APIRouter()


@router.get("")
def resonance_detail(
    song_id: str = Query(...),
    province_code: str = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    current_request_id: str = Depends(request_id),
):
    del user
    return success_response(get_resonance(db, province_code, song_id), current_request_id)

