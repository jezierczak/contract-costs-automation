"""add company ksef settings table

Revision ID: aa3c3d8f6c11
Revises: 5767976b729c
Create Date: 2026-03-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "aa3c3d8f6c11"
down_revision: Union[str, Sequence[str], None] = "5767976b729c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE company_ksef_settings (
            id char(36) NOT NULL,
            organization_id char(36) NOT NULL,
            company_id char(36) NOT NULL,
            environment varchar(16) NOT NULL,
            is_enabled tinyint(1) NOT NULL DEFAULT 0,
            certificate_path varchar(512) DEFAULT NULL,
            certificate_password varchar(255) DEFAULT NULL,
            last_import_from date DEFAULT NULL,
            last_import_at datetime DEFAULT NULL,
            last_error text DEFAULT NULL,
            created_at datetime NOT NULL,
            created_by_user_id char(36) DEFAULT NULL,
            updated_at datetime NOT NULL,
            updated_by_user_id char(36) DEFAULT NULL,
            PRIMARY KEY (id),
            UNIQUE KEY uq_company_ksef_settings_company (company_id),
            KEY idx_company_ksef_settings_org_company (organization_id, company_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS company_ksef_settings")
