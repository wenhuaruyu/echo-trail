import random
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, request_id
from app.core.errors import AppError
from app.core.responses import success_response
from app.db.session import get_db
from app.models.user import User
from app.repositories.song_repository import get_song, list_songs
from app.schemas.song import LyricLineOut
from app.services.song_service import serialize_song


router = APIRouter()


@router.get("")
def get_songs(
    province_code: Optional[str] = None,
    featured: Optional[bool] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    current_request_id: str = Depends(request_id),
):
    del user
    songs = list_songs(db, province_code=province_code, featured=featured)
    return success_response(
        {"items": [serialize_song(song) for song in songs]},
        current_request_id,
    )


@router.get("/{song_id}")
def get_song_detail(
    song_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    current_request_id: str = Depends(request_id),
):
    del user
    song = get_song(db, song_id)
    if song is None:
        raise AppError(404, "SONG_NOT_FOUND", "歌曲不存在")
    return success_response(serialize_song(song), current_request_id)


@router.get("/{song_id}/lyrics")
def get_song_lyrics(
    song_id: str,
    limit: int = Query(default=3, ge=1, le=20),
    random_order: bool = Query(default=False, alias="random"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    current_request_id: str = Depends(request_id),
):
    del user
    song = get_song(db, song_id)
    if song is None:
        raise AppError(404, "SONG_NOT_FOUND", "歌曲不存在")
    lyrics = list(song.lyrics)
    if random_order:
        lyrics = random.sample(lyrics, min(limit, len(lyrics)))
    else:
        lyrics = lyrics[:limit]
    items = [LyricLineOut.model_validate(item).model_dump() for item in lyrics]
    return success_response({"song_id": song.id, "items": items}, current_request_id)

