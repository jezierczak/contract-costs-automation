from enum import Enum


class OrganizationRole(Enum):
    ADMIN = "admin"      # pełne prawa, user management
    OWNER = "owner"      # struktury, kontrakty, konfiguracja
    USER = "user"        # wprowadzanie danych, faktury