from datetime import date
from decimal import Decimal
from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.model.document import DocumentStatus
from contract_costs.model.financial_record import PaymentStatus
from contract_costs.model.record_workspace_view import RecordWorkspaceView
from contract_costs.services.company_dashboard.financials.company_financials_calculator import (
    CompanyFinancialsCalculator,
    EMPTY,
    period_range,
)
from contract_costs.services.dashboard.dto.dashboard_data import (
    DashboardCompanyCard,
    DashboardData,
    DashboardPeriods,
    UnpaidSummary,
)
from contract_costs.services.dashboard.dto.dashboard_query import DashboardQuery
from contract_costs.services.financial_records.review.workspace_query_factory import RecordWorkspaceQueryFactory
from contract_costs.unit_of_work import UnitOfWork


class DashboardQueryService(ActionHandler[DashboardQuery, DashboardData]):
    """
    Dashboard organizacji: karty firm own (rok + poprzedni miesiąc), wynik grupy
    bez INTERNAL oraz niezapłacone faktury (liczba + brutto do zapłaty).
    Finanse liczy ten sam CompanyFinancialsCalculator co widok „Finanse firmy”.
    """

    def execute(self, *, action: DashboardQuery, uow: UnitOfWork) -> DashboardData:
        today = action.today or date.today()
        last_month_year, last_month = (today.year - 1, 12) if today.month == 1 else (today.year, today.month - 1)

        ranges = {
            "year": period_range(today.year, None),
            "last_month": period_range(last_month_year, last_month),
        }

        companies: list[DashboardCompanyCard] = []
        group = {key: EMPTY for key in ranges}

        for company in uow.companies.get_owners(organization_id=action.organization_id):
            if not company.is_active:
                continue

            own: dict = {}
            unapproved = 0
            for key, (start, end) in ranges.items():
                lines = uow.company_dashboard.fetch_company_lines(
                    organization_id=action.organization_id,
                    company_id=company.id,
                    start=start,
                    end=end,
                )
                financials = CompanyFinancialsCalculator.calculate(
                    year=start.year, company_id=company.id, lines=lines,
                )
                own[key] = financials.total
                group[key] += CompanyFinancialsCalculator.calculate(
                    year=start.year, company_id=company.id, lines=lines, skip_internal=True,
                ).total
                if key == "year":
                    unapproved = financials.unapproved_record_count

            companies.append(DashboardCompanyCard(
                company_id=company.id,
                name=company.name,
                periods=DashboardPeriods(year=own["year"], last_month=own["last_month"]),
                unapproved_record_count=unapproved,
            ))

        def unpaid(view: RecordWorkspaceView) -> UnpaidSummary:
            return self._unpaid_summary(
                uow=uow,
                organization_id=action.organization_id,
                actor_user_id=action.actor_user_id,
                view=view,
            )

        return DashboardData(
            year=today.year,
            last_month_year=last_month_year,
            last_month=last_month,
            companies=companies,
            group=DashboardPeriods(year=group["year"], last_month=group["last_month"]),
            unpaid_costs=unpaid(RecordWorkspaceView.UNPAID_COSTS),
            unpaid_revenue=unpaid(RecordWorkspaceView.UNPAID_REVENUE),
            unpaid_internal=unpaid(RecordWorkspaceView.UNPAID_INTERNAL),
            documents_to_assign=len(uow.documents.list_filtered(
                organization_id=action.organization_id,
                document_status=DocumentStatus.READY,
            )),
            records_to_assign=uow.financial_records.count_for_review(
                organization_id=action.organization_id,
                query=RecordWorkspaceQueryFactory.build(
                    organization_id=action.organization_id,
                    actor_user_id=action.actor_user_id,
                    view=RecordWorkspaceView.ASSIGN,
                ),
            ),
        )

    @staticmethod
    def _unpaid_summary(
        *,
        uow: UnitOfWork,
        organization_id: UUID,
        actor_user_id: UUID,
        view: RecordWorkspaceView,
    ) -> UnpaidSummary:
        """Te same filtry co lista /records/unpaid_* – liczba na dashboardzie zgadza się z listą."""
        query = RecordWorkspaceQueryFactory.build(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            view=view,
        )
        records = uow.financial_records.list_for_review(organization_id=organization_id, query=query)
        if not records:
            return UnpaidSummary(count=0, amount=Decimal("0.00"))

        payable: dict[UUID, Decimal] = {}
        for line in uow.financial_record_lines.list_by_financial_record_ids(
            organization_id=organization_id,
            financial_records_ids=[r.id for r in records],
        ):
            payable[line.financial_record_id] = payable.get(line.financial_record_id, Decimal("0")) + line.amount.payable

        amount = Decimal("0")
        for record in records:
            paid = Decimal("0")
            if record.payment_status != PaymentStatus.UNPAID:
                paid = sum(
                    (p.amount for p in uow.financial_record_payments.list_by_financial_record(
                        organization_id=organization_id, financial_record_id=record.id,
                    )),
                    Decimal("0"),
                )
            amount += max(payable.get(record.id, Decimal("0")) - paid, Decimal("0"))

        return UnpaidSummary(count=len(records), amount=amount.quantize(Decimal("0.01")))
