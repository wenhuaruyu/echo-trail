import hashlib
import secrets
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import create_user_with_session, find_user_by_token_hash


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_anonymous_session(db: Session) -> Tuple[str, User]:
    raw_token = secrets.token_urlsafe(32)
    user = create_user_with_session(db, hash_token(raw_token))
    return raw_token, user


def authenticate_token(db: Session, raw_token: str) -> Optional[User]:
    return find_user_by_token_hash(db, hash_token(raw_token))

