from enum import Enum


class InvoiceCompletionReason(str, Enum):
    OK = "ok"
    NO_INVOICE_DIRECTION = "no_invoice_direction"
    NO_LINES = "no_invoice_lines"
    INCOMPLETE_LINES = "incomplete_lines"
    NO_LINE_DIRECTIONS = "no_line_directions"
    MIXED_LINE_DIRECTIONS = "mixed_line_directions"
    DIRECTION_MISMATCH = "direction_mismatch"
    UNKNOWN_LINE_DIRECTION = "unknown_line_direction"
