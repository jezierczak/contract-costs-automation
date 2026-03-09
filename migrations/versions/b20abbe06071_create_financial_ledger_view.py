"""create financial ledger view

Revision ID: b20abbe06071
Revises: 131f3d600d22
Create Date: 2026-03-07 15:53:03.441313

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b20abbe06071'
down_revision: Union[str, Sequence[str], None] = '131f3d600d22'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        """
        CREATE OR REPLACE VIEW financial_ledger AS
        SELECT

            frl.id AS line_id,
            frl.organization_id,

            frl.financial_record_id AS record_id,

            COALESCE(fr.selling_date, fr.invoice_date) AS record_date,

            vt.direction AS direction,

            frl.contract_id,
            frl.contract_node_id,

            frl.value_type_id,

            frl.amount_value,
            frl.vat_rate,
            frl.tax_treatment,

            fr.payment_status,
            fr.paid_date,

            fr.status,

            YEAR(COALESCE(fr.selling_date, fr.invoice_date)) AS record_year,
            MONTH(COALESCE(fr.selling_date, fr.invoice_date)) AS record_month

        FROM financial_record_lines frl

        JOIN financial_records fr
            ON fr.id = frl.financial_record_id

        LEFT JOIN value_types vt
            ON vt.id = frl.value_type_id

        WHERE fr.status != 'deleted'
        """
    )

    op.execute(
        """
        CREATE INDEX idx_fr_org_date
        ON financial_records (organization_id,status, selling_date, invoice_date)
        """
    )


def downgrade():
    op.execute(
        """
        DROP VIEW IF EXISTS financial_ledger
        """
    )

    op.execute(
        """
        DROP INDEX idx_fr_org_date ON financial_records
        """
    )
