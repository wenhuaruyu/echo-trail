import uuid

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


song_provinces = Table(
    "song_provinces",
    Base.metadata,
    Column("song_id", String(36), ForeignKey("songs.id", ondelete="CASCADE"), primary_key=True),
    Column("province_code", String(30), ForeignKey("provinces.code", ondelete="CASCADE"), primary_key=True),
)


class Song(Base):
    __tablename__ = "songs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    artist: Mapped[str] = mapped_column(String(100), nullable=False)
    cover_url: Mapped[str] = mapped_column(String(500), nullable=False)
    audio_url: Mapped[str] = mapped_column(String(500), nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    scene_description: Mapped[str] = mapped_column(String(200), nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    provinces = relationship("Province", secondary=song_provinces, back_populates="songs")
    lyrics = relationship(
        "LyricLine", back_populates="song", cascade="all, delete-orphan", order_by="LyricLine.sort_order"
    )

