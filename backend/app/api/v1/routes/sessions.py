from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import request_id
from app.core.responses import success_response
from app.db.session import get_db
from app.schemas.user import AnonymousSessionOut, UserOut
from app.services.auth_service import create_anonymous_session


router = APIRouter()


@router.post("/anonymous", status_code=status.HTTP_201_CREATED)
def create_anonymous(
    db: Session = Depends(get_db),
    current_request_id: str = Depends(request_id),
):
    token, user = create_anonymous_session(db)
    payload = AnonymousSessionOut(
        access_token=token,
        user=UserOut.model_validate(user),
    ).model_dump(mode="json")
    return success_response(payload, current_request_id, "匿名会话创建成功")

