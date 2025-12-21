import re


class CompanyValidator:

    @staticmethod
    def validate_nip(nip: str) -> bool:
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
