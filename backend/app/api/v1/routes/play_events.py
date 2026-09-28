from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, request_id
from app.core.responses import success_response
from app.db.session import get_db
from app.models.user import User
from app.schemas.play_event import PlayEventCreate
from app.services.play_event_service import record_play_event


router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_play_event(
    payload: PlayEventCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    current_request_id: str = Depends(request_id),
):
    event = record_play_event(db, user, payload.song_id, payload.event_type)
    return success_response(
        {
            "play_event_id": event.id,
            "song_id": event.song_id,
            "can_create_ticket": True,
            "recorded_at": event.created_at.isoformat(),
        },
        current_request_id,
        "播放记录已保存",
    )

