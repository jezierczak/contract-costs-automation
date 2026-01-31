ORGANIZATION_FIELDS = [
    {
        "name": "organization_code",
        "prompt": "Organization code (e.g. REMONTIVO)",
        "type": str,
        "required": True,
    },
    {
        "name": "organization_name",
        "prompt": "Organization full name",
        "type": str,
        "required": True,
    },

    # --- owner ---
    {
        "name": "owner_login",
        "prompt": "Owner login",
        "type": str,
        "required": True,
    },
    {
        "name": "owner_email",
        "prompt": "Owner email (optional)",
        "type": str,
        "required": False,
    },
    {
        "name": "owner_full_name",
        "prompt": "Owner full name (optional)",
        "type": str,
        "required": False,
    },
]
