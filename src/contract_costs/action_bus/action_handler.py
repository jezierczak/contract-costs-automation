from abc import ABC, abstractmethod


class ActionHandler[C, R](ABC):

    @abstractmethod
    def execute(self, command: C) -> R:
        ...