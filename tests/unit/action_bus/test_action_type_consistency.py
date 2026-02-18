from uuid import uuid4

from contract_costs.action_bus.ROLE_PERMISSIONS import ROLE_PERMISSIONS
from contract_costs.action_bus.action_type import ActionType
from contract_costs.action_bus.permission_resolver import PermissionResolver
from contract_costs.action_bus.permission_validator import PermissionValidator
from contract_costs.model.contract import ContractType
from contract_costs.services.contracts.apply.command.apply_contract_progerss_command import (
    ApplyContractProgressCommand,
)
from contract_costs.services.companies.dto.create_company_command import (
    CreateCounterpartyCompanyCommand,
    CreateOwnerCompanyCommand,
)
from contract_costs.services.companies.dto.update_company_command import (
    UpdateCounterpartyCompanyCommand,
    UpdateOwnerCompanyCommand,
)
from contract_costs.services.contracts.query.contract_details.contract_details_query_command import (
    ContractDetailsQuery,
)
from contract_costs.services.contracts.query.list_contracts.list_contracts_query_command import (
    ListContractsQuery,
)
from contract_costs.services.documents.process.dto.process_document_command import (
    ProcessDocumentCommand,
)
from contract_costs.services.documents.query.list_docuemnts_query_command import (
    ListDocumentsQueryCommand,
)
from contract_costs.model.company import CompanyType


class _AllowResolver(PermissionResolver):
    def __init__(self):
        self.calls = []

    def has_permission(self, *, organization_id, user_id, action_type) -> bool:
        self.calls.append((organization_id, user_id, action_type))
        return True


def test_action_type_supports_new_and_legacy_constants():
    assert ActionType.CONTRACT_VIEW.value == "contract_view"
    assert ActionType.DOCUMENT_MANAGEMENT.value == "document_management"
    assert ActionType.COMPANY_MANAGEMENT.value == "company_management"
    assert ActionType.UPLOAD_DOCUMENT.value == "upload_document"


def test_queries_have_explicit_action_type_mapping():
    org_id = uuid4()
    user_id = uuid4()

    list_query = ListContractsQuery(
        organization_id=org_id,
        actor_user_id=user_id,
        contract_type=ContractType.PROJECT,
    )
    details_query = ContractDetailsQuery(
        organization_id=org_id,
        actor_user_id=user_id,
        contract_id=uuid4(),
    )
    docs_query = ListDocumentsQueryCommand(
        organization_id=org_id,
        actor_user_id=user_id,
    )

    assert list_query.action_type is ActionType.CONTRACT_VIEW
    assert details_query.action_type is ActionType.CONTRACT_VIEW
    assert docs_query.action_type is ActionType.DOCUMENT_MANAGEMENT


def test_permission_validator_uses_command_action_type():
    resolver = _AllowResolver()
    validator = PermissionValidator(permission_resolver=resolver)

    cmd = ProcessDocumentCommand(
        organization_id=uuid4(),
        actor_user_id=uuid4(),
        document_id=uuid4(),
    )

    validator.validate(cmd)

    assert len(resolver.calls) == 1
    _, _, action_type = resolver.calls[0]
    assert action_type is ActionType.UPLOAD_DOCUMENT


def test_contract_progress_command_has_management_action_type():
    cmd = ApplyContractProgressCommand(
        organization_id=uuid4(),
        actor_user_id=uuid4(),
        contract_id=uuid4(),
        updates=[],
    )

    assert cmd.action_type is ActionType.CONTRACT_PROGRESS_MANAGEMENT


def test_role_permissions_cover_new_action_types():
    assert ActionType.CONTRACT_PROGRESS_MANAGEMENT in ROLE_PERMISSIONS
    assert ActionType.CONTRACT_VIEW in ROLE_PERMISSIONS
    assert ActionType.DOCUMENT_MANAGEMENT in ROLE_PERMISSIONS


def test_company_commands_are_split_by_role_dimension():
    org_id = uuid4()
    user_id = uuid4()

    owner_create = CreateOwnerCompanyCommand(
        organization_id=org_id,
        actor_user_id=user_id,
        name="Owner Co",
        tax_number="1234567890",
        role=CompanyType.OWN,
    )
    counterparty_create = CreateCounterpartyCompanyCommand(
        organization_id=org_id,
        actor_user_id=user_id,
        name="Supplier Co",
        tax_number="1234567891",
        role=CompanyType.SUPPLIER,
    )
    owner_update = UpdateOwnerCompanyCommand(
        organization_id=org_id,
        actor_user_id=user_id,
        company_id=uuid4(),
        name="Owner Co",
        role=CompanyType.OWN,
        address=None,
        contact=None,
        description=None,
        tax_number=None,
        bank_account=None,
        tags=None,
    )
    counterparty_update = UpdateCounterpartyCompanyCommand(
        organization_id=org_id,
        actor_user_id=user_id,
        company_id=uuid4(),
        name="Supplier Co",
        role=CompanyType.SUPPLIER,
        address=None,
        contact=None,
        description=None,
        tax_number=None,
        bank_account=None,
        tags=None,
    )

    assert owner_create.action_type is ActionType.OWNER_COMPANY_MANAGEMENT
    assert counterparty_create.action_type is ActionType.COUNTERPARTY_MANAGEMENT
    assert owner_update.action_type is ActionType.OWNER_COMPANY_MANAGEMENT
    assert counterparty_update.action_type is ActionType.COUNTERPARTY_MANAGEMENT
