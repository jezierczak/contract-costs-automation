

class IdentityServiceError(Exception):
    """Base exception for identity services."""

class OrganizationAlreadyExists(IdentityServiceError):
    pass

class UserAlreadyExists(IdentityServiceError):
    pass

class OrganizationNotFound(IdentityServiceError): ...

class UserNotMemberOfOrganization(IdentityServiceError): ...

class UserNotFound(IdentityServiceError):
    pass

class UserAlreadyInOrganization(IdentityServiceError):
    pass

class PermissionDenied(IdentityServiceError):
    pass