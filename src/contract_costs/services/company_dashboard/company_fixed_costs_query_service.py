from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.common.pillars import Pillars
from contract_costs.services.company_dashboard.dto.company_fixed_costs_dto import (
    CompanyFixedCostsDTO,
    FixedCostRecordDTO,
    FixedCostValueTypeDTO,
)
from contract_costs.services.company_dashboard.dto.company_fixerd_costs_query import (
    CompanyFixedCostsQuery,
)
from contract_costs.services.company_dashboard.financials.company_financials_calculator import (
    CompanyFinancialsCalculator,
    period_range,
)
from contract_costs.unit_of_work import UnitOfWork


class CompanyFixedCostsQueryService(
    ActionHandler[CompanyFixedCostsQuery, CompanyFixedCostsDTO]
):

    def execute(
        self,
        *,
        action: CompanyFixedCostsQuery,
        uow: UnitOfWork,
    ) -> CompanyFixedCostsDTO:

        start, end = period_range(action.year, action.month)

        lines = uow.company_dashboard.fetch_company_lines(
            organization_id=action.organization_id,
            company_id=action.company_id,
            start=start,
            end=end,
        )

        records_by_type: dict[str | None, list[FixedCostRecordDTO]] = {}
        names: dict[str | None, tuple[str | None, str | None]] = {}

        for line in lines:
            if not CompanyFinancialsCalculator.is_approved(line):
                continue

            period = CompanyFinancialsCalculator.classify(line=line, company_id=action.company_id)
            if period is None or period.fixed == Pillars():
                continue

            records_by_type.setdefault(line.value_type_id, []).append(
                FixedCostRecordDTO(
                    record_id=line.record_id,
                    record_date=line.record_date,
                    item_name=line.item_name,
                    description=line.description,
                    pillars=period.fixed,
                )
            )
            names[line.value_type_id] = (line.value_type_code, line.value_type_name)

        value_types = [
            FixedCostValueTypeDTO(
                value_type_code=names[vt_id][0],
                value_type_name=names[vt_id][1],
                records=sorted(records, key=lambda r: r.record_date),
                total=sum((r.pillars for r in records), Pillars()),
            )
            for vt_id, records in records_by_type.items()
        ]

        # najważniejszy jest realny wypływ — sortujemy po cashflow
        value_types.sort(key=lambda vt: vt.total.cashflow, reverse=True)

        return CompanyFixedCostsDTO(
            value_types=value_types,
            total=sum((vt.total for vt in value_types), Pillars()),
        )
