
AI_SCHEMA: dict[str, str | list[dict[str,str]]] = {
    "invoice_number": "string | null",
    "invoice_date": "string | null",
    "selling_date": "string | null",
    "payment_method": "string | null",
    "due_date": "string | null",
    "payment_status": 'Literal["PAID", "UNPAID"] | null',

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
            "net_unit_price": "number | null",
            "net_total": "number | null",
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
- net_unit_price
- net_total
- vat_rate

Rules:
- quantity, net_unit_price, net_total MUST be numbers (use dot as decimal separator)
- unit should be short (e.g. pcs, kg, m2, h)
- vat_rate must be one of: 0, 5, 8, 23
- If any value is missing or unclear, use null
- Do NOT invent items


Text to analyse:
=== OCR START ===
{TEXT}
=== OCR END ===
"""

