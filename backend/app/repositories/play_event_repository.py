from typing import Optional

from sqlalchemy.orm import Session

from app.models.play_event import PlayEvent


def create_play_event(db: Session, user_id: str, song_id: str, event_type: str) -> PlayEvent:
    event = PlayEvent(user_id=user_id, song_id=song_id, event_type=event_type)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_play_event(db: Session, event_id: str) -> Optional[PlayEvent]:
    return db.get(PlayEvent, event_id)

