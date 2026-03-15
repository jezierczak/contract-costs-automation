from collections import defaultdict
from decimal import Decimal

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.company_dashboard.dto.company_fixed_costs_dto import (
    CompanyFixedCostsDTO,
    FixedCostValueTypeDTO,
    FixedCostRecordDTO,
)
from contract_costs.services.company_dashboard.dto.company_fixerd_costs_query import (
    CompanyFixedCostsQuery,
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

        repo = uow.company_dashboard

        rows = repo.fetch_fixed_costs(
            organization_id=action.organization_id,
            company_id=action.company_id,
            year=action.year,
            month=action.month,
        )

        # ----------------------------------------
        # value_type -> records
        # ----------------------------------------

        value_types: dict = {}

        for r in rows:

            vt = value_types.setdefault(
                r.value_type_code,
                {
                    "value_type_name": r.value_type_name,
                    "records": [],
                    "total": Decimal("0"),
                },
            )

            record = FixedCostRecordDTO(
                record_id=r.record_id,
                record_date=r.record_date,
                item_name=r.item_name,
                description=r.description,
                amount=r.amount,
                tax_treatment=r.tax_treatment,
            )

            vt["records"].append(record)
            vt["total"] += r.amount

        # ----------------------------------------
        # sort records by date
        # ----------------------------------------

        for vt in value_types.values():
            vt["records"].sort(key=lambda rr: rr.record_date)
        # ----------------------------------------
        # convert to DTO
        # ----------------------------------------

        value_type_dtos: list[FixedCostValueTypeDTO] = []
        company_total = Decimal("0")

        for vt_code, vt in value_types.items():

            dto = FixedCostValueTypeDTO(
                value_type_code=vt_code,
                value_type_name=vt["value_type_name"],
                records=vt["records"],
                total=vt["total"],
            )

            value_type_dtos.append(dto)
            company_total += vt["total"]

        # ----------------------------------------
        # sort value types by total
        # ----------------------------------------

        value_type_dtos.sort(key=lambda x: x.total, reverse=True)

        return CompanyFixedCostsDTO(
            value_types=value_type_dtos,
            total=company_total,
        )