"""创建匿名用户、省份、歌曲和歌词基础表。"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260928_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "provinces",
        sa.Column("code", sa.String(length=30), nullable=False),
        sa.Column("name", sa.String(length=20), nullable=False),
        sa.Column("slogan", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("code"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "songs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("artist", sa.String(length=100), nullable=False),
        sa.Column("cover_url", sa.String(length=500), nullable=False),
        sa.Column("audio_url", sa.String(length=500), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=False),
        sa.Column("scene_description", sa.String(length=200), nullable=True),
        sa.Column("is_featured", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_songs_slug"), "songs", ["slug"], unique=True)
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("display_name", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "anonymous_sessions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_anonymous_sessions_token_hash"), "anonymous_sessions", ["token_hash"], unique=True)
    op.create_table(
        "lyric_lines",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("song_id", sa.String(length=36), nullable=False),
        sa.Column("content", sa.String(length=200), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["song_id"], ["songs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "song_provinces",
        sa.Column("song_id", sa.String(length=36), nullable=False),
        sa.Column("province_code", sa.String(length=30), nullable=False),
        sa.ForeignKeyConstraint(["province_code"], ["provinces.code"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["song_id"], ["songs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("song_id", "province_code"),
    )


def downgrade() -> None:
    op.drop_table("song_provinces")
    op.drop_table("lyric_lines")
    op.drop_index(op.f("ix_anonymous_sessions_token_hash"), table_name="anonymous_sessions")
    op.drop_table("anonymous_sessions")
    op.drop_table("users")
    op.drop_index(op.f("ix_songs_slug"), table_name="songs")
    op.drop_table("songs")
    op.drop_table("provinces")

