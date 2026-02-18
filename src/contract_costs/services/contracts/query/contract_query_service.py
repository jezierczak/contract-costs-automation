# from uuid import UUID,uuid4
# from datetime import date
#
# from contract_costs.action_bus.action_bus import ActionBus
# from contract_costs.model.contract import ContractType
# from contract_costs.services.contracts.query.list_contracts.list_contracts_query_command import ListContractsQuery
# from contract_costs.services.contracts.query.contract_details.contract_details_query_command import ContractDetailsQuery
# from contract_costs.services.contracts.query.list_contracts.list_contracts_query_service import ListContractsQueryService
# from contract_costs.services.contracts.query.contract_details.contract_details_query_service import ContractDetailsQueryService
# from contract_costs.services.contracts.query.dto.contract_list_dto import ContractListDTO
# from contract_costs.services.contracts.query.dto.contract_details_dto import ContractDetailsDTO
#
#
# class ContractQueryService:
#     """
#     FACADE for contract queries.
#
#     Keeps public API stable.
#     Delegates logic to specialized query services.
#     """
#
#     def __init__(
#         self,
#         *,
#         list_contracts_service: ListContractsQueryService,
#         contract_details_service: ContractDetailsQueryService,
#     ) -> None:
#         self._list_service = list_contracts_service
#         self._details_service = contract_details_service
#
#     # =====================================================
#     # LIST
#     # =====================================================
#
#     def list_contracts(
#         self,
#         *,
#         action_bus: ActionBus,
#         organization_id: UUID,
#         actor_user_id: UUID,
#         contract_type: ContractType = ContractType.PROJECT,
#     ) -> list[ContractListDTO]:
#
#         query = ListContractsQuery(
#             organization_id=organization_id,
#             actor_user_id=actor_user_id,
#             contract_type=contract_type,
#         )
#         return action_bus.execute(action=query,handler=self._list_service)
#         # return self._list_service.execute(query)
#
#     # =====================================================
#     # DETAILS
#     # =====================================================
#
#     def get_contract_details(
#         self,
#         *,
#         action_bus: ActionBus,
#         organization_id: UUID,
#         contract_id: UUID,
#         actor_user_id: UUID,
#         at_date: date | None = None,
#     ) -> ContractDetailsDTO:
#
#         query = ContractDetailsQuery(
#             organization_id=organization_id,
#             contract_id=contract_id,
#             at_date=at_date,
#             actor_user_id=actor_user_id
#         )
#         return action_bus.execute(action=query,handler=self._details_service)
#         # return self._details_service.execute(query)