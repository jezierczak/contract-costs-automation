from contract_costs.cli.context import Services
from contract_costs.repository.factory.repository_factory import RepoBackend
from contract_costs.services.contracts.apply.update_contract_structure_service import UpdateContractStructureService
from contract_costs.services.contracts.create_contract_service import CreateContractService
from contract_costs.unit_of_work.inmemory_unit_of_work import InMemoryUnitOfWork


class _DummyContextProvider:
    pass


def test_services_exposes_uow_property():
    services = Services(
        backend=RepoBackend.MEMORY,
        context_provider=_DummyContextProvider(),
    )

    uow = services.uow

    assert isinstance(uow, InMemoryUnitOfWork)


def test_services_uow_property_returns_fresh_instance():
    services = Services(
        backend=RepoBackend.MEMORY,
        context_provider=_DummyContextProvider(),
    )

    first = services.uow
    second = services.uow

    assert first is not second


def test_services_uses_transactional_services_for_uow_bound_flows():
    services = Services(
        backend=RepoBackend.MEMORY,
        context_provider=_DummyContextProvider(),
    )

    assert isinstance(services.create_contract, CreateContractService)

