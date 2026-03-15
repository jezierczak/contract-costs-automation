"""add amount_input_type to financial ledger view

Revision ID: 5767976b729c
Revises: 5c9b965074d4
Create Date: 2026-03-12 21:05:40.174879

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5767976b729c'
down_revision: Union[str, Sequence[str], None] = '5c9b965074d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():

    op.execute(
        """
        CREATE OR REPLACE VIEW financial_ledger AS
        SELECT
            frl.id AS line_id,
            frl.organization_id AS organization_id,
            frl.financial_record_id AS record_id,

            COALESCE(fr.selling_date, fr.invoice_date) AS record_date,
            YEAR(COALESCE(fr.selling_date, fr.invoice_date)) AS record_year,
            MONTH(COALESCE(fr.selling_date, fr.invoice_date)) AS record_month,

            fr.buyer_id AS buyer_id,
            fr.seller_id AS seller_id,

            vt.direction AS direction,

            frl.contract_id AS contract_id,
            c.code AS contract_code,
            c.contract_type AS contract_type,
            c.owner_id AS contract_owner_id,

            frl.value_type_id AS value_type_id,
            vt.code AS value_type_code,
            vt.name AS value_type_name,

            frl.item_name AS item_name,
            frl.description AS description,

            frl.amount_value AS amount_value,
            frl.amount_input_type AS amount_input_type,

            frl.vat_rate AS vat_rate,
            frl.tax_treatment AS tax_treatment,

            fr.payment_status AS payment_status,
            fr.paid_date AS paid_date,
            fr.status AS status

        FROM financial_record_lines frl

        JOIN financial_records fr
            ON fr.id = frl.financial_record_id

        LEFT JOIN value_types vt
            ON vt.id = frl.value_type_id

        LEFT JOIN contracts c
            ON c.id = frl.contract_id

        WHERE fr.status <> 'deleted'
        """
    )


def downgrade():

    op.execute(
        """
        CREATE OR REPLACE VIEW financial_ledger AS
        SELECT
            frl.id AS line_id,
            frl.organization_id AS organization_id,
            frl.financial_record_id AS record_id,

            COALESCE(fr.selling_date, fr.invoice_date) AS record_date,
            YEAR(COALESCE(fr.selling_date, fr.invoice_date)) AS record_year,
            MONTH(COALESCE(fr.selling_date, fr.invoice_date)) AS record_month,

            fr.buyer_id AS buyer_id,
            fr.seller_id AS seller_id,

            vt.direction AS direction,

            frl.contract_id AS contract_id,
            c.code AS contract_code,
            c.contract_type AS contract_type,
            c.owner_id AS contract_owner_id,

            frl.value_type_id AS value_type_id,
            vt.code AS value_type_code,
            vt.name AS value_type_name,

            frl.item_name AS item_name,
            frl.description AS description,

            frl.amount_value AS amount_value,

            frl.vat_rate AS vat_rate,
            frl.tax_treatment AS tax_treatment,

            fr.payment_status AS payment_status,
            fr.paid_date AS paid_date,
            fr.status AS status

        FROM financial_record_lines frl

        JOIN financial_records fr
            ON fr.id = frl.financial_record_id

        LEFT JOIN value_types vt
            ON vt.id = frl.value_type_id

        LEFT JOIN contracts c
            ON c.id = frl.contract_id

        WHERE fr.status <> 'deleted'
        """
    )