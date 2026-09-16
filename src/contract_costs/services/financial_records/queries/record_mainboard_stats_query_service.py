from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.model.record_workspace_view import RecordWorkspaceView
from contract_costs.services.financial_records.queries.dto.record_mainbaoard_stats_query import \
    RecordMainboardStatsQuery
from contract_costs.services.financial_records.queries.dto.record_mainboard_stats_view import RecordMainboardStatsView
from contract_costs.services.financial_records.review.workspace_query_factory import RecordWorkspaceQueryFactory
from contract_costs.unit_of_work import UnitOfWork


class RecordMainboardStatsQueryService(
    ActionHandler[RecordMainboardStatsQuery, RecordMainboardStatsView]
):

    def execute(self, *, action:RecordMainboardStatsQuery, uow:UnitOfWork):
        repo = uow.financial_records

        def count(view):
            query = RecordWorkspaceQueryFactory.build(
                organization_id=action.organization_id,
                actor_user_id=action.actor_user_id,
                view=view,
            )
            return repo.count_for_review(
                organization_id=action.organization_id,
                query=query,
            )

        return RecordMainboardStatsView(
            assign=count(RecordWorkspaceView.ASSIGN),
            to_accountant=count(RecordWorkspaceView.TO_ACCOUNTANT),
            sent_history=count(RecordWorkspaceView.SENT_HISTORY),
            unpaid_costs=count(RecordWorkspaceView.UNPAID_COSTS),
            unpaid_revenue=count(RecordWorkspaceView.UNPAID_REVENUE),
        )
