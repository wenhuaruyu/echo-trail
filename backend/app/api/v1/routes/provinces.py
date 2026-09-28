from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, request_id
from app.core.errors import AppError
from app.core.responses import success_response
from app.db.session import get_db
from app.models.user import User
from app.repositories.province_repository import get_province, list_provinces
from app.repositories.song_repository import get_song, list_songs
from app.repositories.ticket_repository import province_ticket_stats, user_ticket_summary
from app.services.song_service import serialize_song
from app.services.province_service import serialize_province


router = APIRouter()


@router.get("")
def get_provinces(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    current_request_id: str = Depends(request_id),
):
    provinces = list_provinces(db)
    payload = {
        "items": [
            serialize_province(province, province_ticket_stats(db, user.id, province.code))
            for province in provinces
        ],
        "summary": user_ticket_summary(db, user.id),
    }
    return success_response(payload, current_request_id)


@router.get("/{province_code}")
def get_province_detail(
    province_code: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    current_request_id: str = Depends(request_id),
):
    province = get_province(db, province_code)
    if province is None:
        raise AppError(404, "PROVINCE_NOT_FOUND", "省份不存在")
    return success_response(
        serialize_province(province, province_ticket_stats(db, user.id, province.code)),
        current_request_id,
    )


@router.get("/{province_code}/song-recommendations")
def get_song_recommendations(
    province_code: str,
    source_song_id: str = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    current_request_id: str = Depends(request_id),
):
    del user
    province = get_province(db, province_code)
    if province is None:
        raise AppError(404, "PROVINCE_NOT_FOUND", "省份不存在")
    if province.status != "available":
        raise AppError(422, "PROVINCE_NOT_AVAILABLE", "当前省份暂未开放票根制作")

    source_song = get_song(db, source_song_id) if source_song_id else None
    if source_song_id and source_song is None:
        raise AppError(404, "SONG_NOT_FOUND", "歌曲不存在")

    candidates = list_songs(db, province_code=province_code, featured=True)
    ordered = []
    if source_song is not None:
        ordered.append(source_song)
    ordered.extend(song for song in candidates if source_song is None or song.id != source_song.id)
    return success_response(
        {
            "province_code": province_code,
            "is_demo_data": True,
            "items": [serialize_song(song) for song in ordered[:3]],
        },
        current_request_id,
    )
