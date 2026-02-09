

from contract_costs.action_bus.action_type import ActionType
from contract_costs.model.identity.organization_role import OrganizationRole

ROLE_PERMISSIONS: dict[ActionType, set[OrganizationRole]] = {
    ActionType.UPLOAD_DOCUMENT:{
        OrganizationRole.OWNER,
        OrganizationRole.ADMIN,
        OrganizationRole.USER,
    },
    ActionType.CREATE_CONTRACT: {
        OrganizationRole.OWNER,
        OrganizationRole.ADMIN,
    },
    ActionType.VIEW_CONTRACT: {
        OrganizationRole.OWNER,
        OrganizationRole.ADMIN,
        OrganizationRole.USER,
    },
    ActionType.CREATE_FINANCIAL_RECORD: {
        OrganizationRole.OWNER,
        OrganizationRole.ADMIN,
    },
    ActionType.UPDATE_FINANCIAL_RECORD: {
        OrganizationRole.OWNER,
        OrganizationRole.ADMIN,
    },
    ActionType.VIEW_FINANCIAL_RECORD: {
        OrganizationRole.OWNER,
        OrganizationRole.ADMIN,
        OrganizationRole.USER,
    },
}