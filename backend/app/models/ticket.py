import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        UniqueConstraint("user_id", "idempotency_key", name="uq_tickets_user_idempotency"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_no: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    song_id: Mapped[str] = mapped_column(ForeignKey("songs.id", ondelete="RESTRICT"), index=True, nullable=False)
    province_code: Mapped[str] = mapped_column(
        ForeignKey("provinces.code", ondelete="RESTRICT"), index=True, nullable=False
    )
    ticket_type: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    song_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)
    message: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    location_text: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    lyric_line_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("lyric_lines.id", ondelete="SET NULL"), nullable=True
    )
    lyric_snapshot: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True, nullable=False
    )

    moods: Mapped[List["TicketMood"]] = relationship(
        "TicketMood", back_populates="ticket", cascade="all, delete-orphan", order_by="TicketMood.mood"
    )


class TicketMood(Base):
    __tablename__ = "ticket_moods"

    ticket_id: Mapped[str] = mapped_column(
        ForeignKey("tickets.id", ondelete="CASCADE"), primary_key=True
    )
    mood: Mapped[str] = mapped_column(String(20), primary_key=True)

    ticket: Mapped[Ticket] = relationship("Ticket", back_populates="moods")

