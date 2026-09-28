from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.song import Song


def list_songs(
    db: Session,
    province_code: Optional[str] = None,
    featured: Optional[bool] = None,
) -> List[Song]:
    statement = select(Song).options(selectinload(Song.provinces)).order_by(Song.title)
    if province_code:
        statement = statement.where(Song.provinces.any(code=province_code))
    if featured is not None:
        statement = statement.where(Song.is_featured == featured)
    return list(db.scalars(statement).unique().all())


def get_song(db: Session, song_id: str) -> Optional[Song]:
    statement = (
        select(Song)
        .options(selectinload(Song.provinces), selectinload(Song.lyrics))
        .where(Song.id == song_id)
    )
    return db.scalar(statement)

