"""initial schema

Revision ID: 030d1ff26402
Revises:
Create Date: 2026-10-18 19:58:05.409649

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "030d1ff26402"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "Anime",
        sa.Column("Id", sa.UUID(), primary_key=True),
        sa.Column("Name", sa.Text(), nullable=False, unique=True),
    )

    op.create_table(
        "Characters",
        sa.Column("Id", sa.UUID(), primary_key=True),
        sa.Column("Name", sa.Text(), nullable=False),
        sa.Column(
            "Elo",
            postgresql.DOUBLE_PRECISION(),
            nullable=False,
            server_default="1500.0",
        ),
        sa.Column("BattleCount", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "AnimeId",
            sa.UUID(),
            sa.ForeignKey("Anime.Id", ondelete="restrict"),
            nullable=False,
        ),
    )

    op.create_table(
        "Cards",
        sa.Column("Id", sa.UUID(), primary_key=True),
        sa.Column("ObjectKey", sa.Text(), nullable=False, unique=True),
        sa.Column(
            "CreatedAt",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
        ),
    )

    op.create_table(
        "CharacterCards",
        sa.Column("Id", sa.UUID(), primary_key=True),
        sa.Column(
            "CardId",
            sa.UUID(),
            sa.ForeignKey("Cards.Id", ondelete="restrict"),
            nullable=False,
        ),
        sa.Column(
            "CharacterId",
            sa.UUID(),
            sa.ForeignKey("Characters.Id", ondelete="restrict"),
            nullable=False,
        ),
    )

    op.create_table(
        "Battles",
        sa.Column("Id", sa.UUID(), primary_key=True),
        sa.Column(
            "CreatedAt",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "ResolvedAt",
            postgresql.TIMESTAMP(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "RoundCount",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )

    op.create_table(
        "BattlePools",
        sa.Column("Id", sa.UUID(), primary_key=True),
        sa.Column(
            "BattleId",
            sa.UUID(),
            sa.ForeignKey("Battles.Id", ondelete="restrict"),
            nullable=False,
        ),
        sa.Column(
            "CharacterId",
            sa.UUID(),
            sa.ForeignKey("Characters.Id", ondelete="restrict"),
            nullable=False,
        ),
    )

    op.create_table(
        "BattleMatches",
        sa.Column("Id", sa.UUID(), primary_key=True),
        sa.Column(
            "BattleId",
            sa.UUID(),
            sa.ForeignKey("Battles.Id", ondelete="restrict"),
            nullable=False,
        ),
        sa.Column("Round", sa.Integer(), nullable=False),
        sa.Column(
            "WinnerId",
            sa.UUID(),
            sa.ForeignKey("Characters.Id", ondelete="restrict"),
            nullable=False,
        ),
        sa.Column(
            "LoserId",
            sa.UUID(),
            sa.ForeignKey("Characters.Id", ondelete="restrict"),
            nullable=False,
        ),
        sa.Column(
            "CreatedAt",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    for table_name in [
        "BattleMatches",
        "BattlePools",
        "Battles",
        "CharacterCards",
        "Cards",
        "Characters",
        "Anime",
    ]:
        op.drop_table(table_name)
