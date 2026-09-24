# action_bus/action_bus.py

import logging
from typing import Any, Callable

from contract_costs.action_bus.action import Action
from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.action_bus.permission_validator import PermissionValidator
from contract_costs.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class ActionBus:

    def __init__(
        self,
        *,
        permission_validator:PermissionValidator,
        uow_factory: Callable[[], UnitOfWork],
    ) -> None:
        self._permission_validator = permission_validator
        self._uow_factory = uow_factory

    def execute(
        self,
        *,
        action: Action,
        handler: ActionHandler,
    ):
        logger.debug("ACTION BUS EXECUTE: %s", type(action).__name__)

        action_type = getattr(type(action), "__action_type__", None)
        if action_type is None:
            raise RuntimeError(
                f"{type(action).__name__} missing @action_type decorator"
            )

        self._permission_validator.validate(action)
        logger.debug("PERMISSION OK")

        if not handler:
            raise ValueError(
                f"No handler registered for {type(action).__name__}"
            )

        logger.debug("HANDLER RESOLVED: %s", type(handler).__name__)

        if not hasattr(handler, "execute"):
            raise TypeError("Handler must expose execute()")

        # 🔥 TU JEST TRANSAKCJA
        with self._uow_factory() as uow:
            try:
                result = handler.execute(action=action, uow=uow)

                logger.debug(
                    "ACTION SUCCESS: %s",
                    type(action).__name__
                )

                return result
            except Exception:
                logger.exception("ACTION FAILED: %s", type(action).__name__)
                raise
