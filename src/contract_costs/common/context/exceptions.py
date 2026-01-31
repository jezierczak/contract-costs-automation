
class ContextError(RuntimeError):
    pass

class NoSession(ContextError):
    """No session found (user never logged in or logged out)."""

class NotLoggedIn(ContextError):
    """Session exists but no user is authenticated."""

class InvalidSession(ContextError):
    """Session exists but is corrupted or invalid."""

class OrganizationNotSelected(ContextError):
    """Session exists but no organization is selected."""
