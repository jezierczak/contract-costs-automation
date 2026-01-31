from uuid import UUID
from contract_costs.common.context.context_provider import ContextProvider
from contract_costs.common.context.exceptions import (
    NotLoggedIn,
    OrganizationNotSelected, InvalidSession, NoSession,
)
from contract_costs.cli.session import load_session, save_session


class FileContextProvider(ContextProvider):

    def current_user_id(self) -> UUID:

        session = self._load_session_or_raise()

        user_id = session.get("user_id")
        if not user_id:
            raise NotLoggedIn("Session has no user. Run: login <user>")
        try:
            return UUID(user_id)
        except ValueError:
            raise InvalidSession("Corrupted session data")

    def current_organization_id(self) -> UUID:
        session = self._load_session_or_raise()
        org_id = session.get("organization_id")
        if not org_id:
            raise OrganizationNotSelected("Session has no organization. Run: use organization <code>")
        try:
            return UUID(org_id)
        except ValueError:
            raise InvalidSession("Corrupted session data")

    def set_current_organization(self, organization_id: UUID) -> None:
        session = self._load_session_or_raise()
        user_id = session.get("user_id")
        if not user_id:
            raise NotLoggedIn("Session has no user. Run: login <user>")
        save_session(user_id=user_id, organization_id =organization_id)

    @staticmethod
    def _load_session_or_raise() -> dict:
        session = load_session()
        if session is None:
            raise NoSession("No active session. Run: login <user>")
        return session