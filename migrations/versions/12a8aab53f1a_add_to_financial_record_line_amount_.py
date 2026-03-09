"""add to financial_record_line amount_input_type column

Revision ID: 12a8aab53f1a
Revises: 312c1372cff9
Create Date: 2026-03-08 12:33:42.153174

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '12a8aab53f1a'
down_revision: Union[str, Sequence[str], None] = '312c1372cff9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    op.add_column(
        "financial_record_lines",
        sa.Column(
            "amount_input_type",
            sa.String(length=16),
            nullable=False,
            server_default="net",
        ),
    )

def downgrade() -> None:
    op.alter_column(
    "financial_record_lines",
    "amount_input_type",
    server_default=None,
)
