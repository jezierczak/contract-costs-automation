from enum import Enum


class ActionType(Enum):
    ORG_QUERY ="org_query"
    # Identity / organization
    ORG_USER_MANAGEMENT = "org_user_management"
    ORGANIZATION_SETTINGS_MANAGEMENT = "organization_settings_management"
    ORG_CONTEXT_SWITCH= "org_context_switch"

    # Companies
    OWNER_COMPANY_MANAGEMENT = "owner_company_management"
    COUNTERPARTY_MANAGEMENT = "counterparty_management"
    COMPANY_MANAGEMENT = "company_management"  # legacy, still used in existing DTOs

    # Documents
    DOCUMENT_MANAGEMENT = "document_management"
    DOCUMENT_PROCESSING = "document_processing"
    DOCUMENT_RECORD_LINK_MANAGEMENT = "document_record_link_management"
    UPLOAD_DOCUMENT = "upload_document"  # legacy
    DELETE_DOCUMENT = "delete_document"  # legacy
    APPLY_DOCUMENT = "apply_document"  # legacy

    # Financial records
    FINANCIAL_RECORD_MANAGEMENT = "financial_record_management"
    FINANCIAL_RECORD_FIXED_COST_ALLOCATION = "financial_record_fixed_cost_allocation"
    FINANCIAL_RECORD_APPROVAL = "financial_record_approval"
    CREATE_FINANCIAL_RECORD = "create_financial_record"  # legacy
    UPDATE_FINANCIAL_RECORD = "update_financial_record"  # legacy

    # Contracts
    CONTRACT_MANAGEMENT = "contract_management"
    CONTRACT_PROGRESS_MANAGEMENT = "contract_progress_management"
    CREATE_CONTRACT = "create_contract"  # legacy

    # Queries
    COUNTERPARTY_VIEW = "counterparty_view"
    CONTRACT_VIEW = "contract_view"
    FINANCIAL_RECORD_VIEW = "financial_record_view"
    UNPAID_RECORDS_VIEW = "unpaid_records_view"
    COST_INVOICES_VIEW = "cost_invoices_view"
    REVENUE_INVOICES_VIEW = "revenue_invoices_view"
    VIEW_CONTRACT = "view_contract"  # legacy
    VIEW_FINANCIAL_RECORD = "view_financial_record"  # legacy
    VIEW_SNAPSHOT = "view_snapshot"
    VIEW = "view"

    #Snapshots
    CREATE_SNAPSHOT = "create_snapshot"

    SYSTEM_CREATE_ORGANIZATION_NEW_USER = "system_create_organization_new_user"





def action_type(action: ActionType):
    def decorator(cls):
        cls.__action_type__ = action
        return cls

    return decorator
