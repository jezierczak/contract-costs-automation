from decimal import Decimal
from collections import defaultdict

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.companies.query.dto.company_detail_dto import CompanyDetailDTO
from contract_costs.services.companies.query.dto.company_detail_query import CompanyDetailQuery
from contract_costs.services.companies.query.dto.company_year_dto import CounterpartyYearDTO
from contract_costs.unit_of_work import UnitOfWork

from contract_costs.model.amount import Amount, AmountInputType, VatRate, TaxTreatment


class CompanyDetailQueryService(
    ActionHandler[CompanyDetailQuery, CompanyDetailDTO]
):

    def execute(
        self,
        *,
        action: CompanyDetailQuery,
        uow: UnitOfWork,
    ) -> CompanyDetailDTO:

        company_repo = uow.companies
        dashboard_repo = uow.company_dashboard

        company = company_repo.get(
            organization_id=action.organization_id,
            company_id=action.company_id,
        )


        if not company:
            raise ValueError("Company not found")

        lines = dashboard_repo.fetch_counterparty_lines(
            organization_id=action.organization_id,
            counterparty_id=action.company_id,
            owner_company_id = action.owner_company_id
        )

        revenue = Decimal("0")
        costs = Decimal("0")

        invoice_ids = set()
        unpaid_invoice_ids = set()
        last_invoice_date = None

        years = defaultdict(lambda: {
            "revenue": Decimal("0"),
            "costs": Decimal("0"),
            "invoice_ids": set(),
        })

        company_id = str(action.company_id)

        for line in lines:

            invoice_ids.add(line.record_id)

            if line.payment_status != "paid":
                unpaid_invoice_ids.add(line.record_id)

            if last_invoice_date is None or line.record_date > last_invoice_date:
                last_invoice_date = line.record_date

            year = line.record_date.year

            amount = Amount.from_input(
                value=line.amount_value,
                input_type=AmountInputType(line.amount_input_type),
                vat_rate=VatRate(Decimal(line.vat_rate)),
                tax_treatment=TaxTreatment(line.tax_treatment),
            )

            value = amount.cashflow

            if line.buyer_id == company_id:
                revenue += value
                years[year]["revenue"] += value

            if line.seller_id == company_id:
                costs += value
                years[year]["costs"] += value

            years[year]["invoice_ids"].add(line.record_id)

        balance = revenue - costs

        years_dto = [
            CounterpartyYearDTO(
                year=year,
                invoice_count=len(data["invoice_ids"]),
                revenue=data["revenue"],
                costs=data["costs"],
                balance=data["revenue"] - data["costs"],
            )
            for year, data in sorted(years.items(), reverse=True)[:5]
        ]

        return CompanyDetailDTO(
            company_id=company.id,
            name=company.name,
            tax_number=company.tax_number,
            role=company.role.value,
            is_active=company.is_active,

            invoice_count=len(invoice_ids),

            revenue=revenue,
            costs=costs,
            balance=balance,

            unpaid_invoices=len(unpaid_invoice_ids),
            last_invoice_date=last_invoice_date,

            years=years_dto,
        )