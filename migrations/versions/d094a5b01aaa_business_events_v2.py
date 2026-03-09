"""business events v2

Revision ID: d094a5b01aaa
Revises: 848ce9c29664
Create Date: 2026-02-27 21:13:13.060874

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd094a5b01aaa'
down_revision: Union[str, Sequence[str], None] = '848ce9c29664'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    # DROP OLD
    op.execute("DROP TABLE IF EXISTS business_events")

    # CREATE NEW
    op.execute("""
    CREATE TABLE business_events (
        id char(36) NOT NULL,
        organization_id char(36) NOT NULL,

        type varchar(16) NOT NULL,
        message text NOT NULL,

        entity_type varchar(64) DEFAULT NULL,
        entity_id char(36) DEFAULT NULL,

        created_at datetime NOT NULL,
        created_by_user_id char(36) DEFAULT NULL,

        PRIMARY KEY (id),

        KEY idx_be_org_created (organization_id, created_at DESC),
        KEY idx_be_entity (entity_type, entity_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)