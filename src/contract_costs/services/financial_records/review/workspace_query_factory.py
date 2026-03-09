from uuid import UUID

from contract_costs.model.financial_record import (
    FinancialRecordStatus,
    PaymentStatus,
)
from contract_costs.model.record_workspace_view import RecordWorkspaceView
from contract_costs.model.value_direction import ValueDirection
from contract_costs.services.financial_records.review.dto.financial_record_review_query import (
    FinancialRecordReviewQuery,
)


class RecordWorkspaceQueryFactory:

    @staticmethod
    def build(
            *,
            organization_id:UUID,
            actor_user_id:UUID,
            view: RecordWorkspaceView,
    ) -> FinancialRecordReviewQuery:

        match view:

            case RecordWorkspaceView.ALL:
                return FinancialRecordReviewQuery(
                    organization_id=organization_id,
                    actor_user_id=actor_user_id,
                )

            case RecordWorkspaceView.ASSIGN:
                return FinancialRecordReviewQuery(
                    organization_id=organization_id,
                    actor_user_id=actor_user_id,
                    statuses=[
                        FinancialRecordStatus.NEW_COST,
                        FinancialRecordStatus.NEW_REVENUE,
                        FinancialRecordStatus.DRAFT,
                        FinancialRecordStatus.IN_PROGRESS,
                    ]
                )

            case RecordWorkspaceView.TO_ACCOUNTANT:

                return FinancialRecordReviewQuery(
                    organization_id=organization_id,
                    actor_user_id=actor_user_id,
                    only_ready_for_accountant=True
                )

            case RecordWorkspaceView.UNPAID_COSTS:
                return FinancialRecordReviewQuery(
                    organization_id=organization_id,
                    actor_user_id=actor_user_id,
                    payment_statuses=[PaymentStatus.UNPAID],
                    direction=ValueDirection.COST

                )

            case RecordWorkspaceView.UNPAID_REVENUE:
                return FinancialRecordReviewQuery(
                    organization_id=organization_id,
                    actor_user_id=actor_user_id,
                    payment_statuses=[PaymentStatus.UNPAID],
                    direction=ValueDirection.REVENUE
                )