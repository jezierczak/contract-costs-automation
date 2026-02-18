from contract_costs.cli.context import get_services
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.services.identity.add.dto.create_organization_command import (
    CreateOrganizationCommand,
)


def create_organization_from_cli(
    *,
    data: dict,
) -> None:
    services = get_services()

    cmd = CreateOrganizationCommand(
        organization_code=data["organization_code"],
        organization_name=data["organization_name"],
        owner_login=data["owner_login"],
        owner_email=data.get("owner_email"),
        owner_full_name=data.get("owner_full_name"),
        created_by_user_id=None,  # CLI = system / bootstrap
    )

    services.action_bus.execute(
        action=cmd,
        handler=services.create_organization_with_owner,
    )

