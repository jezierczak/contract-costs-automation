# action_bus/action_bus.py

import logging
from typing import Any

from contract_costs.action_bus.action import Action
from contract_costs.action_bus.action_handler import ActionHandler

logger = logging.getLogger(__name__)


class ActionBus:

    def __init__(
        self,
        *,
        permission_validator,
        # handlers: dict[type, Any],
    ) -> None:
        self._permission_validator = permission_validator
        # self._handlers = handlers

    def execute(self,
                *,
                action: Action,
                handler: ActionHandler,
                ):

        logger.info("ACTION BUS EXECUTE: %s", type(action).__name__)

        # 🔒 Wymagamy action_type
        action_type = getattr(type(action), "__action_type__", None)
        if action_type is None:
            raise RuntimeError(
                f"{type(action).__name__} missing @action_type decorator"
            )

        # 🔐 Permission check
        self._permission_validator.validate(action)
        logger.info("PERMISSION OK")

        # 🎯 Handler resolution
        # handler = self._handlers.get(type(action))
        # handler = handler
        if not handler:
            raise ValueError(
                f"No handler registered for {type(action).__name__}"
            )

        logger.info("HANDLER RESOLVED: %s", type(handler).__name__)

        if not hasattr(handler, "execute"):
            raise TypeError("Handler must implement execute()")

        return handler.execute(action)
