"""add business events table

Revision ID: 848ce9c29664
Revises: 1af7b19a8780
Create Date: 2026-02-27 20:38:14.575597

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '848ce9c29664'
down_revision: Union[str, Sequence[str], None] = '1af7b19a8780'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "business_events",

        sa.Column("id", sa.CHAR(36), primary_key=True),
        sa.Column("organization_id", sa.CHAR(36), nullable=False),

        sa.Column("aggregate_type", sa.String(50), nullable=False),
        sa.Column("aggregate_id", sa.CHAR(36), nullable=True),

        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),

        sa.Column("payload", sa.JSON(), nullable=True),

        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("created_by_user_id", sa.CHAR(36), nullable=True),
    )

    op.create_index(
        "idx_be_org_time",
        "business_events",
        ["organization_id", "created_at"]
    )

    op.create_index(
        "idx_be_aggregate",
        "business_events",
        ["aggregate_type", "aggregate_id"]
    )


def downgrade() -> None:
    op.drop_index("idx_be_aggregate", table_name="business_events")
    op.drop_index("idx_be_org_time", table_name="business_events")
    op.drop_table("business_events")
