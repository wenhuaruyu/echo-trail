from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models.play_event import PlayEvent
from app.models.user import User
from app.repositories.play_event_repository import create_play_event
from app.repositories.song_repository import get_song


def record_play_event(db: Session, user: User, song_id: str, event_type: str) -> PlayEvent:
    if get_song(db, song_id) is None:
        raise AppError(404, "SONG_NOT_FOUND", "歌曲不存在")
    return create_play_event(db, user.id, song_id, event_type)

