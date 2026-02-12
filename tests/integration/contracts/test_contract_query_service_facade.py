from datetime import date
from uuid import uuid4
from unittest.mock import MagicMock

from contract_costs.services.contracts.query.contract_query_service import ContractQueryService


def test_list_contracts_delegates_to_list_service():
    organization_id = uuid4()

    expected_result = [MagicMock()]

    list_service = MagicMock()
    list_service.execute.return_value = expected_result

    details_service = MagicMock()

    facade = ContractQueryService(
        list_contracts_service=list_service,
        contract_details_service=details_service,
    )

    result = facade.list_contracts(
        organization_id=organization_id
    )

    assert result == expected_result
    list_service.execute.assert_called_once()

    query_passed = list_service.execute.call_args[0][0]

    assert query_passed.organization_id == organization_id

def test_get_contract_details_delegates_to_details_service():
    organization_id = uuid4()
    contract_id = uuid4()

    expected_result = MagicMock()

    list_service = MagicMock()
    details_service = MagicMock()
    details_service.execute.return_value = expected_result

    facade = ContractQueryService(
        list_contracts_service=list_service,
        contract_details_service=details_service,
    )

    result = facade.get_contract_details(
        organization_id=organization_id,
        contract_id=contract_id,
        at_date=date(2024, 1, 1),
    )

    assert result == expected_result
    details_service.execute.assert_called_once()

    query_passed = details_service.execute.call_args[0][0]

    assert query_passed.organization_id == organization_id
    assert query_passed.contract_id == contract_id
    assert query_passed.at_date == date(2024, 1, 1)
