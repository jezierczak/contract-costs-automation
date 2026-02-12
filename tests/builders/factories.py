from tests.builders.user_builder import UserBuilder


def create_user(**kwargs):
    return UserBuilder().build()