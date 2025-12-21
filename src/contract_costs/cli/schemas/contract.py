from contract_costs.model.contract import ContractStatus

CONTRACT_FIELDS = [
    {
        "name": "name",
        "prompt": "Contract name",
        "type": str,
        "required": True,
    },
    {
        "name": "code",
        "prompt": "Define unique contract code name",
        "type": str,
        "required": True,
    },
    {
        "name": "description",
        "prompt": "Description (optional)",
        "type": str,
        "required": False,
    },
    {
        "name": "start_date",
        "prompt": "Start date (YYYY-MM-DD, optional)",
        "type": str,
        "required": False,
    },
    {
        "name": "end_date",
        "prompt": "End date (YYYY-MM-DD, optional)",
        "type": str,
        "required": False,
    },
    {
        "name": "budget",
        "prompt": "Planned budget (optional)",
        "type": float,
        "required": False,
    },
    {
        "name": "status",
        "prompt": "Contract status",
        "type": ContractStatus,
        "choices": {
            "1": ContractStatus.PLANNED,
            "2": ContractStatus.ACTIVE,
        },
        "required": True,
    },
]
