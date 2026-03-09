"""add scoring to documents

Revision ID: 131f3d600d22
Revises: d094a5b01aaa
Create Date: 2026-03-03 18:45:40.135820

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '131f3d600d22'
down_revision: Union[str, Sequence[str], None] = 'd094a5b01aaa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("score", sa.Integer(), nullable=True),
    )

    op.add_column(
        "documents",
        sa.Column("scoring_breakdown", sa.JSON(), nullable=True),
    )



def downgrade() -> None:
    op.drop_column("documents", "scoring_breakdown")
    op.drop_column("documents", "score")