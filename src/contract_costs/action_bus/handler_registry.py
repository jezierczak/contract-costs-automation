# action_bus/handler_registry.py

from typing import Type

_HANDLER_CLASS_REGISTRY: dict[type, type] = {}


def handles(command_type: Type):
    def decorator(handler_cls: Type):
        if command_type in _HANDLER_CLASS_REGISTRY:
            raise RuntimeError(
                f"Handler already registered for {command_type.__name__}"
            )

        _HANDLER_CLASS_REGISTRY[command_type] = handler_cls
        return handler_cls

    return decorator


def get_registered_handler_classes() -> dict[type, type]:
    return dict(_HANDLER_CLASS_REGISTRY)
