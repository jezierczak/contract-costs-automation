from abc import ABC, abstractmethod

from contract_costs.unit_of_work import UnitOfWork


class ActionHandler[C, R](ABC):

    @abstractmethod
    def execute(self, *, action: C, uow:UnitOfWork) -> R:
        ...