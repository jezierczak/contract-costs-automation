"""schema cleanup

Revision ID: 1af7b19a8780
Revises: 22448d13d143
Create Date: 2026-02-27 20:31:48.576036

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1af7b19a8780'
down_revision: Union[str, Sequence[str], None] = '22448d13d143'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# cleanup migration — no business changes
def upgrade() -> None:
      # ==================================================
    # 1️⃣ organizations — remove duplicate index
    # ==================================================
    op.drop_index("ux_organizations_code", table_name="organizations")

    # ==================================================
    # 2️⃣ contracts — fix char length
    # ==================================================
    op.alter_column(
        "contracts",
        "parent_project_id",
        existing_type=sa.CHAR(length=34),
        type_=sa.CHAR(length=36),
        existing_nullable=True,
    )

    # ==================================================
    # 3️⃣ financial_record_lines — fix char length
    # ==================================================
    op.alter_column(
        "financial_record_lines",
        "agreement_id",
        existing_type=sa.CHAR(length=34),
        type_=sa.CHAR(length=36),
        existing_nullable=True,
    )

    op.alter_column(
        "financial_record_lines",
        "agreement_node_id",
        existing_type=sa.CHAR(length=34),
        type_=sa.CHAR(length=36),
        existing_nullable=True,
    )

    # ==================================================
    # 4️⃣ sessions (optional normalization)
    # ==================================================
    op.alter_column(
        "sessions",
        "id",
        existing_type=sa.String(length=36),
        type_=sa.CHAR(length=36),
        existing_nullable=False,
    )

    op.alter_column(
        "sessions",
        "user_id",
        existing_type=sa.String(length=36),
        type_=sa.CHAR(length=36),
        existing_nullable=False,
    )

    op.alter_column(
        "sessions",
        "organization_id",
        existing_type=sa.String(length=36),
        type_=sa.CHAR(length=36),
        existing_nullable=True,
    )


def downgrade() -> None:
    # intentionally empty (cleanup migration)
    pass
