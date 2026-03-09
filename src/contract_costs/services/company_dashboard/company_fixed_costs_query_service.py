from collections import defaultdict
from decimal import Decimal

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.company_dashboard.dto.company_fixed_costs_dto import (
    CompanyFixedCostsDTO,
    FixedCostContractDTO,
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

        # ------------------------------------------------
        # group structure
        # contract_id -> value_type_code -> records
        # ------------------------------------------------

        contracts: dict = {}

        for r in rows:

            contract = contracts.setdefault(
                r.contract_id,
                {
                    "contract_code": r.contract_code,
                    "value_types": {},
                },
            )

            value_type = contract["value_types"].setdefault(
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
                description=r.description,
                amount=r.amount,
                tax_treatment=r.tax_treatment,
            )

            value_type["records"].append(record)
            value_type["total"] += r.amount

        # ------------------------------------------------
        # convert to DTOs
        # ------------------------------------------------

        contract_dtos: list[FixedCostContractDTO] = []
        company_total = Decimal("0")

        for contract_id, c in contracts.items():

            value_type_dtos: list[FixedCostValueTypeDTO] = []
            contract_total = Decimal("0")

            for vt_code, vt in c["value_types"].items():

                value_type_dto = FixedCostValueTypeDTO(
                    value_type_code=vt_code,
                    value_type_name=vt["value_type_name"],
                    records=vt["records"],
                    total=vt["total"],
                )

                value_type_dtos.append(value_type_dto)
                contract_total += vt["total"]

            contract_dtos.append(
                FixedCostContractDTO(
                    contract_id=contract_id,
                    contract_code=c["contract_code"],
                    value_types=value_type_dtos,
                    total=contract_total,
                )
            )

            company_total += contract_total

        return CompanyFixedCostsDTO(
            contracts=contract_dtos,
            total=company_total,
        )