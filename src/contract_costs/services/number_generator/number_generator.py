from datetime import datetime
from uuid import UUID


from contract_costs.model.number_sequence import NumberSequence

from contract_costs.unit_of_work import UnitOfWork


class NumberGenerator:

    # def __init__(
    #     self,
    #     # uow: UnitOfWork,
    #     # number_sequence_repository: NumberSequenceRepository,
    # ):
    #     # self._repo = number_sequence_repository
    #     # self._unit_of_work = uow

    def generate(
        self,
        uow: UnitOfWork,
        organization_id: UUID,
        pattern: str,
        date: datetime,
    ) -> str:

        # 1️⃣ Najpierw resolve bez <auto>
        resolved_without_auto = self._resolve_context(pattern, date)

        # 2️⃣ Jeśli brak <auto> → nie dotykamy DB
        if "<auto>" not in pattern:
            return resolved_without_auto

        # 3️⃣ Budujemy scope_key
        scope_key = self._build_scope_key(resolved_without_auto)

        # 4️⃣ Pobieramy kolejny numer
        next_value = self._get_next_value(
            uow=uow,
            organization_id=organization_id,
            scope_key=scope_key,
        )

        # 5️⃣ Wstawiamy <auto>
        final_number = resolved_without_auto.replace(
            "<auto>",
            str(next_value),
        )

        return final_number

    # --------------------------------------------------
    # PRIVATE
    # --------------------------------------------------

    def _get_next_value(
        self,
        uow: UnitOfWork,
        organization_id: UUID,
        scope_key: str,
    ) -> int:
        sequence = uow.number_sequences.get_for_update(
            organization_id,
            scope_key,
        )

        if sequence is None:
            sequence = NumberSequence(
                organization_id=organization_id,
                scope_key=scope_key,
                current_value=1,
            )
            uow.number_sequences.add(sequence)
            return 1

        next_value = sequence.increase()
        uow.number_sequences.update(sequence)
        return next_value
        # conn = get_connection()
        #
        # try:
        #     conn.start_transaction()
        #
        #     sequence = self._repo.get_for_update(
        #         conn,
        #         organization_id,
        #         scope_key,
        #     )
        #
        #     if sequence is None:
        #         sequence = NumberSequence(
        #             organization_id=organization_id,
        #             scope_key=scope_key,
        #             current_value=1,
        #         )
        #         self._repo.add(conn, sequence)
        #         next_value = 1
        #     else:
        #         next_value = sequence.increase()
        #         self._repo.save(conn, sequence)
        #
        #     conn.commit()
        #
        # except Exception:
        #     conn.rollback()
        #     raise
        # finally:
        #     conn.close()
        #
        # return next_value

    @staticmethod
    def _resolve_context(
        pattern: str,
        date: datetime,
    ) -> str:

        result = pattern

        result = result.replace("<Y>", str(date.year))
        result = result.replace("<m>", f"{date.month:02d}")

        return result

    @staticmethod
    def _build_scope_key(
        resolved_pattern: str,
    ) -> str:
        """
        Budujemy scope bez <auto>.
        Usuwamy placeholder i ewentualne końcowe separatory.
        """

        scope = resolved_pattern.replace("<auto>", "")

        # usuwamy ewentualne końcowe znaki typu '_' lub '-'
        scope = scope.rstrip("_-/")

        return scope
