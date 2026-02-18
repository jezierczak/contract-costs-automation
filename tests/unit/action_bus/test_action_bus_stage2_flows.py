from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest

from contract_costs.action_bus.action_bus import ActionBus
from contract_costs.action_bus.permission_resolver import PermissionResolver
from contract_costs.action_bus.permission_validator import PermissionValidator
from contract_costs.model.amount import Amount, VatRate
from contract_costs.model.company import CompanyType
from contract_costs.model.contract import ContractStatus, ContractType
from contract_costs.model.identity.organization_role import OrganizationRole
from contract_costs.model.value_direction import ValueDirection
from contract_costs.services.companies.dto.create_company_command import (
    CreateCounterpartyCompanyCommand,
    CreateOwnerCompanyCommand,
)
from contract_costs.services.companies.dto.update_company_command import (
    UpdateCounterpartyCompanyCommand,
)
from contract_costs.services.contracts.apply.command.set_contract_status_command import (
    SetContractStatusCommand,
)
from contract_costs.services.contracts.dto.create_contract_command import CreateContractCommand
from contract_costs.services.identity.add.dto.assign_user_to_organization_command import (
    AssignUserToOrganizationCommand,
)
from contract_costs.services.identity.add.dto.create_organization_command import (
    CreateOrganizationCommand,
)
from contract_costs.services.identity.add.dto.create_user_command import CreateUserCommand
from contract_costs.services.identity.change.dto.change_organization_user_role_command import (
    ChangeOrganizationUserRoleCommand,
)
from contract_costs.services.identity.remove.dto.remove_organization_user_command import (
    RemoveOrganizationUserCommand,
)
from contract_costs.services.snapshots.dto.create_contract_snapshot_command import (
    CreateContractSnapshotCommand,
)
from contract_costs.services.value_types.apply.commands.change_value_type_code_command import (
    ChangeValueTypeCodeCommand,
)
from contract_costs.services.value_types.apply.commands.update_value_type_command import (
    UpdateValueTypeCommand,
)
from contract_costs.services.value_types.dto.create_value_type_command import (
    CreateValueTypeCommand,
)
from tests.builders.company_builder import CompanyBuilder
from tests.builders.contract_builder import ContractBuilder
from tests.builders.financial_record_line_builder import FinancialRecordLineBuilder
from tests.builders.organization_builder import OrganizationBuilder
from tests.builders.organization_user_builder import OrganizationUserBuilder
from tests.builders.user_builder import UserBuilder
from tests.helpers.contracts_helpers import make_contract_node


class _AllowAllResolver(PermissionResolver):
    def has_permission(self, *, organization_id, user_id, action_type) -> bool:
        return True


def _bus_for_uow(uow):
    validator = PermissionValidator(permission_resolver=_AllowAllResolver())
    return ActionBus(permission_validator=validator, uow_factory=lambda: uow)


def test_action_bus_add_company_owner_creates_company_and_system_contract(services_memory, uow):
    org_id = uuid4()
    user_id = uuid4()
    bus = _bus_for_uow(uow)

    bus.execute(
        action=CreateOwnerCompanyCommand(
            organization_id=org_id,
            actor_user_id=user_id,
            name="Own Co",
            tax_number="6762680195",
            role=CompanyType.OWN,
        ),
        handler=services_memory.create_company,
    )

    owners = uow.companies.get_owners(organization_id=org_id)
    assert len(owners) == 1
    system_contract = uow.contracts.get_system_contract(
        organization_id=org_id,
        owner_id=owners[0].id,
    )
    assert system_contract is not None


def test_action_bus_add_company_counterparty_creates_company(services_memory, uow):
    org_id = uuid4()
    user_id = uuid4()
    bus = _bus_for_uow(uow)

    bus.execute(
        action=CreateCounterpartyCompanyCommand(
            organization_id=org_id,
            actor_user_id=user_id,
            name="Supplier A",
            tax_number="6792740424",
            role=CompanyType.SUPPLIER,
        ),
        handler=services_memory.create_company,
    )

    companies = uow.companies.list_all(organization_id=org_id)
    assert len(companies) == 1
    assert companies[0].name == "Supplier A"


