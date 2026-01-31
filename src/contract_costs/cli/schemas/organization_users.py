from contract_costs.model.identity.organization_role import OrganizationRole

ORG_USER_FIELDS = [
    {
        "name": "login",
        "prompt": "User login",
        "type": str,
        "required": True,
    },
    {
        "name": "role",
        "prompt": "Role",
        "type": OrganizationRole,
        "choices": {
            "1": OrganizationRole.ADMIN,
            "2": OrganizationRole.USER,
        },
        "required": True,
    },
]
