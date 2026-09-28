from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.song import Song
from app.models.statistics import ProvinceMoodBaseline, ProvinceMusicInsight, ResonanceBaseline
from app.models.ticket import Ticket, TicketMood


def get_resonance_baseline(db: Session, province_code: str, song_id: str) -> Optional[ResonanceBaseline]:
    return db.get(ResonanceBaseline, (province_code, song_id))


def count_resonating_users(db: Session, province_code: str, song_id: str) -> int:
    return db.scalar(
        select(func.count(func.distinct(Ticket.user_id))).where(
            Ticket.province_code == province_code,
            Ticket.song_id == song_id,
        )
    ) or 0


def list_insights(db: Session, province_code: str) -> List[Tuple[ProvinceMusicInsight, Song]]:
    statement = (
        select(ProvinceMusicInsight, Song)
        .join(Song, Song.id == ProvinceMusicInsight.song_id)
        .where(ProvinceMusicInsight.province_code == province_code)
    )
    return list(db.execute(statement).all())


def weekly_top_song(db: Session, province_code: str) -> Optional[Tuple[Song, int]]:
    since = datetime.now(timezone.utc) - timedelta(days=7)
    statement = (
        select(Song, func.count(Ticket.id).label("ticket_count"))
        .join(Ticket, Ticket.song_id == Song.id)
        .where(Ticket.province_code == province_code, Ticket.created_at >= since)
        .group_by(Song.id)
        .order_by(func.count(Ticket.id).desc(), Song.title.asc())
        .limit(1)
    )
    row = db.execute(statement).first()
    return (row[0], row[1]) if row else None


def mood_counts(db: Session, province_code: str) -> Dict[str, int]:
    baseline_rows = db.execute(
        select(ProvinceMoodBaseline.mood, ProvinceMoodBaseline.base_count).where(
            ProvinceMoodBaseline.province_code == province_code
        )
    ).all()
    counts = {mood: count for mood, count in baseline_rows}
    real_rows = db.execute(
        select(TicketMood.mood, func.count(TicketMood.ticket_id))
        .join(Ticket, Ticket.id == TicketMood.ticket_id)
        .where(Ticket.province_code == province_code)
        .group_by(TicketMood.mood)
    ).all()
    for mood, count in real_rows:
        counts[mood] = counts.get(mood, 0) + count
    return counts

