from uuid import UUID

from contract_costs.model.identity.user import User
from contract_costs.repository.identity.user_repository import UserRepository
from contract_costs.repository.inmemory.identity.in_memory_storage_repository import InMemoryIdentityStorage


class InMemoryUserRepository(UserRepository):

    def __init__(self, storage: InMemoryIdentityStorage | None =None) -> None:
        if not storage:
            self._items: dict[UUID, User] = {}
        else:
            self._items = storage.users

    def add(self, user: User) -> None:
        if user.id in self._items:
            raise ValueError("User already exists")

        # login musi być unikalny
        if any(u.login == user.login for u in self._items.values()):
            raise ValueError("Login already exists")

        self._items[user.id] = user

    def update(self, user: User) -> None:
        if user.id not in self._items:
            raise ValueError("User does not exist")
        self._items[user.id] = user

    def get(self, user_id: UUID) -> User | None:
        return self._items.get(user_id)

    def get_by_login(self, login: str) -> User | None:
        for user in self._items.values():
            if user.login == login:
                return user
        return None

    def list(self, *, active_only: bool = False) -> list[User]:
        if not active_only:
            return list(self._items.values())
        return [u for u in self._items.values() if u.is_active]

    def exists(self, user_id: UUID) -> bool:
        return user_id in self._items
