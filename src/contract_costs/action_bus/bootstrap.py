# action_bus/bootstrap.py

from typing import Callable, Any
from contract_costs.action_bus.handler_registry import (
    get_registered_handler_classes,
)


def build_handler_instances(
    handler_factory: Callable[[type], Any],
) -> dict[type, Any]:

    handler_instances: dict[type, Any] = {}

    for command_type, handler_cls in get_registered_handler_classes().items():
        handler_instances[command_type] = handler_factory(handler_cls)

    return handler_instances
