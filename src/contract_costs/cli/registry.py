from typing import Callable

class CommandRegistry:
    def __init__(self):
        self._groups: dict[str, list] = {}
        self._simple: dict[str, Callable] = {}

    def register_group(self, name: str, builder):
        self._groups.setdefault(name, []).append(builder)

    def register_simple(self, name: str, handler):
        self._simple[name] = handler

    def groups(self):
        return self._groups.items()

    def simples(self):
        return self._simple.items()

REGISTRY = CommandRegistry()
