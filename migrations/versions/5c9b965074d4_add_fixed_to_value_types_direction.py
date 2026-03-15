"""add FIXED to value_types.direction

Revision ID: 5c9b965074d4
Revises: 12a8aab53f1a
Create Date: 2026-03-12 14:41:23.882286

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c9b965074d4'
down_revision: Union[str, Sequence[str], None] = '12a8aab53f1a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
        ALTER TABLE value_types
        DROP CHECK chk_value_types_direction
    """)

    op.execute("""
        ALTER TABLE value_types
        ADD CONSTRAINT chk_value_types_direction
        CHECK (direction IN ('COST','REVENUE','INTERNAL','FIXED'))
    """)


def downgrade():
    op.execute("""
        ALTER TABLE value_types
        DROP CHECK chk_value_types_direction
    """)

    op.execute("""
        ALTER TABLE value_types
        ADD CONSTRAINT chk_value_types_direction
        CHECK (direction IN ('COST','REVENUE','INTERNAL'))
    """)