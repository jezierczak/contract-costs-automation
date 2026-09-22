import os

from cryptography.fernet import Fernet, InvalidToken


def _load_key() -> bytes:
    raw = os.getenv("KSEF_SECRETS_KEY")
    if not raw:
        raise RuntimeError(
            "KSEF_SECRETS_KEY is not set - required to encrypt/decrypt stored secrets "
            "(e.g. KSeF certificate password). Generate one with: "
            'python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
        )
    return raw.encode("utf-8")


def encrypt_secret(plaintext: str) -> str:
    return Fernet(_load_key()).encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_secret(ciphertext: str) -> str:
    try:
        return Fernet(_load_key()).decrypt(ciphertext.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise RuntimeError(
            "Failed to decrypt secret - wrong KSEF_SECRETS_KEY or corrupted value"
        ) from exc
