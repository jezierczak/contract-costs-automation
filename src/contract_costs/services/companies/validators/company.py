import re


class CompanyValidator:

    @staticmethod
    def is_trusted_tax_number(tax_number: str | None) -> bool:
        """
        Numer, któremu ufamy bez weryfikacji przez użytkownika:
        polski NIP z poprawną sumą kontrolną albo numer VAT UE z prefiksem kraju.
        Placeholdery (TMP-/AI-) i numery obcięte z liter są niepewne.
        """
        if not tax_number:
            return False
        value = tax_number.strip().upper()
        if value.startswith(("TMP-", "AI-")):
            return False
        if re.fullmatch(r"[A-Z]{2}[0-9A-Z]{2,13}", value) and not value.startswith("PL"):
            return any(ch.isdigit() for ch in value[2:])
        return CompanyValidator.validate_nip(value)

    @staticmethod
    def validate_nip(nip: str | None) -> bool:
        if not nip:
            return False

        # usunięcie PL / PL(spacja) i wszystkiego co nie jest cyfrą
        nip = re.sub(r'^\s*PL\s*', '', nip, flags=re.IGNORECASE)
        nip = re.sub(r'\D', '', nip)

        if len(nip) != 10:
            return False

        weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
        checksum = sum(int(nip[i]) * weights[i] for i in range(9)) % 11

        return checksum == int(nip[9])
