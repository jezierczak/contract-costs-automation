from passlib.context import CryptContext
from contract_costs.services.identity.auth.password_hasher import PasswordHasher

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class PasslibPasswordHasher(PasswordHasher):
    def verify(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)
    @staticmethod
    def hash(plain: str) -> str:
        return pwd_context.hash(plain)
