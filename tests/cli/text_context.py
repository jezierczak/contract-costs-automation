from contract_costs.cli.context import get_services


def test_get_services_memory_backend():
    services = get_services("test")

    from contract_costs.repository.inmemory.company_repository import (
        InMemoryCompanyRepository,
    )

    assert isinstance(
        services.company_repository,
        InMemoryCompanyRepository,
    )

def test_get_services_is_singleton_per_env():
    s1 = get_services("test")
    s2 = get_services("test")

    assert s1 is s2


def test_get_services_different_envs_are_isolated():
    s1 = get_services("test")
    s2 = get_services("prod")

    assert s1 is not s2
