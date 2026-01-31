from contract_costs.common.context.context_provider import ContextProvider


class FakeContextProvider(ContextProvider):
    def __init__(self, user_id, org_id):
        self._user_id = user_id
        self._org_id = org_id

    def current_user_id(self):
        return self._user_id

    def current_organization_id(self):
        return self._org_id
