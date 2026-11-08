"""add indexes

Revision ID: 0262409ef150
Revises: 030d1ff26402
Create Date: 2026-10-22 13:32:44.177173

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0262409ef150"
down_revision: str | Sequence[str] | None = "030d1ff26402"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index("ix_BattlePools_BattleId", "BattlePools", ["BattleId"])
    op.create_index("ix_BattleMatches_BattleId", "BattleMatches", ["BattleId"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_BattlePools_BattleId", table_name="BattlePools")
    op.drop_index("ix_BattleMatches_BattleId", table_name="BattleMatches")
