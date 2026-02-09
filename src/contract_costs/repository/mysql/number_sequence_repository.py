from uuid import UUID

from contract_costs.model.number_sequence import NumberSequence
from contract_costs.repository.number_sequence_repository import (
    NumberSequenceRepository,
)


class MySQLNumberSequenceRepository(NumberSequenceRepository):

    def get_for_update(
        self,
        conn,
        organization_id: UUID,
        scope_key: str,
    ) -> NumberSequence | None:

        cur = conn.cursor(dictionary=True)

        cur.execute(
            """
            SELECT *
            FROM number_sequences
            WHERE organization_id = %s
              AND scope_key = %s
            FOR UPDATE
            """,
            (str(organization_id), scope_key),
        )

        row = cur.fetchone()
        cur.close()

        if not row:
            return None

        return NumberSequence(
            organization_id=UUID(row["organization_id"]),
            scope_key=row["scope_key"],
            current_value=row["current_value"],
        )

    def add(
        self,
        conn,
        sequence: NumberSequence,
    ) -> None:

        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO number_sequences (
                organization_id,
                scope_key,
                current_value,
                created_at,
                updated_at
            )
            VALUES (%s, %s, %s, NOW(6), NOW(6))
            """,
            (
                str(sequence.organization_id),
                sequence.scope_key,
                sequence.current_value,
            ),
        )

        cur.close()

    def save(
        self,
        conn,
        sequence: NumberSequence,
    ) -> None:

        cur = conn.cursor()

        cur.execute(
            """
            UPDATE number_sequences
            SET current_value = %s,
                updated_at = NOW(6)
            WHERE organization_id = %s
              AND scope_key = %s
            """,
            (
                sequence.current_value,
                str(sequence.organization_id),
                sequence.scope_key,
            ),
        )

        cur.close()
