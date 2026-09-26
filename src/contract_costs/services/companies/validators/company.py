import re

from contract_costs.services.common.resolve_utils import OTHER_IDENTIFIER_PREFIX


class CompanyValidator:

    @staticmethod
    def is_trusted_tax_number(tax_number: str | None) -> bool:
        """
        Numer, któremu ufamy bez weryfikacji przez użytkownika:
        polski NIP albo PESEL z poprawną sumą kontrolną, numer VAT UE z prefiksem kraju
        albo identyfikator nadany ręcznie (OTH-). Placeholdery TMP-/AI-,
        UNKNOWN_* i numery obcięte z liter są niepewne.
        """
        if not tax_number:
            return False
        value = tax_number.strip().upper()
        if value.startswith(OTHER_IDENTIFIER_PREFIX):
            return True
        if value.startswith(("TMP-", "AI-")):
            return False
        if re.fullmatch(r"[A-Z]{2}[0-9A-Z]{2,13}", value) and not value.startswith("PL"):
            return any(ch.isdigit() for ch in value[2:])
        return CompanyValidator.validate_nip(value) or CompanyValidator.validate_pesel(value)

    @staticmethod
    def validate_pesel(pesel: str | None) -> bool:
        if not pesel:
            return False
        pesel = pesel.strip()
        if len(pesel) != 11 or not pesel.isdigit():
            return False
        weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
        checksum = (10 - sum(int(pesel[i]) * weights[i] for i in range(10)) % 10) % 10
        return checksum == int(pesel[10])

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
