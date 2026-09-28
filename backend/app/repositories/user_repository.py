from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.anonymous_session import AnonymousSession
from app.models.user import User


def create_user_with_session(db: Session, token_hash: str) -> User:
    user = User()
    session = AnonymousSession(user=user, token_hash=token_hash)
    db.add_all([user, session])
    db.commit()
    db.refresh(user)
    return user


def find_user_by_token_hash(db: Session, token_hash: str) -> Optional[User]:
    statement = (
        select(User)
        .join(AnonymousSession, AnonymousSession.user_id == User.id)
        .where(AnonymousSession.token_hash == token_hash)
    )
    return db.scalar(statement)

