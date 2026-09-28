import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LyricLine(Base):
    __tablename__ = "lyric_lines"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    song_id: Mapped[str] = mapped_column(ForeignKey("songs.id", ondelete="CASCADE"), nullable=False)
    content: Mapped[str] = mapped_column(String(200), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    song = relationship("Song", back_populates="lyrics")

