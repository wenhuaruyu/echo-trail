"""创建共鸣基数、地区音乐洞察和心情基数表。"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "20260928_0003"
down_revision: Union[str, None] = "20260928_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "resonance_baselines",
        sa.Column("province_code", sa.String(30), nullable=False),
        sa.Column("song_id", sa.String(36), nullable=False),
        sa.Column("base_count", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["province_code"], ["provinces.code"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["song_id"], ["songs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("province_code", "song_id"),
    )
    op.create_table(
        "province_music_insights",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("province_code", sa.String(30), nullable=False),
        sa.Column("scene", sa.String(40), nullable=False),
        sa.Column("label", sa.String(40), nullable=False),
        sa.Column("song_id", sa.String(36), nullable=False),
        sa.Column("is_demo_data", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["province_code"], ["provinces.code"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["song_id"], ["songs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("province_code", "scene", name="uq_insight_province_scene"),
    )
    op.create_table(
        "province_mood_baselines",
        sa.Column("province_code", sa.String(30), nullable=False),
        sa.Column("mood", sa.String(20), nullable=False),
        sa.Column("base_count", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["province_code"], ["provinces.code"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("province_code", "mood"),
    )


def downgrade() -> None:
    op.drop_table("province_mood_baselines")
    op.drop_table("province_music_insights")
    op.drop_table("resonance_baselines")
