from contract_costs.action_bus.action_type import ActionType
from contract_costs.model.identity.organization_role import OrganizationRole


ROLE_PERMISSIONS: dict[ActionType, set[OrganizationRole]] = {
    # Legacy mappings currently used by existing commands
    ActionType.UPLOAD_DOCUMENT: {
        OrganizationRole.ADMIN,
        OrganizationRole.USER,
    },
    ActionType.DELETE_DOCUMENT: {
        OrganizationRole.ADMIN,
        OrganizationRole.USER,
    },
    ActionType.APPLY_DOCUMENT: {
        OrganizationRole.ADMIN,
        OrganizationRole.USER,
    },
    ActionType.CREATE_CONTRACT: {
        OrganizationRole.ADMIN,
    },
    ActionType.VIEW_CONTRACT: {
        OrganizationRole.ADMIN,
        OrganizationRole.USER,
    },
    ActionType.CREATE_FINANCIAL_RECORD: {
        OrganizationRole.ADMIN,
    },
    ActionType.UPDATE_FINANCIAL_RECORD: {
        OrganizationRole.ADMIN,
    },
    ActionType.VIEW_FINANCIAL_RECORD: {
        OrganizationRole.ADMIN,
        OrganizationRole.USER,
    },
    ActionType.COMPANY_MANAGEMENT: {
        OrganizationRole.ADMIN,
        OrganizationRole.USER,
    },

    # New mappings
    ActionType.ORG_USER_MANAGEMENT: {
        OrganizationRole.ADMIN,
    },
    ActionType.ORGANIZATION_SETTINGS_MANAGEMENT: {
        OrganizationRole.ADMIN,
    },
    ActionType.ORG_CONTEXT_SWITCH: {
        OrganizationRole.ADMIN,
    },
    ActionType.OWNER_COMPANY_MANAGEMENT: {
        OrganizationRole.ADMIN,
    },
    ActionType.COUNTERPARTY_MANAGEMENT: {
        OrganizationRole.ADMIN,
        OrganizationRole.USER,
    },
    ActionType.DOCUMENT_MANAGEMENT: {
        OrganizationRole.ADMIN,
        OrganizationRole.USER,
    },
    ActionType.DOCUMENT_PROCESSING: {
        OrganizationRole.ADMIN,
        OrganizationRole.USER,
    },
    ActionType.DOCUMENT_RECORD_LINK_MANAGEMENT: {
        OrganizationRole.ADMIN,
        OrganizationRole.USER,
    },
    ActionType.FINANCIAL_RECORD_MANAGEMENT: {
        OrganizationRole.ADMIN,
    },
    ActionType.FINANCIAL_RECORD_FIXED_COST_ALLOCATION: {
        OrganizationRole.ADMIN,
    },
    ActionType.FINANCIAL_RECORD_APPROVAL: {
        OrganizationRole.ADMIN,
    },
    ActionType.CONTRACT_MANAGEMENT: {
        OrganizationRole.ADMIN,
    },
    ActionType.CONTRACT_PROGRESS_MANAGEMENT: {
        OrganizationRole.ADMIN,
    },
    ActionType.COUNTERPARTY_VIEW: {
        OrganizationRole.ADMIN,
        OrganizationRole.USER,
    },
    ActionType.CONTRACT_VIEW: {
        OrganizationRole.ADMIN,
        OrganizationRole.USER,
    },
    ActionType.FINANCIAL_RECORD_VIEW: {

        OrganizationRole.ADMIN,
        OrganizationRole.USER,
    },
    ActionType.UNPAID_RECORDS_VIEW: {
        OrganizationRole.ADMIN,
        OrganizationRole.USER,
    },
    ActionType.COST_INVOICES_VIEW: {
        OrganizationRole.ADMIN,
        OrganizationRole.USER,
    },
    ActionType.REVENUE_INVOICES_VIEW: {
        OrganizationRole.ADMIN,
        OrganizationRole.USER,
    },
    ActionType.VIEW: {
        OrganizationRole.ADMIN,
        OrganizationRole.USER,
    },
}
