from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.db.session import get_db
from app.models.user import User
from app.services.auth_service import authenticate_token


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise AppError(401, "AUTH_TOKEN_MISSING", "未携带访问令牌")
    user = authenticate_token(db, credentials.credentials)
    if user is None:
        raise AppError(401, "AUTH_TOKEN_INVALID", "访问令牌无效")
    return user


def request_id(request: Request) -> str:
    return request.state.request_id

