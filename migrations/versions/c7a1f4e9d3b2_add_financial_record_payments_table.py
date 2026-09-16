"""add financial record payments table

Revision ID: c7a1f4e9d3b2
Revises: aa3c3d8f6c11
Create Date: 2026-09-16 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7a1f4e9d3b2'
down_revision: Union[str, Sequence[str], None] = 'aa3c3d8f6c11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        """
        CREATE TABLE financial_record_payments
        (
            id                 char(36)      NOT NULL,
            organization_id    char(36)      NOT NULL,
            financial_record_id char(36)     NOT NULL,
            amount             decimal(15,2) NOT NULL,
            paid_date          date          NOT NULL,
            created_at         datetime      NOT NULL,
            created_by_user_id char(36)      DEFAULT NULL,
            updated_at         datetime      DEFAULT NULL,
            updated_by_user_id char(36)      DEFAULT NULL,

            PRIMARY KEY (id),

            KEY idx_frp_org (organization_id),
            KEY idx_frp_record (financial_record_id),

            CONSTRAINT fk_frp_financial_record
                FOREIGN KEY (financial_record_id)
                REFERENCES financial_records (id)
                ON DELETE CASCADE
        ) ENGINE = InnoDB
          DEFAULT CHARSET = utf8mb4
          COLLATE = utf8mb4_0900_ai_ci
        """
    )


def downgrade():
    op.execute(
        """
        DROP TABLE IF EXISTS financial_record_payments
        """
    )
