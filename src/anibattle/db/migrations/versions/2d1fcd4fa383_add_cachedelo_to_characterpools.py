"""add 'CachedElo' to 'CharacterPools'

Revision ID: 2d1fcd4fa383
Revises: 0262409ef150
Create Date: 2026-10-25 20:45:34.243522

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "2d1fcd4fa383"
down_revision: str | Sequence[str] | None = "0262409ef150"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "BattlePools",
        sa.Column(
            "CachedElo",
            postgresql.DOUBLE_PRECISION(),
            nullable=False,
            server_default=sa.text("1000.0"),
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("BattlePools", "CachedElo")
