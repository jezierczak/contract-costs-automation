from enum import Enum


class InvoiceCommand(str, Enum):
    APPLY = "APPLY"
    # MODIFY = "MODIFY"
    DELETE = "DELETE"