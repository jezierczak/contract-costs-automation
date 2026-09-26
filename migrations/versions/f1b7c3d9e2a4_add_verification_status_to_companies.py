"""add verification status to companies

Revision ID: f1b7c3d9e2a4
Revises: e5c9a2f1b8d4
Create Date: 2026-09-26 00:00:00.000000

"""
import re
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'f1b7c3d9e2a4'
down_revision: Union[str, Sequence[str], None] = 'e5c9a2f1b8d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_trusted_tax_number(tax_number: str | None) -> bool:
    # kopia CompanyValidator.is_trusted_tax_number z dnia migracji
    if not tax_number:
        return False
    value = tax_number.strip().upper()
    if value.startswith(("TMP-", "AI-")):
        return False
    if re.fullmatch(r"[A-Z]{2}[0-9A-Z]{2,13}", value) and not value.startswith("PL"):
        return any(ch.isdigit() for ch in value[2:])
    digits = re.sub(r"\D", "", re.sub(r"^\s*PL\s*", "", value))
    if len(digits) != 10:
        return False
    weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
    return sum(int(digits[i]) * weights[i] for i in range(9)) % 11 == int(digits[9])


def upgrade():
    # verified = dane firmy pewne; to_verify = do uzupełnienia przez użytkownika,
    # rekord z taką firmą nie przejdzie walidacji
    op.execute(
        """
        ALTER TABLE companies
            ADD COLUMN verification_status varchar(16) NOT NULL DEFAULT 'verified'
        """
    )

    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT id, tax_number, role FROM companies")).fetchall()
    to_verify = [
        row.id
        for row in rows
        if row.role != "Own" and not _is_trusted_tax_number(row.tax_number)
    ]
    for company_id in to_verify:
        conn.execute(
            sa.text("UPDATE companies SET verification_status = 'to_verify' WHERE id = :id"),
            {"id": company_id},
        )


def downgrade():
    op.execute(
        """
        ALTER TABLE companies
            DROP COLUMN verification_status
        """
    )
