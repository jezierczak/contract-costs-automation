COST_TYPE_FIELDS = [
    {
        "name": "code",
        "prompt": "Type cost type code",
        "type": str,
        "required": True,
    },
    {
        "name": "name",
        "prompt": "Type cost type name",
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
        "name": "is_active",
        "prompt": "Is cost type active? (y/n)",
        "type": bool,
        "required": True,
    },
]
