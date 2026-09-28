from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models import anonymous_session, lyric_line, province, song, user  # noqa: E402,F401

