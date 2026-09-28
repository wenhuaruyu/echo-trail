"""创建播放记录、票根和票根心情表。"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260928_0002"
down_revision: Union[str, None] = "20260928_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "play_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("song_id", sa.String(length=36), nullable=False),
        sa.Column("event_type", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["song_id"], ["songs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_play_events_song_id"), "play_events", ["song_id"], unique=False)
    op.create_index(op.f("ix_play_events_user_id"), "play_events", ["user_id"], unique=False)
    op.create_table(
        "tickets",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("ticket_no", sa.String(length=30), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("song_id", sa.String(length=36), nullable=False),
        sa.Column("province_code", sa.String(length=30), nullable=False),
        sa.Column("ticket_type", sa.String(length=20), nullable=False),
        sa.Column("song_snapshot", sa.JSON(), nullable=False),
        sa.Column("message", sa.String(length=60), nullable=True),
        sa.Column("location_text", sa.String(length=20), nullable=True),
        sa.Column("lyric_line_id", sa.String(length=36), nullable=True),
        sa.Column("lyric_snapshot", sa.String(length=200), nullable=True),
        sa.Column("photo_url", sa.String(length=500), nullable=True),
        sa.Column("idempotency_key", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["lyric_line_id"], ["lyric_lines.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["province_code"], ["provinces.code"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["song_id"], ["songs.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "idempotency_key", name="uq_tickets_user_idempotency"),
    )
    op.create_index(op.f("ix_tickets_created_at"), "tickets", ["created_at"], unique=False)
    op.create_index(op.f("ix_tickets_province_code"), "tickets", ["province_code"], unique=False)
    op.create_index(op.f("ix_tickets_song_id"), "tickets", ["song_id"], unique=False)
    op.create_index(op.f("ix_tickets_ticket_no"), "tickets", ["ticket_no"], unique=True)
    op.create_index(op.f("ix_tickets_ticket_type"), "tickets", ["ticket_type"], unique=False)
    op.create_index(op.f("ix_tickets_user_id"), "tickets", ["user_id"], unique=False)
    op.create_table(
        "ticket_moods",
        sa.Column("ticket_id", sa.String(length=36), nullable=False),
        sa.Column("mood", sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(["ticket_id"], ["tickets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("ticket_id", "mood"),
    )


def downgrade() -> None:
    op.drop_table("ticket_moods")
    op.drop_index(op.f("ix_tickets_user_id"), table_name="tickets")
    op.drop_index(op.f("ix_tickets_ticket_type"), table_name="tickets")
    op.drop_index(op.f("ix_tickets_ticket_no"), table_name="tickets")
    op.drop_index(op.f("ix_tickets_song_id"), table_name="tickets")
    op.drop_index(op.f("ix_tickets_province_code"), table_name="tickets")
    op.drop_index(op.f("ix_tickets_created_at"), table_name="tickets")
    op.drop_table("tickets")
    op.drop_index(op.f("ix_play_events_user_id"), table_name="play_events")
    op.drop_index(op.f("ix_play_events_song_id"), table_name="play_events")
    op.drop_table("play_events")

