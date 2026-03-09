from typing import Protocol


class PasswordHasher(Protocol):
    def verify(self, plain: str, hashed: str) -> bool: ...