from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ResonanceBaseline(Base):
    __tablename__ = "resonance_baselines"

    province_code: Mapped[str] = mapped_column(
        ForeignKey("provinces.code", ondelete="CASCADE"), primary_key=True
    )
    song_id: Mapped[str] = mapped_column(ForeignKey("songs.id", ondelete="CASCADE"), primary_key=True)
    base_count: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class ProvinceMusicInsight(Base):
    __tablename__ = "province_music_insights"
    __table_args__ = (UniqueConstraint("province_code", "scene", name="uq_insight_province_scene"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    province_code: Mapped[str] = mapped_column(ForeignKey("provinces.code", ondelete="CASCADE"), nullable=False)
    scene: Mapped[str] = mapped_column(String(40), nullable=False)
    label: Mapped[str] = mapped_column(String(40), nullable=False)
    song_id: Mapped[str] = mapped_column(ForeignKey("songs.id", ondelete="CASCADE"), nullable=False)
    is_demo_data: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class ProvinceMoodBaseline(Base):
    __tablename__ = "province_mood_baselines"

    province_code: Mapped[str] = mapped_column(
        ForeignKey("provinces.code", ondelete="CASCADE"), primary_key=True
    )
    mood: Mapped[str] = mapped_column(String(20), primary_key=True)
    base_count: Mapped[int] = mapped_column(Integer, nullable=False)

