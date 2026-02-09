from enum import Enum

class ActionType(Enum):
    UPLOAD_DOCUMENT = "upload_document"
    # PROCESS_DOCUMENT = "process_document"
    DELETE_DOCUMENT = "delete_document"
    GET_DOCUMENT = "get_document"
    LIST_RECORDS = "list_records"
    APPLY_DOCUMENT = "apply_document"
    CREATE_CONTRACT = "create_contract"
    VIEW_CONTRACT = "view_contract"
    CREATE_FINANCIAL_RECORD = "create_financial_record"
    UPDATE_FINANCIAL_RECORD = "update_financial_record"
    VIEW_FINANCIAL_RECORD = "view_financial_record"
    CREATE_COMPANY = "create_company"


def action_type(action: ActionType):
    def decorator(cls):
        cls.__action_type__ = action
        return cls
    return decorator