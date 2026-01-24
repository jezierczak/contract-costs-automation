VALUE_TYPE_FIELDS = [
    {
        "name": "code",
        "prompt": "Type value type code",
        "type": str,
        "required": True,
    },
    {
        "name": "name",
        "prompt": "Type value type name",
        "type": str,
        "required": True,
    },
    {
        "name": "description",
        "prompt": "Type description (optional)",
        "type": str,
        "required": False,
    },
    {
        "name": "direction",
        "prompt": "Direction (COST = expense, REVENUE = income, INTERNAL) [c/r/i]",
        "type": str,
        "required": True,
    },
    {
        "name": "is_active",
        "prompt": "Is value type active? (y/n)",
        "type": bool,
        "required": True,
    },
]