def test_action_bus_add_contract_creates_contract(services_memory, uow):
    org_id = uuid4()
    user_id = uuid4()
    bus = _bus_for_uow(uow)

    owner = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_role(CompanyType.OWN)
        .build()
    )
    uow.companies.add(owner)

    bus.execute(
        action=CreateContractCommand(
            organization_id=org_id,
            actor_user_id=user_id,
            code="ADD-C-1",
            name="Contract A",
            description=None,
            owner=owner,
            client=None,
            start_date=None,
            end_date=None,
            budget=Decimal("1000"),
            path=None,
            status=ContractStatus.ACTIVE,
            contract_type=ContractType.PROJECT,
            contract_node_input=[],
        ),
        handler=services_memory.create_contract,
    )

    contracts = uow.contracts.list_contracts(org_id, contract_type=ContractType.PROJECT)
    assert len(contracts) == 1
    assert contracts[0].code == "ADD-C-1"


def test_action_bus_add_value_type_creates_value_type(services_memory, uow):
    org_id = uuid4()
    user_id = uuid4()
    bus = _bus_for_uow(uow)

    bus.execute(
        action=CreateValueTypeCommand(
            organization_id=org_id,
            actor_user_id=user_id,
            code="MAT",
            name="Materials",
            description=None,
            direction=ValueDirection.COST,
        ),
        handler=services_memory.create_value_type,
    )

    value_types = uow.value_types.list_all(organization_id=org_id)
    assert len(value_types) == 1
    assert value_types[0].code == "MAT"


def test_action_bus_edit_company_updates_company(services_memory, uow):
    org_id = uuid4()
    user_id = uuid4()
    bus = _bus_for_uow(uow)

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_role(CompanyType.SUPPLIER)
        .with_tax_number("6792740424")
        .with_name("Old Name")
        .build()
    )
    uow.companies.add(company)

    bus.execute(
        action=UpdateCounterpartyCompanyCommand(
            organization_id=org_id,
            actor_user_id=user_id,
            company_id=company.id,
            name="New Name",
            role=CompanyType.SUPPLIER,
            address=company.address,
            contact=company.contact,
            description=company.description,
            tax_number=company.tax_number,
            bank_account=company.bank_account,
            tags=company.tags,
        ),
        handler=services_memory.update_company_service,
    )

    updated = uow.companies.get(company.id, org_id)
    assert updated is not None
    assert updated.name == "New Name"


def test_action_bus_add_create_user_and_assign_and_edit_and_remove_membership(services_memory, uow):
    org_id = uuid4()
    actor_id = uuid4()
    target_id = uuid4()
    bus = _bus_for_uow(uow)

    uow.organizations.add(
        OrganizationBuilder().with_id(org_id).with_code("ORG-AB").build()
    )
    uow.users.add(UserBuilder().with_id(actor_id).with_login("owner_login").build())
    uow.users.add(UserBuilder().with_id(target_id).with_login("target_login").build())
    uow.organization_users.add(
        OrganizationUserBuilder()
        .with_organization_id(org_id)
        .with_user_id(actor_id)
        .as_owner()
        .build()
    )

    bus.execute(
        action=AssignUserToOrganizationCommand(
            organization_id=org_id,
            actor_user_id=actor_id,
            target_user_id=target_id,
            role=OrganizationRole.USER,
        ),
        handler=services_memory.add_organization_user,
    )
    membership = uow.organization_users.get_by_org_and_user(
        organization_id=org_id,
        user_id=target_id,
    )
    assert membership is not None
    assert membership.role == OrganizationRole.USER

    bus.execute(
        action=ChangeOrganizationUserRoleCommand(
            organization_id=org_id,
            actor_user_id=actor_id,
            target_user_id=target_id,
            new_role=OrganizationRole.ADMIN,
        ),
        handler=services_memory.change_organization_user_role,
    )
    changed = uow.organization_users.get_by_org_and_user(
        organization_id=org_id,
        user_id=target_id,
    )
    assert changed is not None
    assert changed.role == OrganizationRole.ADMIN

    bus.execute(
        action=RemoveOrganizationUserCommand(
            organization_id=org_id,
            actor_user_id=actor_id,
            target_user_id=target_id,
        ),
        handler=services_memory.remove_organization_user,
    )
    removed = uow.organization_users.get_by_org_and_user(
        organization_id=org_id,
        user_id=target_id,
    )
    assert removed is not None
    assert removed.is_active is False


def test_action_bus_add_create_user_command_creates_user(services_memory, uow):
    org_id = uuid4()
    actor_id = uuid4()
    bus = _bus_for_uow(uow)

    bus.execute(
        action=CreateUserCommand(
            organization_id=org_id,
            actor_user_id=actor_id,
            login="new_login",
            email="new@example.com",
            full_name="New User",
        ),
        handler=services_memory.create_user,
    )

    created = uow.users.get_by_login("new_login")
    assert created is not None
    assert created.email == "new@example.com"


