from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Province(Base):
    __tablename__ = "provinces"

    code: Mapped[str] = mapped_column(String(30), primary_key=True)
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    slogan: Mapped[str] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="placeholder", nullable=False)

    songs = relationship("Song", secondary="song_provinces", back_populates="provinces")

