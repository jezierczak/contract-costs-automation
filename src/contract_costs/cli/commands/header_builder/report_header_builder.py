from datetime import datetime
from typing import Any
from enum import Enum


class ReportHeaderBuilder:

    @staticmethod
    def _fmt_value(value: Any) -> str:
        if value is None:
            return "ALL"

        if isinstance(value, list):
            return ", ".join(str(v) for v in value)

        if isinstance(value, Enum):
            return value.name

        return str(value)

    @classmethod
    def build(
        cls,
        *,
        mappings: list[tuple[str, Any]],
    ) -> dict[str, list[str]]:
        header: dict[str, list[str]] = {}

        for label, value in mappings:
            if value is None:
                continue
            header[label] = [cls._fmt_value(value)]

        header["Report created"] = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]

        return header
