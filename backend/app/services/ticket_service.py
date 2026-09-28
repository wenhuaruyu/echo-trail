import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models.ticket import Ticket, TicketMood
from app.models.user import User
from app.repositories.play_event_repository import get_play_event
from app.repositories.province_repository import get_province
from app.repositories.song_repository import get_song
from app.repositories.ticket_repository import (
    get_by_idempotency_key,
    province_ticket_stats,
    ticket_number_exists,
)
from app.schemas.ticket import TicketCreate
from app.services.storage_service import photo_storage


TICKET_TYPES = {"gold", "silver", "paper"}
ALLOWED_MOODS = {
    "在路上",
    "想家了",
    "治愈",
    "孤独",
    "自由",
    "怀旧",
    "宁静",
    "热血",
    "迷茫",
    "释然",
    "感动",
    "思念",
}
PROVINCE_ABBREVIATIONS = {"guangdong": "GD", "shaanxi": "SX"}


def _aware_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _validate_text(data: TicketCreate) -> None:
    if data.message is not None and len(data.message) > 60:
        raise AppError(422, "TICKET_MESSAGE_TOO_LONG", "自定义话语最多60字")
    if data.location_text is not None and len(data.location_text) > 20:
        raise AppError(422, "TICKET_LOCATION_TOO_LONG", "具体地点最多20字")
    if len(data.mood_tags) > 3:
        raise AppError(422, "TICKET_MOOD_LIMIT_EXCEEDED", "最多只能选择三个心情标签")
    if len(set(data.mood_tags)) != len(data.mood_tags) or any(
        mood not in ALLOWED_MOODS for mood in data.mood_tags
    ):
        raise AppError(422, "TICKET_MOOD_INVALID", "包含不支持或重复的心情标签")
    if not data.idempotency_key or len(data.idempotency_key) > 100:
        raise AppError(400, "REQUEST_INVALID", "防重复提交编号格式错误")


def _generate_ticket_number(db: Session, province_code: str) -> str:
    abbreviation = PROVINCE_ABBREVIATIONS[province_code]
    year = datetime.now(timezone.utc).year
    for _ in range(50):
        number = 1000 + secrets.randbelow(9000)
        ticket_no = "ET-{}-{}-{}".format(abbreviation, year, number)
        if not ticket_number_exists(db, ticket_no):
            return ticket_no
    raise AppError(500, "INTERNAL_ERROR", "票根编号生成失败")


def serialize_ticket(ticket: Ticket) -> Dict[str, object]:
    return {
        "id": ticket.id,
        "ticket_no": ticket.ticket_no,
        "province_code": ticket.province_code,
        "ticket_type": ticket.ticket_type,
        "song_id": ticket.song_id,
        "song_snapshot": ticket.song_snapshot,
        "message": ticket.message,
        "location_text": ticket.location_text,
        "mood_tags": [item.mood for item in ticket.moods],
        "lyric_snapshot": ticket.lyric_snapshot,
        "photo_url": ticket.photo_url,
        "created_at": ticket.created_at.isoformat(),
    }


def create_ticket(
    db: Session,
    user: User,
    data: TicketCreate,
) -> Tuple[Ticket, Dict[str, object], bool]:
    existing = get_by_idempotency_key(db, user.id, data.idempotency_key)
    if existing is not None:
        return existing, province_ticket_stats(db, user.id, existing.province_code), False

    _validate_text(data)
    if data.ticket_type not in TICKET_TYPES:
        raise AppError(422, "TICKET_TYPE_INVALID", "票根类型错误")

    province = get_province(db, data.province_code)
    if province is None:
        raise AppError(404, "PROVINCE_NOT_FOUND", "省份不存在")
    if province.status != "available":
        raise AppError(422, "PROVINCE_NOT_AVAILABLE", "当前省份暂未开放票根制作")

    song = get_song(db, data.song_id)
    if song is None:
        raise AppError(404, "SONG_NOT_FOUND", "歌曲不存在")

    play_event = get_play_event(db, data.play_event_id)
    if play_event is None or play_event.user_id != user.id:
        raise AppError(422, "PLAY_EVENT_REQUIRED", "需要先播放当前歌曲")
    if play_event.song_id != data.song_id:
        raise AppError(422, "PLAY_EVENT_REQUIRED", "播放记录与当前歌曲不匹配")
    if datetime.now(timezone.utc) - _aware_datetime(play_event.created_at) > timedelta(hours=24):
        raise AppError(422, "PLAY_EVENT_REQUIRED", "播放记录已过期，请重新播放歌曲")

    if data.ticket_type == "silver" and not data.photo_url:
        raise AppError(422, "TICKET_PHOTO_REQUIRED", "烫银票必须添加照片")
    if data.ticket_type == "silver" and data.photo_url and not photo_storage.owns_photo_url(data.photo_url):
        raise AppError(422, "TICKET_PHOTO_INVALID", "烫银票照片必须由本服务上传")
    if data.ticket_type != "silver" and data.photo_url:
        raise AppError(422, "TICKET_PHOTO_NOT_ALLOWED", "当前票根类型不能添加照片")

    lyric = None
    if data.lyric_line_id:
        lyric = next((item for item in song.lyrics if item.id == data.lyric_line_id), None)
        if lyric is None:
            raise AppError(422, "LYRIC_NOT_IN_SONG", "所选歌词不属于当前歌曲")

    ticket = Ticket(
        ticket_no=_generate_ticket_number(db, data.province_code),
        user_id=user.id,
        song_id=song.id,
        province_code=province.code,
        ticket_type=data.ticket_type,
        song_snapshot={
            "title": song.title,
            "artist": song.artist,
            "cover_url": song.cover_url,
        },
        message=data.message,
        location_text=data.location_text,
        lyric_line_id=lyric.id if lyric else None,
        lyric_snapshot=lyric.content if lyric else None,
        photo_url=data.photo_url,
        idempotency_key=data.idempotency_key,
    )
    ticket.moods = [TicketMood(mood=mood) for mood in data.mood_tags]
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    stats = province_ticket_stats(db, user.id, province.code)
    return ticket, stats, True
