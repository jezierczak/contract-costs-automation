"""update financial_ledger add buyer seller

Revision ID: f4ebb300d30e
Revises: b20abbe06071
Create Date: 2026-03-07 16:35:13.193099

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4ebb300d30e'
down_revision: Union[str, Sequence[str], None] = 'b20abbe06071'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
        CREATE OR REPLACE VIEW financial_ledger AS
        SELECT
            frl.id AS line_id,
            frl.organization_id,
            frl.financial_record_id AS record_id,

            COALESCE(fr.selling_date, fr.invoice_date) AS record_date,

            YEAR(COALESCE(fr.selling_date, fr.invoice_date)) AS record_year,
            MONTH(COALESCE(fr.selling_date, fr.invoice_date)) AS record_month,

            fr.buyer_id,
            fr.seller_id,

            vt.direction,

            frl.contract_id,
            frl.contract_node_id,
            frl.value_type_id,

            frl.amount_value,
            frl.vat_rate,
            frl.tax_treatment,

            fr.payment_status,
            fr.paid_date,
            fr.status

        FROM financial_record_lines frl
        JOIN financial_records fr
            ON fr.id = frl.financial_record_id
        LEFT JOIN value_types vt
            ON vt.id = frl.value_type_id
        WHERE fr.status != 'deleted'
    """)

    def downgrade():
        op.execute("""
                   CREATE OR REPLACE VIEW financial_ledger AS
                   SELECT frl.id                                            AS line_id,
                          frl.organization_id,
                          frl.financial_record_id                           AS record_id,
                          COALESCE(fr.selling_date, fr.invoice_date)        AS record_date,
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
                          YEAR(COALESCE(fr.selling_date, fr.invoice_date))  AS record_year,
                          MONTH(COALESCE(fr.selling_date, fr.invoice_date)) AS record_month
                   FROM financial_record_lines frl
                            JOIN financial_records fr
                                 ON fr.id = frl.financial_record_id
                            LEFT JOIN value_types vt
                                      ON vt.id = frl.value_type_id
                   WHERE fr.status != 'deleted'
                   """)