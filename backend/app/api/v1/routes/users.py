from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, request_id
from app.core.responses import success_response
from app.models.user import User
from app.schemas.user import UserOut


router = APIRouter()


@router.get("/me")
def get_me(
    user: User = Depends(get_current_user),
    current_request_id: str = Depends(request_id),
):
    return success_response(
        UserOut.model_validate(user).model_dump(mode="json"),
        current_request_id,
    )

