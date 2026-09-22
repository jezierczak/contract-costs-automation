
AI_SCHEMA: dict[str, str | list[dict[str,str]]] = {
    "document_type": 'Literal["invoice", "proforma", "receipt", "correction", "contract", "unknown"]',

    "invoice_number": "string | null",
    "invoice_date": "string | null",
    "selling_date": "string | null",
    "payment_method": 'Literal["pre_paid", "bank_transfer", "card", "cash", "blik"] | null',
    "due_date": "string | null",
    "payment_status": 'Literal["paid", "unpaid", "partially_paid" | null]',
    "paid_date": "string | null",

    "buyer_name": "string | null",
    "buyer_tax_number": "string | null",
    "buyer_street": "string | null",
    "buyer_city": "string | null",
    "buyer_state": "string | null",
    "buyer_zip_code": "string | null",
    "buyer_country": "string | null",
    "buyer_phone_number": "string | null",
    "buyer_email": "string | null",
    "buyer_bank_account": "string | null",

    "seller_name": "string | null",
    "seller_tax_number": "string | null",
    "seller_street": "string | null",
    "seller_city": "string | null",
    "seller_state": "string | null",
    "seller_zip_code": "string | null",
    "seller_country": "string | null",
    "seller_phone_number": "string | null",
    "seller_email": "string | null",
    "seller_bank_account": "string | null",

    "invoice_items": [
        {   "item_name": "string | null",
            "description": "string | null",
            "quantity": "number | null",
            "unit": "string | null",
            "unit_price": "number | null",
            "line_total": "number | null",
            "amount_type": 'Literal["net", "gross"]',
            "vat_rate": "string | null"
        }
    ]
}




AI_PROMPT: str = """
Extract invoice data from the given text and return ONLY raw JSON
matching EXACTLY this schema:

{SCHEMA}

Rules:
- Return ONLY JSON, no explanations
- Use null if value is missing
- Dates must be ISO format YYYY-MM-DD
- Amounts must use dot as decimal separator
- Do not invent data
- invoice_item should contain one object per invoice line

invoice_items MUST be an array.
Each invoice_items element MUST have exactly these fields:
- item_name
- quantity
- unit
- unit_price
- line_total
- amount_type
- vat_rate

Rules:
- quantity, unit_price, line_total MUST be numbers (use dot as decimal separator)
- unit should be short (e.g. pcs, kg, m2, h)
- vat_rate must be one of: 0, 5, 8, 23
- Extract unit_price and line_total EXACTLY as printed on the document.
  Do NOT calculate or convert between net and gross yourself.
- Set amount_type to "gross" if the printed amount already includes VAT
  (this is the common case on receipts/paragony, which usually show only
  the final price paid). Set amount_type to "net" if the printed amount
  is the pre-VAT amount (this is the common case on VAT invoices/faktury
  VAT, which usually list net, VAT and gross separately).
- If unsure whether the amount is net or gross, use "net".
- If any value is missing or unclear, use null
- Do NOT invent items
- document_type must be one of:
  invoice, proforma, receipt, correction, contract, unknown
- If unsure, use "unknown"


Text to analyse:
=== OCR START ===
{TEXT}
=== OCR END ===
"""

