def requires_role(*roles):
    def wrapper(cls):
        cls.__allowed_roles__ = set(roles)
        return cls
    return wrapper