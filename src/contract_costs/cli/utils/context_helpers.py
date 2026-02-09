from uuid import UUID

from contract_costs.common.context.context_provider import ContextProvider
from contract_costs.common.context.exceptions import ContextError


def require_user_id(ctx:ContextProvider) -> UUID:
    try:
        return ctx.current_user_id()
    except ContextError as e:
        print(f"❌ {e}")
        raise

def require_organization_id(ctx:ContextProvider) -> UUID:
    try:
        return ctx.current_organization_id()
    except ContextError as e:
        print(f"❌ {e}")
        raise