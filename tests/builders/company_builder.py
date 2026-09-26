import uuid

from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.company import Company, CompanyType, Address, Contact, BankAccount, CompanyVerificationStatus


class CompanyBuilder:
    def __init__(self):
        now = utc_now()

        self._id = new_uuid()
        self._organization_id = new_uuid()
        self._created_at = now
        self._created_by_user_id = None
        self._updated_at = None
        self._updated_by_user_id = None

        self._name = "Test Company"
        self._description = None
        self._tax_number = "1234567890"
        self._verification_status = CompanyVerificationStatus.VERIFIED
        self._address = None
        self._contact = None
        self._bank_account = None
        self._role = CompanyType.SUPPLIER
        self._is_active = True
        self._tags = set()

    # ---------- build ----------

    def build(self) -> Company:
        return Company(
            id=self._id,
            organization_id=self._organization_id,
            created_at=self._created_at,
            created_by_user_id=self._created_by_user_id,
            updated_at=self._updated_at,
            updated_by_user_id=self._updated_by_user_id,
            name=self._name,
            description=self._description,
            tax_number=self._tax_number,
            address=self._address,
            contact=self._contact,
            bank_account=self._bank_account,
            role=self._role,
            is_active=self._is_active,
            tags=self._tags,
            verification_status=self._verification_status,
        )

    # ---------- base ----------

    def is_active(self, is_active: bool) -> "CompanyBuilder":
        self._is_active = is_active
        return self

    def with_id(self, id_: uuid.UUID) -> "CompanyBuilder":
        self._id = id_
        return self

    def with_organization_id(self, org_id: uuid.UUID) -> "CompanyBuilder":
        self._organization_id = org_id
        return self

    def with_verification_status(self, status: CompanyVerificationStatus) -> "CompanyBuilder":
        self._verification_status = status
        return self

    def with_tax_number(self, tax_number: str) -> "CompanyBuilder":
        self._tax_number = tax_number
        return self

    def with_name(self, name: str) -> "CompanyBuilder":
        self._name = name
        return self

    def with_description(self, description: str | None) -> "CompanyBuilder":
        self._description = description
        return self

    def with_role(self, role: CompanyType) -> "CompanyBuilder":
        self._role = role
        return self

    def with_is_active(self, is_active: bool) -> "CompanyBuilder":
        self._is_active = is_active
        return self

    def with_tags(self, tags: set[str]) -> "CompanyBuilder":
        self._tags = tags
        return self

    # ---------- contact ----------

    def with_email(self, email: str) -> "CompanyBuilder":
        self._contact = Contact(
            phone_number=self._contact.phone_number if self._contact else None,
            email=email,
        )
        return self

    def with_phone(self, phone: str) -> "CompanyBuilder":
        self._contact = Contact(
            phone_number=phone,
            email=self._contact.email if self._contact else None,
        )
        return self

    # ---------- address ----------

    def with_street(self, street: str) -> "CompanyBuilder":
        self._address = Address(
            street=street,
            city=None,
            zip_code=None,
            country=None,
        )
        return self

    def with_address(
        self,
        *,
        street: str | None = None,
        city: str | None = None,
        zip_code: str | None = None,
        country: str | None = None,
    ) -> "CompanyBuilder":
        self._address = Address(
            street=street,
            city=city,
            zip_code=zip_code,
            country=country,
        )
        return self

    # ---------- bank ----------

    def with_bank_account(
        self,
        account_number: str,
        country_code: str | None = None,
    ) -> "CompanyBuilder":
        self._bank_account = BankAccount(
            account_number=account_number,
            country_code=country_code,
        )
        return self