def test_action_bus_add_create_organization_command_creates_org_with_owner(services_memory, uow):
    bus = _bus_for_uow(uow)

    org_code = f"ORG-{uuid4().hex[:6]}"
    bus.execute(
        action=CreateOrganizationCommand(
            organization_code=org_code,
            organization_name="Org Name",
            owner_login=f"owner-{uuid4().hex[:6]}",
            owner_email="owner@example.com",
            owner_full_name="Owner",
            created_by_user_id=None,
        ),
        handler=services_memory.create_organization_with_owner,
    )

    created_org = uow.organizations.get_by_code(org_code)
    assert created_org is not None
    owner = uow.users.get_by_login(created_org.code.replace("ORG-", "owner-"))
    assert owner is None
    assert len(uow.organization_users.list_by_organization(created_org.id)) == 1


def test_action_bus_edit_value_type_and_code(services_memory, uow):
    org_id = uuid4()
    user_id = uuid4()
    bus = _bus_for_uow(uow)

    value_type_id = bus.execute(
        action=CreateValueTypeCommand(
            organization_id=org_id,
            actor_user_id=user_id,
            code="LAB",
            name="Labor",
            description=None,
            direction=ValueDirection.COST,
        ),
        handler=services_memory.create_value_type,
    )

    bus.execute(
        action=UpdateValueTypeCommand(
            organization_id=org_id,
            actor_user_id=user_id,
            value_type_id=value_type_id,
            name="Labor Updated",
            description="upd",
        ),
        handler=services_memory.update_value_type_service,
    )

    bus.execute(
        action=ChangeValueTypeCodeCommand(
            organization_id=org_id,
            actor_user_id=user_id,
            value_type_id=value_type_id,
            new_code="LAB2",
        ),
        handler=services_memory.change_value_type_code_service,
    )

    updated = uow.value_types.get(organization_id=org_id, value_type_id=value_type_id)
    assert updated is not None
    assert updated.name == "Labor Updated"
    assert updated.code == "LAB2"


def test_action_bus_add_contract_snapshot_command_creates_snapshot(services_memory, uow):
    org_id = uuid4()
    user_id = uuid4()
    bus = _bus_for_uow(uow)

    owner = CompanyBuilder().with_organization_id(org_id).with_role(CompanyType.OWN).build()
    contract = (
        ContractBuilder()
        .with_organization_id(org_id)
        .with_owner(owner)
        .with_status(ContractStatus.ACTIVE)
        .build()
    )
    uow.contracts.add(contract)
    node = make_contract_node(organization_id=org_id, contract_id=contract.id, code="A", budget=Decimal("100"))
    uow.contract_nodes.add_all([node])
    uow.financial_record_lines.add(
        organization_id=org_id,
        line=(
            FinancialRecordLineBuilder()
            .with_organization_id(org_id)
            .with_contract_id(contract.id)
            .with_contract_node_id(node.id)
            .with_created_at(datetime.combine(date.today(), datetime.min.time()))
            .with_amount(Amount(value=Decimal("10"), vat_rate=VatRate.VAT_23))
            .build()
        ),
    )

    snapshot, created = bus.execute(
        action=CreateContractSnapshotCommand(
            organization_id=org_id,
            actor_user_id=user_id,
            contract_id=contract.id,
            snapshot_date=date.today(),
        ),
        handler=services_memory.create_contract_snapshot,
    )
    assert created is True
    assert snapshot.contract_id == contract.id


def test_action_bus_set_contract_status_command_updates_status(services_memory, uow):
    org_id = uuid4()
    user_id = uuid4()
    bus = _bus_for_uow(uow)

    owner = CompanyBuilder().with_organization_id(org_id).with_role(CompanyType.OWN).build()
    contract = (
        ContractBuilder()
        .with_organization_id(org_id)
        .with_owner(owner)
        .with_status(ContractStatus.PLANNED)
        .build()
    )
    uow.contracts.add(contract)

    bus.execute(
        action=SetContractStatusCommand(
            organization_id=org_id,
            actor_user_id=user_id,
            contract_id=contract.id,
            new_status=ContractStatus.ACTIVE,
        ),
        handler=services_memory.set_contract_status_service,
    )
    updated = uow.contracts.get(
        organization_id=org_id,
        contract_id=contract.id,
    )
    assert updated is not None
    assert updated.status == ContractStatus.ACTIVE
