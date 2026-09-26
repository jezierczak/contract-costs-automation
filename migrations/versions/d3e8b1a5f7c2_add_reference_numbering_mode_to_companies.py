"""add reference numbering mode to companies

Revision ID: d3e8b1a5f7c2
Revises: c7a1f4e9d3b2
Create Date: 2026-09-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'd3e8b1a5f7c2'
down_revision: Union[str, Sequence[str], None] = 'c7a1f4e9d3b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # NULL = nie generuj numerów; monthly / yearly / global = automatyczna numeracja
    # dokumentów tego sprzedawcy (wzór <nr>/<NIP>/<rok>[/<mies>])
    op.execute(
        """
        ALTER TABLE companies
            ADD COLUMN reference_numbering_mode varchar(16) DEFAULT NULL
        """
    )


def downgrade():
    op.execute(
        """
        ALTER TABLE companies
            DROP COLUMN reference_numbering_mode
        """
    )
