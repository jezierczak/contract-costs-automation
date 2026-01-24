from contract_costs.model.company import Company, CompanyType
from contract_costs.model.invoice_line import InvoiceLine
from contract_costs.model.value_direction import ValueDirection
from contract_costs.services.invoices.assigment.ingest.completion_validator.invoice_completion_reason import \
    InvoiceCompletionReason
from contract_costs.services.invoices.assigment.ingest.dto.invoice_assignment_facts import InvoiceAssignmentFacts


class InvoiceCompletionValidator:

    # @staticmethod
    # def validate( facts: InvoiceAssignmentFacts) -> bool:
    #     if facts.invoice_direction is None:
    #         return False
    #
    #     if not facts.all_lines_complete:
    #         return False
    #
    #     if len(facts.line_directions) != 1:
    #         return False
    #
    #     if facts.invoice_direction not in facts.line_directions:
    #         return False
    #
    #     return True
    def validate(self,facts: InvoiceAssignmentFacts) -> bool:
        return InvoiceCompletionReason.OK in self.status(facts)

    def status(self,
        facts: InvoiceAssignmentFacts
    ) -> list[InvoiceCompletionReason]:

        issues: list[InvoiceCompletionReason] = []

        for line in facts.invoice_lines:
            if line.value_type_id is not None and line.value_type_id not in facts.value_type_directions:
                raise RuntimeError(
                    f"Missing value_type_direction for value_type_id={line.value_type_id}"
                )

        invoice_direction = self.resolve_invoice_direction(
            facts.buyer_role,
            facts.seller_role,
        )

        if invoice_direction is None:
            issues.append(InvoiceCompletionReason.NO_INVOICE_DIRECTION)


        if not facts.invoice_lines:
            issues.append(InvoiceCompletionReason.NO_LINES)

        all_lines_complete = all(self._is_line_complete(line) for line in facts.invoice_lines)

        if not all_lines_complete:
            issues.append(InvoiceCompletionReason.INCOMPLETE_LINES)

        line_directions = {
            facts.value_type_directions.get(line.value_type_id)
            for line in facts.invoice_lines
            if line.value_type_id is not None
        }

        if None in line_directions:
            issues.append(InvoiceCompletionReason.UNKNOWN_LINE_DIRECTION)

        if not line_directions:
            issues.append(InvoiceCompletionReason.NO_LINE_DIRECTIONS)

        elif len(line_directions) != 1:
            issues.append(InvoiceCompletionReason.MIXED_LINE_DIRECTIONS)

        elif invoice_direction not in line_directions:
            issues.append(InvoiceCompletionReason.DIRECTION_MISMATCH)

        if len(issues) == 0:
            issues.append(InvoiceCompletionReason.OK)

        return issues

    @staticmethod
    def resolve_invoice_direction(
            buyer_role: CompanyType,
            seller_role: CompanyType,
    ) -> ValueDirection | None:
        if buyer_role == CompanyType.OWN and seller_role == CompanyType.OWN:
            return ValueDirection.INTERNAL
        if buyer_role == CompanyType.OWN:
            return ValueDirection.COST
        if seller_role == CompanyType.OWN:
            return ValueDirection.REVENUE
        return None

    @staticmethod
    def _is_line_complete(line: InvoiceLine) -> bool:
        return (
                line.contract_id is not None and
                line.contract_node_id is not None and
                line.value_type_id is not None
        )
