"""update financial_ledger add buyersellerid contractdata valuetypedata

Revision ID: 9ec5ff85f341
Revises: f4ebb300d30e
Create Date: 2026-03-07 19:45:58.874187

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9ec5ff85f341'
down_revision: Union[str, Sequence[str], None] = 'f4ebb300d30e'
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

            vt.direction,

            fr.buyer_id,
            fr.seller_id,

            frl.contract_id,
            c.contract_type,
            c.owner_id AS contract_owner_id,

            frl.value_type_id,
            vt.code AS value_type_code,
            vt.name AS value_type_name,

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

        LEFT JOIN contracts c
            ON c.id = frl.contract_id

        WHERE fr.status != 'deleted'
        """
    )


def downgrade():
    op.execute(
        """
        CREATE OR REPLACE VIEW financial_ledger AS
        SELECT

            frl.id AS line_id,
            frl.organization_id,
            frl.financial_record_id AS record_id,

            COALESCE(fr.selling_date, fr.invoice_date) AS record_date,

            vt.direction,

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
