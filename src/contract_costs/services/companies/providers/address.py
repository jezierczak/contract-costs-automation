import re

from contract_costs.model.company import Company
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.services.companies.providers.candidate_provider import CompanyCandidateProvider
from contract_costs.services.invoices.dto.parse import CompanyInput


STOPWORDS = {
    "UL", "UL.", "ALEJA", "AL", "AL.", "PLAC", "PL", "OS", "OS."
}


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.upper().strip())


def extract_street_number(street: str) -> str | None:
    """
    Wyciąga numer budynku: 12, 12A, 12/3 itd.
    """
    if not street:
        return None

    match = re.search(r"\b\d+[A-Z]?(?:/\d+)?\b", street.upper())
    return match.group(0) if match else None


def extract_street_tokens(street: str) -> list[str]:
    """
    Zwraca tokeny nazwy ulicy (bez numeru i stopwords)
    """
    if not street:
        return []

    street = normalize_text(street)

    # usuń numer
    street = re.sub(r"\b\d+[A-Z]?(?:/\d+)?\b", "", street)

    tokens = re.split(r"[^\wĄĆĘŁŃÓŚŻŹ]+", street)

    return [
        t for t in tokens
        if len(t) >= 3 and t not in STOPWORDS
    ]

class AddressCandidateProvider(CompanyCandidateProvider):
    def __init__(self, repo: CompanyRepository) -> None:
        self._repo = repo

    def find_candidates(self, input_: CompanyInput) -> list[Company]:
        if not input_.street:
            return []

        input_tokens = extract_street_tokens(input_.street)
        input_number = extract_street_number(input_.street)

        if not input_tokens:
            return []

        # tokeny do SQL (z numerem jeśli jest)
        query_tokens = input_tokens + ([input_number] if input_number else [])

        candidates: list[Company] = []

        for company in self._repo.find_by_street_tokens(query_tokens):
            if not company.address or not company.address.street:
                continue

            company_tokens = extract_street_tokens(company.address.street)
            company_number = extract_street_number(company.address.street)

            # 🔹 REGUŁY MATCHOWANIA

            # 1️⃣ numer + przynajmniej 1 token
            if input_number and company_number == input_number:
                if any(t in company_tokens for t in input_tokens):
                    candidates.append(company)
                    continue

            # 2️⃣ bez numeru → minimum 2 wspólne tokeny
            common_tokens = set(input_tokens) & set(company_tokens)
            if len(common_tokens) >= 2:
                candidates.append(company)

        return candidates


