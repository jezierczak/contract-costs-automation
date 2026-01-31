class InMemoryIdentityStorage:
    def __init__(self):
        self.organizations = {}
        self.users = {}
        self.organization_users = {}