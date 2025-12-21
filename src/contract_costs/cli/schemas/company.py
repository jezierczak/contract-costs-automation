from contract_costs.model.company import CompanyType

COMPANY_FIELDS = [
    # -------- basic --------
    {
        "name": "name",
        "prompt": "Type company name",
        "type": str,
        "required": True,
    },
    {
        "name": "tax_number",
        "prompt": "Type tax number (NIP)",
        "type": str,
        "required": True,
    },
    {
        "name": "description",
        "prompt": "Type description (optional)",
        "type": str,
        "required": False,
    },

    # -------- address --------
    {
        "name": "address_street",
        "prompt": "Street",
        "type": str,
        "required": True,
    },
    {
        "name": "address_city",
        "prompt": "City",
        "type": str,
        "required": True,
    },
    {
        "name": "address_zip_code",
        "prompt": "ZIP code",
        "type": str,
        "required": True,
    },
    {
        "name": "address_country",
        "prompt": "Country",
        "type": str,
        "required": True,
    },

    # -------- bank account (optional) --------
    {
        "name": "bank_account",
        "prompt": "Bank account (leave empty if none)",
        "type": str,
        "required": False,
    },
    {
        "name": "bank_account_IBAN",
        "prompt": "IBAN (required if IBAN given)",
        "type": str,
        "required": False,
    },

    # -------- meta --------
    {
        "name": "role",
        "prompt": "Set company type",
        "type": CompanyType,
        "choices": {
            "1": CompanyType.OWN,
            "2": CompanyType.SUPPLIER,
            "3": CompanyType.CLIENT,
            "4": CompanyType.BUYER,
            "5": CompanyType.SELLER,
        },
        "required": True,
    },
    {
        "name": "is_active",
        "prompt": "Is company active? (y/n)",
        "type": bool,
        "required": True,
    },
]
