from uuid import UUID

from contract_costs.model.company import CompanyType
from contract_costs.services.companies.apply.command import (
    CompanyActionCommand,
    CompanyActionType,
)


class CompanyExcelActionMapper:
    @staticmethod
    def map(row: dict) -> CompanyActionCommand:
        action = CompanyActionType((row.get("ACTION") or "none").lower())

        company_id = (
            UUID(row["COMPANY_ID"])
            if row.get("COMPANY_ID")
            else None
        )

        return CompanyActionCommand(
            action=action,
            company_id=company_id,
            tax_number=row["Tax Number"],
            name=row["Name"],
            role=CompanyType(row["Role"]),
            description=row.get("Description"),

            address_street=row.get("Street"),
            address_city=row.get("City"),
            address_zip_code=row.get("Zip Code"),
            address_country=row.get("Country"),

            phone_number=row.get("Phone"),
            email=row.get("Email"),

            bank_account_number=row.get("Bank Account"),
            bank_account_country_code=row.get("Bank Country"),

            tags={
                t.strip()
                for t in (row.get("Tags") or "").split(",")
                if t.strip()
            },
        )
