"""add ksef_number to documents

Revision ID: e5c9a2f1b8d4
Revises: d3e8b1a5f7c2
Create Date: 2026-09-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'e5c9a2f1b8d4'
down_revision: Union[str, Sequence[str], None] = 'd3e8b1a5f7c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# numer KSeF: <NIP 10 cyfr>-<RRRRMMDD>-<12 znaków hex>-<2 znaki hex>
KSEF_NUMBER_PATTERN = "[0-9]{10}-[0-9]{8}-[0-9A-F]{12}-[0-9A-F]{2}"


def upgrade():
    op.execute(
        """
        ALTER TABLE documents
            ADD COLUMN ksef_number varchar(64) DEFAULT NULL,
            ADD KEY idx_documents_org_ksef_number (organization_id, ksef_number)
        """
    )
    # dokumenty, które wciąż mają numer KSeF w nazwie/ścieżce pliku (z importu
    # przed przeniesieniem do katalogu firmy); resztę uzupełni ponowny import z KSeF
    op.execute(
        f"""
        UPDATE documents
        SET ksef_number = REGEXP_SUBSTR(file_path, '{KSEF_NUMBER_PATTERN}', 1, 1, 'c')
        WHERE ksef_number IS NULL
          AND REGEXP_LIKE(file_path, '{KSEF_NUMBER_PATTERN}', 'c')
        """
    )


def downgrade():
    op.execute(
        """
        ALTER TABLE documents
            DROP KEY idx_documents_org_ksef_number,
            DROP COLUMN ksef_number
        """
    )
