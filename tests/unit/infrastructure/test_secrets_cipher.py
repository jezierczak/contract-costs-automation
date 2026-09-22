import pytest

from contract_costs.infrastructure.secrets_cipher import decrypt_secret, encrypt_secret


def test_encrypt_then_decrypt_roundtrips(monkeypatch):
    monkeypatch.setenv("KSEF_SECRETS_KEY", "8VgU3JhX2wq5ZC7nP0aF1bK9dS4tR6yM8oL2eI0uQzA=")

    ciphertext = encrypt_secret("super-secret-password")

    assert ciphertext != "super-secret-password"
    assert decrypt_secret(ciphertext) == "super-secret-password"


def test_encrypt_raises_when_key_missing(monkeypatch):
    monkeypatch.delenv("KSEF_SECRETS_KEY", raising=False)

    with pytest.raises(RuntimeError, match="KSEF_SECRETS_KEY"):
        encrypt_secret("anything")


def test_decrypt_raises_on_wrong_key(monkeypatch):
    monkeypatch.setenv("KSEF_SECRETS_KEY", "Heggxv__2jUy7ocBV8xsK5jaAJIyidvCPpAvgWWTPFk=")
    ciphertext = encrypt_secret("secret")

    monkeypatch.setenv("KSEF_SECRETS_KEY", "MBmRU8JpQ58QuoGnHwrBr-xs4nx3yk2fAy4pmjIzawg=")

    with pytest.raises(RuntimeError, match="Failed to decrypt"):
        decrypt_secret(ciphertext)
