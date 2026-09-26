"""verify companies identified by a valid PESEL or OTH- identifier

Revision ID: a7d2e4f6b8c1
Revises: f1b7c3d9e2a4
Create Date: 2026-09-26 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a7d2e4f6b8c1'
down_revision: Union[str, Sequence[str], None] = 'f1b7c3d9e2a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_valid_pesel(value: str | None) -> bool:
    # kopia CompanyValidator.validate_pesel z dnia migracji
    if not value:
        return False
    value = value.strip()
    if len(value) != 11 or not value.isdigit():
        return False
    weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
    checksum = (10 - sum(int(value[i]) * weights[i] for i in range(10)) % 10) % 10
    return checksum == int(value[10])


def upgrade():
    # f1b7c3d9e2a4 uznawała tylko NIP i VAT UE – osoby z PESEL-em (i numery OTH-)
    # trafiły do weryfikacji niepotrzebnie
    conn = op.get_bind()
    rows = conn.execute(
        sa.text("SELECT id, tax_number FROM companies WHERE verification_status = 'to_verify'")
    ).fetchall()
    for row in rows:
        tax_number = (row.tax_number or "").strip().upper()
        if _is_valid_pesel(tax_number) or tax_number.startswith("OTH-"):
            conn.execute(
                sa.text("UPDATE companies SET verification_status = 'verified' WHERE id = :id"),
                {"id": row.id},
            )


def downgrade():
    # dane – bez cofania (nie wiadomo, które firmy były wcześniej to_verify)
    pass
